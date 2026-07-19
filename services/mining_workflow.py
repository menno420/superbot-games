"""Mining WORKFLOW audited seam — rung 2 of the mining ladder.

The audited **write boundary** for mining. Below it sits the shipped PURE CORE
(``games/mining/core/``, 19 stdlib-only modules of stateless decision
functions); above it (rung 3) a HOST adapter will bind this seam onto the
superbot-next plugin contract. This module is the middle rung: every
state-changing mining op is orchestrated here in one place —

    read session state  ->  call PURE CORE to decide  ->  mutate the state  ->
    build an audit record  ->  ``sink.record(...)``  ->  return a frozen Result

Design provenance — ``docs/design/mining-workflow-seam.md`` §5 (the sanctioned,
REVERSIBLE D1/D2 default, flagged for owner/lab ratification in
``control/outbox.md``):

* **D1** — the seam's audit record is the oracle's 11-field structural
  ``audit.action_recorded`` schema (:class:`AuditRecord`), adopted VERBATIM.
* **D2** — the seam audits **every** state-changing action routed through it,
  including item grants (``mine`` / ``harvest``). This is a deliberate,
  reversible DIVERGENCE from the oracle (whose ``mine`` / ``harvest`` write no
  audit row at all); flipping it back is a one-line policy toggle. Failed /
  no-op actions record NOTHING.

Persistence is deferred behind an injected :class:`Sink` port (D3/D4); the seam
calls ``sink.record(...)`` as the last step of its logical commit. Tests bind an
:class:`InMemorySink`; the real DB / bus binding lands at the host-adapter rung.

Balance discipline: reason tokens, prices, costs and loot weights come VERBATIM
from the core (never re-derived here). Only *structural* audit fields — the
mutation id, timestamps, ids, ``scope`` and ``target`` strings — are constructed
(they carry no balance meaning). This module is stdlib-only apart from
``games.mining.core.*`` so CI stays hermetic (no discord / db / network).
"""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from services.audit import AuditRecord, InMemorySink, Sink

from games.mining.core import (
    capacity,
    energy,
    equipment,
    market,
    rewards,
    skills,
    structures,
    workshop,
    world,
)
from games.mining.core.energy import EnergyState

# --- structural mutation-type tokens ---------------------------------------
# The economy legs reuse the core's VERBATIM reason tokens (market.SELL_REASON,
# BUY_REASON, workshop.REPAIR_REASON, VAULT_UPGRADE_REASON,
# market.structure_build_reason). The purely *structural* actions below have no
# money leg and therefore no core reason token, so the seam constructs a stable
# ``mining:<verb>`` token for them — a structural field (no balance meaning), on
# the same ``mining:*`` namespace the core reason tokens already use.
MUTATION_MINE = "mining:mine"
MUTATION_HARVEST = "mining:harvest"
MUTATION_DESCEND = "mining:descend"
MUTATION_ASCEND = "mining:ascend"
MUTATION_ALLOCATE_SKILL = "mining:allocate_skill"

#: The seam's actor-type token for a human player (the ``actor_type`` field of
#: :class:`AuditRecord`; the oracle's capability-resolver actor-type slot).
ACTOR_PLAYER = "player"


# ---------------------------------------------------------------------------
# The audit record (D1) + the sink port (D3/D4) are GAME-NEUTRAL and live in
# ``services/audit.py`` so every game's seam reuses them without coupling; the
# mining seam re-exports them for callers that import off this module.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# The session state the seam mutates
# ---------------------------------------------------------------------------
@dataclass
class MiningState:
    """A full mutable mining session — everything the seam reads and writes.

    Field notes:

    * ``inventory`` — the carried pack: mined ore/wood loot lands here and
      sellable resources are sold from here (the faucet + the trade store).
    * ``materials`` — the refined stockpile that structure builds consume
      (``build_structure`` debits ``BuildCost.materials`` from here). Kept
      distinct from ``inventory`` so each action's data source is unambiguous.
    * ``equipped`` — ``{slot: item_name}`` feeding ``equipment.compute_stats``
      (drives the mine multiplier, the descend gate, and which slots wear).
    * ``durability`` — ``{item_name: remaining_uses}``; the wear plan ticks it.
    * ``structures`` — ``{structure: level}`` (0 / absent = not built).
    * ``skills`` — ``{branch: points}`` skill allocation.
    """

    inventory: dict[str, int] = field(default_factory=dict)
    coins: int = 0
    equipped: dict[str, str] = field(default_factory=dict)
    durability: dict[str, int] = field(default_factory=dict)
    energy: EnergyState = field(default_factory=lambda: EnergyState(energy.MAX_ENERGY, 0))
    depth: int = 0
    materials: dict[str, int] = field(default_factory=dict)
    structures: dict[str, int] = field(default_factory=dict)
    skills: dict[str, int] = field(default_factory=dict)
    vault_level: int = 0

    def stats(self) -> equipment.EffectiveStats:
        """Effective gear stats for the equipped loadout (used by depth-gating)."""
        return equipment.compute_stats(self.equipped)


