"""Cross-game inventory BRIDGE — the fishing → mining market exchange seam (slice 1).

Slice 1 of the shared cross-game inventory, built to the merged design doc
(``docs/design-shared-cross-game-inventory.md``, PR #179) **Option B**: a thin,
config-gated, fully reversible *bridge* between the two games' existing per-game
inventories, rather than a unified hold (Option A) or a pure price lookup with no
transfer (Option C). Delete this one file and the two games are exactly as they
are today; nothing persisted changes shape.

What this seam does — and, deliberately, does NOT do (slice 1 boundary):

* It **values** a caught fish at the mining market using the canonical **V043**
  sell curve — the SAME curve PR #174 wired into the mining market as a fish's
  price (``games/mining/core/items.py::_fish_value`` lazily imports
  ``games.fishing.core.economy.sell_value``). This module reuses that real curve
  directly via :func:`fish_market_value`; it never re-derives or hard-codes a
  price.
* It **exchanges** fish for coins one-directionally (fishing → mining): remove N
  landed fish from a :class:`~services.fishing_workflow.FishingState`'s haul and
  credit the equivalent coins onto a
  :class:`~services.mining_workflow.MiningState`, 1:1 at the shared V043 price
  (:func:`exchange_fish_for_coins`).
* It is **nothing wired into a live CLI / command path** — additive seam only.
  A later slice threads this onto a "walk your catch to the market" verb and
  routes both legs through the ``services/audit.py`` sink.

The 6 ``⚠️ OWNER PRODUCT CALL`` forks the design doc flagged are resolved here to
the most conservative, reversible defaults (coordinator-decided, owner continue
directive 2026-07-20):

1. **Fish sellable at the mining market at all?** YES in principle, but the whole
   bridge path is **CONFIG-GATED OFF BY DEFAULT** (:func:`bridge_enabled` reads
   ``GAMES_INVENTORY_BRIDGE_ENABLED`` from the env; unset/false ⇒ off) — no
   existing gameplay changes until a host explicitly enables it. Reversible by
   flipping the flag or deleting this file.
2. **Unified vs bridged hold?** BRIDGED (Option B): two separate per-game
   inventories, this service pipes between them. No migration of mining's dict
   store, no shared id scheme.
3. **One-directional or bidirectional?** ONE-DIRECTIONAL (fishing → mining only).
   No ore/gear flows into fishing.
4. **V043 as the cross-game price?** USE the V043 canonical valuation (#174's
   default) as the fish's coin value at the mining market.
5. **Exchange rate / parity?** 1:1 at the shared V043 price. No currency/XP
   conversion.
6. **Does a fish occupy the mining capacity cap?** N/A BY DESIGN — the bridge
   SELLS fish for coins (fish → coins); it never deposits fish objects into the
   mining pack, so no fish occupies the mining capacity cap.

Stdlib-only apart from ``games.fishing.*`` / ``services.*`` types; pure integer
math, no IO beyond a single env read for the flag. The exchange is
**all-or-nothing**: it validates fully BEFORE mutating either side, so it can
never leave fish removed without coins credited (and never credits coins without
removing fish).
"""

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from uuid import uuid4

from games.fishing.core import economy
from services.audit import AuditRecord, Sink
from services.fishing_workflow import FishingState
from services.mining_workflow import MiningState

#: The env var that gates the entire bridge path. DEFAULT OFF: unset (or any
#: value not in :data:`_TRUTHY`) leaves the bridge disabled, so no existing
#: gameplay changes until a host explicitly opts in. Matches the codebase's
#: stdlib-only, env-read config idiom (no config module / no ``.env``).
BRIDGE_ENABLED_ENV = "GAMES_INVENTORY_BRIDGE_ENABLED"

#: The env-string values read as "on" (case-insensitive). Everything else —
#: including unset — is OFF, so the safe/reversible default needs no config.
_TRUTHY = frozenset({"1", "true", "yes", "on"})

