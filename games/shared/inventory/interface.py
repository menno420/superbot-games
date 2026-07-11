"""PUBLIC shared inventory / resource contract (claim-first per docs/lanes.md).

This is the unified item · quantity · reward · inventory vocabulary specified by
``docs/design/world-inventory-resource-contract.md`` §2. It is the ONE reward /
inventory shape the world games converge on: six divergent representations
(mining ``Reward``/dig-tuple/explore-tuple, fishing ``Catch``, quest
``RewardBundle``, the encounter ``payload``) all map onto these types via a thin
per-system adapter (migration PRs 2..6 — NOT in this PR).

Any change to this interface's public surface is an INTERFACE CHANGE and must be
announced in ``control/status.md`` in the same session it ships (single-seat repo;
``docs/lanes.md`` §"games/shared/** — claim-first"). This mirrors the
``games/shared/encounter/`` seam precedent verbatim.

Design floor (spec §5), enforced by construction here and pinned by the conformance
suite (``conformance.py``, spec §7):

* **Pure / deterministic** — frozen dataclasses + ``@runtime_checkable`` Protocols,
  stdlib-only. No Discord, DB, IO, wall-clock, or RNG. Inert data + interfaces; the
  contract CANNOT perturb any resolver's determinism.
* **No pay-to-win** (Q-0039 / Q-0190) — the contract CARRIES values, it never rolls
  or derives them. There is no coin / purchase / spend lever anywhere; every reward
  number stays sim-pinned in its owning system.
* **Nouns in data** (Q-0267) — item identity is a NEUTRAL ``ItemId``; every
  player-visible noun lives in ``ItemMeta`` / an ``ItemCatalog`` data row, never in a
  mechanic. This package holds NO player-visible noun.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import Mapping, Protocol, runtime_checkable

# ---------------------------------------------------------------------------
# 2a. Item identity — a neutral id + a data-side theme lookup
# ---------------------------------------------------------------------------

# A NewType-style neutral id: "ore.diamond", "fish.legend_carp", "curio.coral_idol".
# NEVER a player-facing noun. Mechanics key on this; nouns live in ``ItemMeta`` data.
ItemId = str

# A neutral id is a dotted path of lowercase ascii segments: at least a
# ``namespace.name`` pair, each segment ``[a-z0-9_]+``. This is what distinguishes a
# neutral id ("ore.diamond") from a player-facing noun ("diamond", "Lucky Charm"):
# a noun has no namespace, or carries capitals / spaces / punctuation.
_ITEM_ID_RE = re.compile(r"^[a-z0-9_]+(?:\.[a-z0-9_]+)+$")


def is_valid_item_id(value: object) -> bool:
    """True iff ``value`` is a neutral ``ItemId`` (dotted lowercase, >= 2 segments).

    Rejects the non-neutral shapes the design doc §1a calls out: bare display nouns
    (``"diamond"`` — no namespace), spaced nouns (``"Lucky Charm"``), and any string
    carrying uppercase or punctuation outside ``[a-z0-9_.]``.
    """
    return isinstance(value, str) and _ITEM_ID_RE.fullmatch(value) is not None


def item_id(value: str) -> ItemId:
    """Validating constructor for an ``ItemId``. Raises ``ValueError`` on a non-neutral id.

    Use at trust boundaries (adapter inputs, catalog construction) so a display noun
    can never leak in as an identity key — the Q-0267 gap this contract closes.
    """
    if not is_valid_item_id(value):
        raise ValueError(
            f"not a neutral ItemId: {value!r} "
            "(expected dotted lowercase, e.g. 'ore.diamond'; nouns belong in ItemMeta)"
        )
    return value


@dataclass(frozen=True)
class ItemMeta:
    """The theme + economy data for one item id — the ONLY re-theme surface (Q-0267).

    Every player-visible noun (``name``, ``emoji``) is a data row here, swappable
    without touching any mechanic. ``value`` is a CARRIED economy/display number, never
    computed by this contract.
    """

    item_id: ItemId
    name: str
    kind: str  # "resource" | "tool" | "consumable" | ...
    stackable: bool = True
    value: int = 1
    emoji: str = ""
    tags: frozenset[str] = frozenset()


@runtime_checkable
class ItemCatalog(Protocol):
    """A theme-data lookup: neutral id -> ``ItemMeta``.

    Each system supplies one (or shares one). Mechanics read nouns off it and never
    hard-code a name in a logic branch — generalising fishing's already-correct
    ``species.py`` (neutral id + data row) to every item.
    """

    def lookup(self, item_id: ItemId) -> ItemMeta | None:
        """Return the meta row for ``item_id``, or ``None`` if unknown."""
        ...

    def ids(self) -> tuple[ItemId, ...]:
        """Return every known item id (deterministic order)."""
        ...


# ---------------------------------------------------------------------------
# 2b. Quantity / stack
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Stack:
    """A quantity of one item.

    ``qty`` is normally >= 1 for a fungible stack; a NEGATIVE ``qty`` expresses a loss
    (mining explore ``delta<0``), per spec §2c / §6-D — so no positivity check is
    enforced here (the contract carries, it does not police economy). ``attrs`` carries
    per-instance magnitudes (e.g. a fish's ``size``) for non-fungible items without a
    parallel type; it is normalised to a read-only mapping so a passed dict cannot be
    mutated through the frozen stack.
    """

    item: ItemId
    qty: int = 1
    attrs: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Defensive copy into a read-only proxy: immutability by construction, and a
        # caller's later mutation of the source dict cannot leak into this stack.
        object.__setattr__(self, "attrs", MappingProxyType(dict(self.attrs)))


# ---------------------------------------------------------------------------
# 2c. Reward / grant — the ONE reward shape
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProgressionDelta:
    """Non-item grants — XP / currency / an earned capability. Subsumes quest's
    ``RewardBundle``.

    Every amount is CARRIED (set by the granting system), never computed here. The
    ``currency`` field is a *carried grant amount*, never an input that buys a better
    outcome — there is no spend lever (spec §5, no pay-to-win). All numeric fields
    default to zero and ``capability`` to ``None`` so an empty delta is the identity for
    :func:`add_delta`.
    """

    global_xp: int = 0
    game_xp: int = 0
    currency: int = 0
    capability: str | None = None


@dataclass(frozen=True)
class Grant:
    """The ONE reward shape: item stacks + a progression delta.

    A stack's ``qty`` may be negative to express a loss (spec §2c). One ``Grant``
    expresses all six current reward shapes (design doc §2c). Defaults give the empty
    grant, the identity for :func:`merge_grants`.
    """

    items: tuple[Stack, ...] = ()
    progression: ProgressionDelta = field(default_factory=ProgressionDelta)


# ---------------------------------------------------------------------------
# 2d. Inventory / capacity — pure interface, the host store seam left open
# ---------------------------------------------------------------------------


@runtime_checkable
class InventoryView(Protocol):
    """Read-only view of a player's hold. The BACKING STORE is the host's — the
    contract is a pure interface, no persistence / IO here.

    ``held`` / ``distinct_types`` are the spec §2d surface verbatim; ``stacks`` is a
    minimal gap-fill (spec §2d named only the two scalar queries) so the conformance
    suite can enumerate a hold without knowing its ids up front.
    """

    def held(self, item: ItemId) -> int:
        """Return the quantity of ``item`` currently held (0 if none)."""
        ...

    def distinct_types(self) -> int:
        """Return the count of distinct item types held — the capacity unit (§2d)."""
        ...

    def stacks(self) -> tuple[Stack, ...]:
        """Return every held stack (deterministic order). Gap-fill beyond §2d."""
        ...


@dataclass(frozen=True)
class CapStatus:
    """A hold's fill against a (soft) cap, in distinct item-types — mining's
    ``capacity.py`` shape, promoted verbatim so its warn-not-block policy is preserved.
    """

    used: int
    cap: int

    @property
    def remaining(self) -> int:
        return max(0, self.cap - self.used)

    @property
    def at_cap(self) -> bool:
        return self.used >= self.cap


@runtime_checkable
class CapacityPolicy(Protocol):
    """How a host measures a hold against a cap. Default = distinct-types soft cap
    (mining's chosen model); a host may supply its own without changing the contract.
    """

    def status(self, view: InventoryView) -> CapStatus:
        """Measure ``view`` against this policy's cap."""
        ...


# ---------------------------------------------------------------------------
# Pure helper constructors — all deterministic, stdlib-only, no IO
# ---------------------------------------------------------------------------

# The empty grant — the identity element for ``merge_grants``. Reusable singleton.
EMPTY_GRANT: Grant = Grant()


def empty_grant() -> Grant:
    """Return the empty grant (no items, zero progression)."""
    return EMPTY_GRANT


def add_delta(a: ProgressionDelta, b: ProgressionDelta) -> ProgressionDelta:
    """Field-wise sum of two progression deltas. Pure and associative.

    Numeric fields add; ``capability`` uses last-writer-wins (``b`` if it names one,
    else ``a``) — a hold has one capability slot, and last-writer-wins is associative.
    ``ProgressionDelta()`` is the identity.
    """
    return ProgressionDelta(
        global_xp=a.global_xp + b.global_xp,
        game_xp=a.game_xp + b.game_xp,
        currency=a.currency + b.currency,
        capability=b.capability if b.capability is not None else a.capability,
    )


def scale_delta(d: ProgressionDelta, factor: int) -> ProgressionDelta:
    """Scale every numeric field of ``d`` by an integer ``factor``. Pure.

    ``capability`` is a discrete slot, not a magnitude, so it is carried unchanged.
    Scaling distributes over :func:`add_delta` for the numeric fields.
    """
    return replace(
        d,
        global_xp=d.global_xp * factor,
        game_xp=d.game_xp * factor,
        currency=d.currency * factor,
    )


def merge_grants(a: Grant, b: Grant) -> Grant:
    """Concatenate two grants: items joined, progression summed. Pure and associative.

    ``EMPTY_GRANT`` is the identity. Stacks are NOT coalesced by id here — a grant is a
    transcript of what was awarded; folding stacks into a hold is a host/inventory
    concern (see ``reference.ReferenceInventory.add_grant``).
    """
    return Grant(
        items=a.items + b.items,
        progression=add_delta(a.progression, b.progression),
    )