# ---------------------------------------------------------------------------
# Result dataclasses — one frozen result per action (the seam's return contract)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class MineResult:
    """Outcome of a :func:`mine` op."""

    ok: bool
    message: str
    ore: str | None = None
    amount: int = 0
    broke: tuple[str, ...] = ()
    record: AuditRecord | None = None


@dataclass(frozen=True)
class HarvestResult:
    """Outcome of a :func:`harvest` op."""

    ok: bool
    message: str
    amount: int = 0
    record: AuditRecord | None = None


@dataclass(frozen=True)
class TradeResult:
    """Outcome of a :func:`sell` / :func:`buy` op (a coin leg + an item leg)."""

    ok: bool
    message: str
    item: str | None = None
    quantity: int = 0
    coins_delta: int = 0
    new_balance: int | None = None
    record: AuditRecord | None = None


@dataclass(frozen=True)
class RepairResult:
    """Outcome of a :func:`repair` op."""

    ok: bool
    message: str
    item: str | None = None
    cost: int = 0
    restored_to: int | None = None
    new_balance: int | None = None
    record: AuditRecord | None = None


@dataclass(frozen=True)
class MoveResult:
    """Outcome of a :func:`descend` / :func:`ascend` op."""

    ok: bool
    message: str
    depth: int = 0
    record: AuditRecord | None = None


@dataclass(frozen=True)
class BuildResult:
    """Outcome of a :func:`build_structure` op."""

    ok: bool
    message: str
    structure: str | None = None
    level: int = 0
    coins_spent: int = 0
    materials_spent: dict[str, int] = field(default_factory=dict)
    record: AuditRecord | None = None


@dataclass(frozen=True)
class VaultResult:
    """Outcome of a :func:`vault_upgrade` op."""

    ok: bool
    message: str
    level: int = 0
    capacity: int = 0
    coins_spent: int = 0
    new_balance: int | None = None
    record: AuditRecord | None = None


@dataclass(frozen=True)
class SkillResult:
    """Outcome of an :func:`allocate_skill` op."""

    ok: bool
    message: str
    branch: str | None = None
    points: int = 0
    record: AuditRecord | None = None


# ---------------------------------------------------------------------------
# Injectables — a simple clock + id factory kept deterministic for tests
# ---------------------------------------------------------------------------
def _resolve_now(now: datetime | None) -> datetime:
    """The op's timestamp — the injected *now* or ``datetime.now(timezone.utc)``."""
    return now if now is not None else datetime.now(timezone.utc)


def _resolve_id(factory: Callable[[], str] | None) -> str:
    """A fresh mutation id — from the injected *factory* or ``uuid4().hex``."""
    return factory() if factory is not None else uuid4().hex


def _make_record(
    *,
    mutation_type: str,
    target: str,
    prev_value: str | None,
    new_value: str | None,
    now: datetime,
    mutation_id: str,
    guild_id: int | None,
    actor_id: int | None,
    actor_type: str,
) -> AuditRecord:
    """Build one :class:`AuditRecord` with the seam's fixed structural defaults."""
    return AuditRecord(
        mutation_id=mutation_id,
        subsystem="mining",
        mutation_type=mutation_type,
        target=target,
        scope="global",
        guild_id=guild_id,
        prev_value=prev_value,
        new_value=new_value,
        actor_id=actor_id,
        actor_type=actor_type,
        occurred_at=now,
    )