#: Structural mutation-type token for BOTH audited legs of a bridge exchange
#: (slice 2). It sits in a game-neutral ``inventory:*`` verb namespace — a
#: sibling of the per-game ``fishing:sell`` / ``mining:sell`` structural verbs —
#: because a bridge sale is exactly one cross-game action whose two audit rows
#: (a fishing-haul debit + a mining-coin credit) are distinguished by their
#: ``subsystem`` / ``target``, not by inventing two separate verbs. The verb
#: carries no balance meaning; the AMOUNT moved is the V043 constant reused via
#: :func:`fish_market_value`.
MUTATION_EXCHANGE = "inventory:exchange"

#: ``subsystem`` tokens for the two legs — honest about which game's state each
#: row changed: the fish leave the FISHING haul, the coins land on the MINING
#: side. Mirrors the seams' own ``subsystem`` field (``"fishing"`` / ``"mining"``).
SUBSYSTEM_FISHING = "fishing"
SUBSYSTEM_MINING = "mining"

#: The seam's actor-type token for a human player (the ``actor_type`` field of
#: :class:`~services.audit.AuditRecord`) — same default the fishing/mining seams use.
ACTOR_PLAYER = "player"


def bridge_enabled() -> bool:
    """True iff the bridge is explicitly enabled via ``GAMES_INVENTORY_BRIDGE_ENABLED``.

    DEFAULT OFF (owner decision 1, conservative/reversible): unset or any value
    outside :data:`_TRUTHY` ⇒ ``False``. Read live from the environment on each
    call so a host can flip it without a process restart in tests.
    """
    return os.environ.get(BRIDGE_ENABLED_ENV, "").strip().lower() in _TRUTHY


@dataclass(frozen=True)
class BridgeResult:
    """Outcome of an :func:`exchange_fish_for_coins` op — a frozen return contract.

    ``ok`` is ``True`` only when the exchange committed (fish debited from the
    fishing haul, coins credited on the mining side). Every no-op — the bridge
    disabled, an unsellable/unknown species, a non-positive quantity, or too few
    fish held — returns ``ok=False`` with a plain-language ``message`` and changes
    NOTHING on either side. ``gated`` distinguishes the disabled-flag no-op (the
    reversible default) from the honest validation no-ops.
    """

    ok: bool
    message: str
    species: str | None = None
    quantity: int = 0
    coins_delta: int = 0
    new_mining_balance: int | None = None
    gated: bool = False
    #: The audit rows emitted for a COMMITTED audited exchange
    #: (:func:`exchange_fish_for_coins_audited`) — the fishing-haul debit leg
    #: then the mining-coin credit leg, in commit order. Empty for the pure
    #: :func:`exchange_fish_for_coins` (which audits nothing) and for EVERY
    #: no-op (gated or failed) — no partial audit is ever left behind.
    records: tuple[AuditRecord, ...] = ()


def fish_market_value(species_id: str, qty: int = 1) -> int:
    """The coins *qty* fish of *species_id* fetch at the mining market (PURE).

    Computed from the canonical **V043** fishing sell curve
    (:func:`games.fishing.core.economy.sell_value` — minnow 8 · bass 13 · pike 27
    · legend_carp 80), the exact single source of truth PR #174 made the fish's
    mining-market price (``items._fish_value`` lazily imports the same function).
    This never re-derives or hard-codes a price; it reuses #174's canonical
    valuation, 1:1 (owner decisions 4 + 5 — V043 at parity).

    Pure integer math: ``sell_value(species_id) * qty``. Raises ``KeyError`` for a
    species absent from the V043 curve (callers guard with
    :func:`economy.is_sellable`) and ``ValueError`` for a non-positive quantity —
    a valuation of "zero or fewer" fish is not a meaningful quote.
    """
    if qty <= 0:
        raise ValueError(f"qty must be positive, got {qty!r}")
    return economy.sell_value(species_id) * qty