def _grant(store: dict[str, int], item: str, amount: int) -> int:
    """Add *amount* of *item* to *store*; return the new total."""
    store[item] = store.get(item, 0) + amount
    return store[item]


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------
def mine(
    state: MiningState,
    *,
    sink: Sink,
    guild_id: int | None = None,
    actor_id: int | None = None,
    actor_type: str = ACTOR_PLAYER,
    rng: random.Random | None = None,
    now: datetime | None = None,
    mutation_id_factory: Callable[[], str] | None = None,
    cost: int = energy.DIG_COST,
) -> MineResult:
    """Dig once: spend energy, roll loot, wear the tool/light, grant the ore.

    Wires ``energy.can_dig`` / ``energy.spend`` -> ``rewards.mine_multiplier``
    -> ``rewards.roll_mine_loot`` -> ``workshop.WEAR_PLAN[ACTION_MINE]`` ->
    grant to inventory. Blocked (out of energy) returns ``ok=False`` and records
    nothing.
    """
    now_dt = _resolve_now(now)
    now_unix = int(now_dt.timestamp())

    if not energy.can_dig(state.energy, now_unix, cost=cost):
        return MineResult(ok=False, message="Not enough energy to dig — rest to regen.")

    state.energy = energy.spend(state.energy, now_unix, cost=cost)

    multiplier = rewards.mine_multiplier(state.equipped, state.inventory)
    has_pickaxe = state.inventory.get("pickaxe", 0) > 0
    ore, amount = rewards.roll_mine_loot(
        has_pickaxe=has_pickaxe,
        depth=state.depth,
        multiplier=multiplier,
        rng=rng,
    )

    broke = _apply_wear(state, workshop.ACTION_MINE)

    prev = state.inventory.get(ore, 0)
    new_total = _grant(state.inventory, ore, amount)

    record = _make_record(
        mutation_type=MUTATION_MINE,
        target=f"inventory:{ore}",
        prev_value=str(prev),
        new_value=str(new_total),
        now=now_dt,
        mutation_id=_resolve_id(mutation_id_factory),
        guild_id=guild_id,
        actor_id=actor_id,
        actor_type=actor_type,
    )
    sink.record(record)
    return MineResult(
        ok=True,
        message=f"Mined {amount}× {ore}.",
        ore=ore,
        amount=amount,
        broke=broke,
        record=record,
    )


def harvest(
    state: MiningState,
    *,
    sink: Sink,
    guild_id: int | None = None,
    actor_id: int | None = None,
    actor_type: str = ACTOR_PLAYER,
    rng: random.Random | None = None,
    now: datetime | None = None,
    mutation_id_factory: Callable[[], str] | None = None,
) -> HarvestResult:
    """Chop once: roll a wood amount and grant it.

    Wires ``rewards.roll_harvest_amount`` -> grant wood to inventory. The core
    ``WEAR_PLAN`` has no ``harvest`` entry (chopping wears no equipped mining
    slot), so no durability tick is applied — inventing one would fabricate a
    balance rule, which this seam never does.
    """
    now_dt = _resolve_now(now)
    has_axe = state.inventory.get("axe", 0) > 0
    amount = rewards.roll_harvest_amount(has_axe=has_axe, rng=rng)

    prev = state.inventory.get("wood", 0)
    new_total = _grant(state.inventory, "wood", amount)

    record = _make_record(
        mutation_type=MUTATION_HARVEST,
        target="inventory:wood",
        prev_value=str(prev),
        new_value=str(new_total),
        now=now_dt,
        mutation_id=_resolve_id(mutation_id_factory),
        guild_id=guild_id,
        actor_id=actor_id,
        actor_type=actor_type,
    )
    sink.record(record)
    return HarvestResult(
        ok=True,
        message=f"Harvested {amount}× wood.",
        amount=amount,
        record=record,
    )


def sell(
    state: MiningState,
    name: str,
    qty: int,
    *,
    sink: Sink,
    guild_id: int | None = None,
    actor_id: int | None = None,
    actor_type: str = ACTOR_PLAYER,
    now: datetime | None = None,
    mutation_id_factory: Callable[[], str] | None = None,
) -> TradeResult:
    """Sell *qty* of a resource: credit coins at the core's verbatim sell price.

    Wires ``market.sell_price`` (reason ``market.SELL_REASON``). Not-sellable,
    a non-positive quantity, or too few held all return ``ok=False`` and record
    nothing.
    """
    unit = market.sell_price(name)
    if unit is None:
        return TradeResult(ok=False, message=f"{name} cannot be sold.", item=name)
    if qty <= 0:
        return TradeResult(ok=False, message="Quantity must be positive.", item=name)
    held = state.inventory.get(name, 0)
    if held < qty:
        return TradeResult(
            ok=False,
            message=f"You only have {held}× {name}.",
            item=name,
        )

    total = unit * qty
    prev_coins = state.coins
    state.inventory[name] = held - qty
    state.coins = prev_coins + total

    record = _make_record(
        mutation_type=market.SELL_REASON,
        target="coins",
        prev_value=str(prev_coins),
        new_value=str(state.coins),
        now=_resolve_now(now),
        mutation_id=_resolve_id(mutation_id_factory),
        guild_id=guild_id,
        actor_id=actor_id,
        actor_type=actor_type,
    )
    sink.record(record)
    return TradeResult(
        ok=True,
        message=f"Sold {qty}× {name} for {total} coins.",
        item=name,
        quantity=qty,
        coins_delta=total,
        new_balance=state.coins,
        record=record,
    )


def buy(
    state: MiningState,
    name: str,
    *,
    sink: Sink,
    guild_id: int | None = None,
    actor_id: int | None = None,
    actor_type: str = ACTOR_PLAYER,
    now: datetime | None = None,
    mutation_id_factory: Callable[[], str] | None = None,
) -> TradeResult:
    """Buy one shop item: debit coins at the core's verbatim buy price, grant it.

    Wires ``market.buy_price`` (reason ``market.BUY_REASON``). Not-for-sale or
    unaffordable returns ``ok=False`` and records nothing.
    """
    price = market.buy_price(name)
    if price is None:
        return TradeResult(ok=False, message=f"{name} is not for sale.", item=name)
    if state.coins < price:
        return TradeResult(
            ok=False,
            message=f"Not enough coins — {name} costs {price}.",
            item=name,
        )

    prev_coins = state.coins
    state.coins = prev_coins - price
    _grant(state.inventory, name, 1)

    record = _make_record(
        mutation_type=market.BUY_REASON,
        target="coins",
        prev_value=str(prev_coins),
        new_value=str(state.coins),
        now=_resolve_now(now),
        mutation_id=_resolve_id(mutation_id_factory),
        guild_id=guild_id,
        actor_id=actor_id,
        actor_type=actor_type,
    )
    sink.record(record)
    return TradeResult(
        ok=True,
        message=f"Bought 1× {name} for {price} coins.",
        item=name,
        quantity=1,
        coins_delta=-price,
        new_balance=state.coins,
        record=record,
    )


def repair(
    state: MiningState,
    name: str,
    *,
    sink: Sink,
    guild_id: int | None = None,
    actor_id: int | None = None,
    actor_type: str = ACTOR_PLAYER,
    now: datetime | None = None,
    mutation_id_factory: Callable[[], str] | None = None,
) -> RepairResult:
    """Fully repair a worn item: debit the core repair cost, restore durability.

    Wires ``workshop.repair_cost`` (reason ``workshop.REPAIR_REASON``). An item
    not tracked / not worn / not repairable, or an unaffordable cost, returns
    ``ok=False`` and records nothing.
    """
    if name not in state.durability:
        return RepairResult(ok=False, message=f"You have no {name} to repair.", item=name)

    remaining = state.durability[name]
    cost = workshop.repair_cost(name, remaining)
    if cost is None:
        return RepairResult(
            ok=False,
            message=f"{name} needs no repair.",
            item=name,
        )
    if state.coins < cost:
        return RepairResult(
            ok=False,
            message=f"Not enough coins — repairing {name} costs {cost}.",
            item=name,
        )

    maximum = equipment.max_durability(name)
    prev_coins = state.coins
    state.coins = prev_coins - cost
    state.durability[name] = maximum

    record = _make_record(
        mutation_type=workshop.REPAIR_REASON,
        target="coins",
        prev_value=str(prev_coins),
        new_value=str(state.coins),
        now=_resolve_now(now),
        mutation_id=_resolve_id(mutation_id_factory),
        guild_id=guild_id,
        actor_id=actor_id,
        actor_type=actor_type,
    )
    sink.record(record)
    return RepairResult(
        ok=True,
        message=f"Repaired {name} for {cost} coins.",
        item=name,
        cost=cost,
        restored_to=maximum,
        new_balance=state.coins,
        record=record,
    )