def exchange_fish_for_coins(
    fishing_state: FishingState,
    mining_state: MiningState,
    species_id: str,
    qty: int = 1,
    *,
    enabled: bool | None = None,
) -> BridgeResult:
    """Sell *qty* landed fish (fishing haul) for coins at the mining market (V043).

    The Option-B bridge leg: remove *qty* fish of *species_id* from
    ``fishing_state.haul`` and credit the equivalent coins onto
    ``mining_state.coins``, ONE-DIRECTIONALLY (fishing → mining), 1:1 at the
    canonical V043 price (:func:`fish_market_value`). The fish are SOLD for
    coins — no fish object is ever deposited into ``mining_state.inventory``, so
    no fish occupies the mining capacity cap (owner decision 6, N/A by design).

    **Config-gated (owner decision 1).** When the bridge is disabled it is a pure
    no-op: nothing on either side changes and ``BridgeResult(ok=False,
    gated=True)`` is returned. *enabled* defaults to :func:`bridge_enabled` (the
    ``GAMES_INVENTORY_BRIDGE_ENABLED`` env flag, DEFAULT OFF); pass it explicitly
    to drive the gate deterministically in a test/host without touching the env.

    **All-or-nothing / non-destructive (design floor).** Every precondition —
    the flag, a sellable species, a positive quantity, and enough fish held — is
    checked BEFORE either side is mutated, so the exchange can never leave fish
    removed without coins credited (or coins credited without fish removed). Each
    failure returns ``ok=False`` and changes NOTHING.
    """
    if enabled is None:
        enabled = bridge_enabled()
    if not enabled:
        # The reversible default: the whole path is off, so this is a pure no-op.
        return BridgeResult(
            ok=False,
            message="Cross-game inventory bridge is disabled.",
            species=species_id,
            gated=True,
        )

    if not economy.is_sellable(species_id):
        return BridgeResult(
            ok=False,
            message=f"{species_id} cannot be sold at the mining market.",
            species=species_id,
        )
    if qty <= 0:
        return BridgeResult(ok=False, message="Quantity must be positive.", species=species_id)

    held = fishing_state.haul.get(species_id, 0)
    if held < qty:
        return BridgeResult(
            ok=False,
            message=f"You only have {held}× {species_id}.",
            species=species_id,
        )

    # Everything validated — compute the coin value BEFORE any mutation, then
    # apply both legs together so no partial state is possible (all-or-nothing).
    total = fish_market_value(species_id, qty)
    fishing_state.haul[species_id] = held - qty  # the fish is CONSUMED (fishing → mining)
    mining_state.coins += total

    return BridgeResult(
        ok=True,
        message=f"Sold {qty}× {species_id} at the mining market for {total} coins.",
        species=species_id,
        quantity=qty,
        coins_delta=total,
        new_mining_balance=mining_state.coins,
    )


# ---------------------------------------------------------------------------
# The AUDITED exchange (slice 2) — routes BOTH legs through the shared sink
# ---------------------------------------------------------------------------
def _resolve_now(now: datetime | None) -> datetime:
    """The op's timestamp — the injected *now* or ``datetime.now(timezone.utc)``."""
    return now if now is not None else datetime.now(timezone.utc)


def _resolve_id(factory: Callable[[], str] | None) -> str:
    """A fresh mutation id — from the injected *factory* or ``uuid4().hex``."""
    return factory() if factory is not None else uuid4().hex


def _exchange_record(
    *,
    subsystem: str,
    target: str,
    prev_value: str,
    new_value: str,
    now: datetime,
    mutation_id: str,
    guild_id: int | None,
    actor_id: int | None,
    actor_type: str,
) -> AuditRecord:
    """Build one leg's :class:`~services.audit.AuditRecord` (the 11-field schema).

    Same structural shape the fishing/mining seams construct for their own
    ``sell`` legs (verb + target + prev/new + ids), so a bridge sale sits in the
    ONE ledger those seams already write to. Only structural fields are set here;
    the moved AMOUNT lives in ``prev_value``/``new_value`` (the balances), quoted
    from the V043 exchange, never re-derived.
    """
    return AuditRecord(
        mutation_id=mutation_id,
        subsystem=subsystem,
        mutation_type=MUTATION_EXCHANGE,
        target=target,
        scope="global",
        guild_id=guild_id,
        prev_value=prev_value,
        new_value=new_value,
        actor_id=actor_id,
        actor_type=actor_type,
        occurred_at=now,
    )