def descend(
    state: MiningState,
    *,
    sink: Sink,
    guild_id: int | None = None,
    actor_id: int | None = None,
    actor_type: str = ACTOR_PLAYER,
    now: datetime | None = None,
    mutation_id_factory: Callable[[], str] | None = None,
) -> MoveResult:
    """Go one band deeper if the equipped light gates it.

    Wires ``world.can_descend`` / ``world.descend`` against the equipped
    ``depth_access`` stat. A blocked descent (no light for the next band)
    returns ``ok=False`` (with ``world.descend_hint``) and records nothing.
    """
    stats = state.stats()
    if not world.can_descend(state.depth, stats):
        return MoveResult(
            ok=False,
            message=world.descend_hint(stats),
            depth=state.depth,
        )

    prev = state.depth
    state.depth = world.descend(state.depth, stats)

    record = _make_record(
        mutation_type=MUTATION_DESCEND,
        target="depth",
        prev_value=str(prev),
        new_value=str(state.depth),
        now=_resolve_now(now),
        mutation_id=_resolve_id(mutation_id_factory),
        guild_id=guild_id,
        actor_id=actor_id,
        actor_type=actor_type,
    )
    sink.record(record)
    return MoveResult(
        ok=True,
        message=f"Descended to {world.describe_position(state.depth)}.",
        depth=state.depth,
        record=record,
    )


def ascend(
    state: MiningState,
    *,
    sink: Sink,
    guild_id: int | None = None,
    actor_id: int | None = None,
    actor_type: str = ACTOR_PLAYER,
    now: datetime | None = None,
    mutation_id_factory: Callable[[], str] | None = None,
) -> MoveResult:
    """Climb one band toward the surface.

    Wires ``world.can_ascend`` / ``world.ascend``. Already at the surface
    returns ``ok=False`` and records nothing.
    """
    if not world.can_ascend(state.depth):
        return MoveResult(
            ok=False,
            message="You are already at the Surface.",
            depth=state.depth,
        )

    prev = state.depth
    state.depth = world.ascend(state.depth)

    record = _make_record(
        mutation_type=MUTATION_ASCEND,
        target="depth",
        prev_value=str(prev),
        new_value=str(state.depth),
        now=_resolve_now(now),
        mutation_id=_resolve_id(mutation_id_factory),
        guild_id=guild_id,
        actor_id=actor_id,
        actor_type=actor_type,
    )
    sink.record(record)
    return MoveResult(
        ok=True,
        message=f"Ascended to {world.describe_position(state.depth)}.",
        depth=state.depth,
        record=record,
    )


def build_structure(
    state: MiningState,
    structure: str,
    level: int,
    *,
    sink: Sink,
    guild_id: int | None = None,
    actor_id: int | None = None,
    actor_type: str = ACTOR_PLAYER,
    now: datetime | None = None,
    mutation_id_factory: Callable[[], str] | None = None,
) -> BuildResult:
    """Build/upgrade *structure* from *level* to *level*+1: debit coins + materials.

    Wires ``structures.build_cost`` (reason via ``market.structure_build_reason``).
    An unknown structure, a maxed / invalid level, or insufficient coins or
    materials all return ``ok=False`` and record nothing.
    """
    if not structures.is_structure(structure):
        return BuildResult(ok=False, message=f"{structure} is not buildable.")

    key = structure.strip().lower()
    # The *level* parameter is advisory only — a caller-typed value must never
    # decide the cost, the write, or the audit prev_value (that lets `build
    # forge 0` downgrade a maxed forge for the cheap level-0 cost and `build
    # forge 1` skip a tier for free). Derive the authoritative current level
    # from state, exactly as ``vault_upgrade`` reads ``state.vault_level``.
    level = state.structures.get(key, 0)
    cost = structures.build_cost(key, level)
    if cost is None:
        return BuildResult(
            ok=False,
            message=f"{structures.display_name(key)} cannot be upgraded from level {level}.",
            structure=key,
            level=level,
        )
    if state.coins < cost.coins:
        return BuildResult(
            ok=False,
            message=f"Not enough coins — {structures.display_name(key)} costs {cost.coins}.",
            structure=key,
            level=level,
        )
    short = {
        mat: qty for mat, qty in cost.materials.items() if state.materials.get(mat, 0) < qty
    }
    if short:
        need = workshop.describe_materials(short)
        return BuildResult(
            ok=False,
            message=f"Not enough materials — still need {need}.",
            structure=key,
            level=level,
        )

    prev_coins = state.coins
    state.coins = prev_coins - cost.coins
    for mat, qty in cost.materials.items():
        state.materials[mat] -= qty
    new_level = level + 1
    state.structures[key] = new_level

    now_dt = _resolve_now(now)
    reason = market.structure_build_reason(key)
    record = _make_record(
        mutation_type=reason,
        target=f"structure:{key}",
        prev_value=str(level),
        new_value=str(new_level),
        now=now_dt,
        mutation_id=_resolve_id(mutation_id_factory),
        guild_id=guild_id,
        actor_id=actor_id,
        actor_type=actor_type,
    )
    sink.record(record)
    # Decision #8 — economy_audit_log completeness: a build is a coin SINK, so in
    # addition to the structure-LEVEL row above, emit a target="coins" ledger row
    # carrying the coin balance before/after — the exact row shape sell / buy /
    # repair use — so a wallet reconstructed purely from the log's coin rows
    # accounts for this sink. The level row stays the primary ``result.record``.
    sink.record(
        _make_record(
            mutation_type=reason,
            target="coins",
            prev_value=str(prev_coins),
            new_value=str(state.coins),
            now=now_dt,
            mutation_id=_resolve_id(mutation_id_factory),
            guild_id=guild_id,
            actor_id=actor_id,
            actor_type=actor_type,
        )
    )
    return BuildResult(
        ok=True,
        message=f"Built {structures.level_name(key, new_level)} for {cost.coins} coins.",
        structure=key,
        level=new_level,
        coins_spent=cost.coins,
        materials_spent=dict(cost.materials),
        record=record,
    )


def vault_upgrade(
    state: MiningState,
    *,
    sink: Sink,
    guild_id: int | None = None,
    actor_id: int | None = None,
    actor_type: str = ACTOR_PLAYER,
    now: datetime | None = None,
    mutation_id_factory: Callable[[], str] | None = None,
) -> VaultResult:
    """Upgrade the vault one level: debit the core cost, raise the cap.

    Wires ``capacity.vault_upgrade_cost`` (reason ``market.VAULT_UPGRADE_REASON``).
    A maxed vault or an unaffordable cost returns ``ok=False`` and records nothing.
    """
    level = state.vault_level
    cost = capacity.vault_upgrade_cost(level)
    if cost is None:
        return VaultResult(
            ok=False,
            message="The vault is already at its maximum level.",
            level=level,
            capacity=capacity.vault_capacity(level),
        )
    if state.coins < cost:
        return VaultResult(
            ok=False,
            message=f"Not enough coins — a vault upgrade costs {cost}.",
            level=level,
            capacity=capacity.vault_capacity(level),
        )

    prev_coins = state.coins
    state.coins = prev_coins - cost
    new_level = level + 1
    state.vault_level = new_level
    new_cap = capacity.vault_capacity(new_level)

    now_dt = _resolve_now(now)
    record = _make_record(
        mutation_type=market.VAULT_UPGRADE_REASON,
        target="vault",
        prev_value=str(level),
        new_value=str(new_level),
        now=now_dt,
        mutation_id=_resolve_id(mutation_id_factory),
        guild_id=guild_id,
        actor_id=actor_id,
        actor_type=actor_type,
    )
    sink.record(record)
    # Decision #8 — economy_audit_log completeness: a vault upgrade is a coin
    # SINK, so alongside the vault-LEVEL row above, emit a target="coins" ledger
    # row (same money-flow reason token) carrying the coin balance before/after —
    # matching sell / buy / repair — so a log-derived wallet counts this sink.
    sink.record(
        _make_record(
            mutation_type=market.VAULT_UPGRADE_REASON,
            target="coins",
            prev_value=str(prev_coins),
            new_value=str(state.coins),
            now=now_dt,
            mutation_id=_resolve_id(mutation_id_factory),
            guild_id=guild_id,
            actor_id=actor_id,
            actor_type=actor_type,
        )
    )
    return VaultResult(
        ok=True,
        message=f"Vault upgraded to level {new_level} ({new_cap} slots) for {cost} coins.",
        level=new_level,
        capacity=new_cap,
        coins_spent=cost,
        new_balance=state.coins,
        record=record,
    )