def exchange_fish_for_coins_audited(
    fishing_state: FishingState,
    mining_state: MiningState,
    species_id: str,
    qty: int = 1,
    *,
    sink: Sink,
    enabled: bool | None = None,
    guild_id: int | None = None,
    actor_id: int | None = None,
    actor_type: str = ACTOR_PLAYER,
    now: datetime | None = None,
    mutation_id_factory: Callable[[], str] | None = None,
) -> BridgeResult:
    """The AUDITED bridge sale (slice 2): exchange fish → coins AND audit both legs.

    Wraps the pure, all-or-nothing :func:`exchange_fish_for_coins` (which owns the
    gate, the validation, and the atomic mutation) and, ON A COMMITTED exchange,
    emits the money flow to the SAME injected :class:`~services.audit.Sink` the
    sibling ``fishing_workflow.sell`` / ``mining_workflow.sell`` legs write to —
    so the cross-game sale is reconstructable from one ledger. TWO rows are
    recorded, in commit order:

    1. the **fishing-haul debit** (``subsystem="fishing"``, ``target="haul:<species>"``,
       prev→new haul count), and
    2. the **mining-coin credit** (``subsystem="mining"``, ``target="coins"``,
       prev→new mining balance),

    both with ``mutation_type`` :data:`MUTATION_EXCHANGE`. The prev-state for both
    legs is captured BEFORE the mutation, so the rows carry honest values.

    **Config-gated + non-destructive (no partial audit).** Because the underlying
    exchange validates the flag, the species, the quantity, and the held count
    BEFORE touching either side, a gated OR failed call mutates NOTHING — and this
    wrapper records NOTHING in that case (``result.ok is False`` ⇒ no ``sink``
    call, ``records=()``), mirroring the seams' "a no-op records nothing" rule.
    An exchange can therefore never leave one leg audited without the other, nor
    fish removed without coins credited. *enabled* / *now* / *mutation_id_factory*
    are injectable so a host/test can drive the gate and reproduce the rows
    deterministically.
    """
    if enabled is None:
        enabled = bridge_enabled()

    # Capture the pre-state for BOTH legs BEFORE any mutation, so a committed
    # exchange's audit rows carry honest prev/new values (and a gated/failed
    # call — which mutates nothing — emits nothing).
    prev_held = fishing_state.haul.get(species_id, 0)
    prev_coins = mining_state.coins

    result = exchange_fish_for_coins(
        fishing_state, mining_state, species_id, qty, enabled=enabled
    )
    if not result.ok:
        # Gated OR an honest validation no-op: nothing mutated, so NOTHING is
        # audited — no partial audit is ever left behind (all-or-nothing).
        return result

    now_dt = _resolve_now(now)
    new_held = prev_held - result.quantity
    fish_leg = _exchange_record(
        subsystem=SUBSYSTEM_FISHING,
        target=f"haul:{species_id}",
        prev_value=str(prev_held),
        new_value=str(new_held),
        now=now_dt,
        mutation_id=_resolve_id(mutation_id_factory),
        guild_id=guild_id,
        actor_id=actor_id,
        actor_type=actor_type,
    )
    coins_leg = _exchange_record(
        subsystem=SUBSYSTEM_MINING,
        target="coins",
        prev_value=str(prev_coins),
        new_value=str(result.new_mining_balance),
        now=now_dt,
        mutation_id=_resolve_id(mutation_id_factory),
        guild_id=guild_id,
        actor_id=actor_id,
        actor_type=actor_type,
    )
    # The state mutation already committed atomically inside
    # exchange_fish_for_coins; recording BOTH legs is the last commit step.
    sink.record(fish_leg)
    sink.record(coins_leg)
    return replace(result, records=(fish_leg, coins_leg))


__all__ = [
    "BRIDGE_ENABLED_ENV",
    "MUTATION_EXCHANGE",
    "SUBSYSTEM_FISHING",
    "SUBSYSTEM_MINING",
    "ACTOR_PLAYER",
    "BridgeResult",
    "bridge_enabled",
    "fish_market_value",
    "exchange_fish_for_coins",
    "exchange_fish_for_coins_audited",
]