def allocate_skill(
    state: MiningState,
    branch: str,
    points: int,
    *,
    sink: Sink,
    guild_id: int | None = None,
    actor_id: int | None = None,
    actor_type: str = ACTOR_PLAYER,
    now: datetime | None = None,
    mutation_id_factory: Callable[[], str] | None = None,
) -> SkillResult:
    """Spend *points* in a skill *branch*.

    Uses ``skills.is_branch`` to REJECT an unknown branch (rather than silently
    zeroing it), and enforces the core ``PER_BRANCH_CAP`` / ``SOFT_TOTAL_CAP``.
    A bad branch, non-positive points, or a cap breach returns ``ok=False`` and
    records nothing.
    """
    if not skills.is_branch(branch):
        return SkillResult(ok=False, message=f"{branch} is not a skill branch.", branch=branch)
    if points <= 0:
        return SkillResult(
            ok=False,
            message="Points must be positive.",
            branch=branch,
        )

    prev = state.skills.get(branch, 0)
    if prev + points > skills.PER_BRANCH_CAP:
        return SkillResult(
            ok=False,
            message=f"{branch} is capped at {skills.PER_BRANCH_CAP} points.",
            branch=branch,
        )
    if skills.total_spent(state.skills) + points > skills.SOFT_TOTAL_CAP:
        return SkillResult(
            ok=False,
            message=f"That exceeds the {skills.SOFT_TOTAL_CAP}-point soft total cap.",
            branch=branch,
        )

    new_total = prev + points
    state.skills[branch] = new_total

    record = _make_record(
        mutation_type=MUTATION_ALLOCATE_SKILL,
        target=f"skill:{branch}",
        prev_value=str(prev),
        new_value=str(new_total),
        now=_resolve_now(now),
        mutation_id=_resolve_id(mutation_id_factory),
        guild_id=guild_id,
        actor_id=actor_id,
        actor_type=actor_type,
    )
    sink.record(record)
    return SkillResult(
        ok=True,
        message=f"Allocated {points} point(s) to {branch}.",
        branch=branch,
        points=points,
        record=record,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _apply_wear(state: MiningState, action: str) -> tuple[str, ...]:
    """Tick 1 durability on each equipped slot the *action*'s wear plan names.

    Underground-only slots (the light) wear only below the surface (depth > 0),
    per ``workshop.WEAR_PLAN``. A slot with no ``durability`` entry does not wear
    (the core's safe default for untracked items). An item already at 0 (a broken
    item still sitting in the slot) does not wear again and is NOT re-reported —
    ``broke`` names only the items that hit 0 THIS tick, not ones that broke on an
    earlier action and were never cleared. Returns the names of any items that
    broke (hit 0) this tick.
    """
    broke: list[str] = []
    for slot, underground_only in workshop.WEAR_PLAN.get(action, ()):
        if underground_only and state.depth <= 0:
            continue
        item = state.equipped.get(slot)
        if not item or item not in state.durability:
            continue
        if state.durability[item] <= 0:
            continue  # already broken — nothing left to wear, and not a fresh break
        state.durability[item] -= 1
        if state.durability[item] == 0:
            broke.append(item)
    return tuple(broke)


__all__ = [
    "AuditRecord",
    "Sink",
    "InMemorySink",
    "MiningState",
    "MineResult",
    "HarvestResult",
    "TradeResult",
    "RepairResult",
    "MoveResult",
    "BuildResult",
    "VaultResult",
    "SkillResult",
    "ACTOR_PLAYER",
    "MUTATION_MINE",
    "MUTATION_HARVEST",
    "MUTATION_DESCEND",
    "MUTATION_ASCEND",
    "MUTATION_ALLOCATE_SKILL",
    "mine",
    "harvest",
    "sell",
    "buy",
    "repair",
    "descend",
    "ascend",
    "build_structure",
    "vault_upgrade",
    "allocate_skill",
]
