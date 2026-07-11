"""REFERENCE inventory impls — deterministic, dependency-free, in-memory.

The conformance reference for the ``games/shared/inventory/`` seam, mirroring
``games/shared/encounter/reference.py``: a minimal, IO-free implementation of every
Protocol in ``interface.py`` so consumers (and the conformance suite) are unblocked
before a host store exists. Replace each via its Protocol without touching consumers.

* ``DictItemCatalog``    — an ``ItemCatalog`` over an in-memory ``{ItemId: ItemMeta}``.
* ``ReferenceInventory`` — an immutable, dict-backed ``InventoryView``; ``add`` /
  ``add_grant`` return a NEW inventory (pure — no in-place mutation, no IO).
* ``DefaultCapacityPolicy`` — the distinct-types soft-cap ``CapacityPolicy``, pinned to
  mining's ``PACK_SOFT_CAP = 40`` so promoting ``capacity.py`` cannot silently move the
  cap (spec §7.5 regression pin).

Determinism: every method is a pure function of the object's stored state; ordering is
made explicit (sorted by id) so outputs are byte-reproducible. No RNG, no wall-clock, no
IO.
"""

from __future__ import annotations

from typing import Mapping

from .interface import (
    CapacityPolicy,
    CapStatus,
    Grant,
    ItemCatalog,
    ItemId,
    ItemMeta,
    InventoryView,
    Stack,
)

# Mining's soft cap, in DISTINCT item-types (games/mining/core/capacity.py PACK_SOFT_CAP).
# Promoted verbatim as the reference default; a regression pin (spec §7.5).
PACK_SOFT_CAP: int = 40


class DictItemCatalog(ItemCatalog):
    """An ``ItemCatalog`` backed by an in-memory ``{ItemId: ItemMeta}`` mapping."""

    def __init__(self, metas: Mapping[ItemId, ItemMeta] | tuple[ItemMeta, ...] = ()) -> None:
        rows: dict[ItemId, ItemMeta] = {}
        if isinstance(metas, Mapping):
            rows.update(metas)
        else:
            for meta in metas:
                rows[meta.item_id] = meta
        # Frozen after construction; ids() returns a stable sorted order.
        self._rows: dict[ItemId, ItemMeta] = rows

    def lookup(self, item_id: ItemId) -> ItemMeta | None:
        return self._rows.get(item_id)

    def ids(self) -> tuple[ItemId, ...]:
        return tuple(sorted(self._rows))


class ReferenceInventory(InventoryView):
    """An immutable, dict-backed ``InventoryView``.

    State is a frozen snapshot of ``{ItemId: qty}`` (qty > 0 only). ``add`` / ``add_grant``
    return a NEW ``ReferenceInventory`` — the reference is pure, so a hold never mutates
    under a caller. A negative-qty stack (a loss) reduces the count and clamps at 0; the
    item drops out of ``distinct_types`` once it reaches 0.
    """

    def __init__(self, counts: Mapping[ItemId, int] | None = None) -> None:
        self._counts: dict[ItemId, int] = {
            item: qty for item, qty in (counts or {}).items() if qty > 0
        }

    def held(self, item: ItemId) -> int:
        return self._counts.get(item, 0)

    def distinct_types(self) -> int:
        return len(self._counts)

    def stacks(self) -> tuple[Stack, ...]:
        # Deterministic order: sorted by id. Per-instance ``attrs`` are not tracked by
        # this fungible-count reference; a host that holds non-fungibles supplies its own.
        return tuple(Stack(item, qty) for item, qty in sorted(self._counts.items()))

    def add(self, stack: Stack) -> "ReferenceInventory":
        """Return a new inventory with ``stack`` folded in (qty may be negative = loss)."""
        new_counts = dict(self._counts)
        updated = new_counts.get(stack.item, 0) + stack.qty
        if updated > 0:
            new_counts[stack.item] = updated
        else:
            new_counts.pop(stack.item, None)
        return ReferenceInventory(new_counts)

    def add_grant(self, grant: Grant) -> "ReferenceInventory":
        """Return a new inventory with every stack in ``grant`` folded in (order-stable)."""
        result = self
        for stack in grant.items:
            result = result.add(stack)
        return result


class DefaultCapacityPolicy(CapacityPolicy):
    """The default ``CapacityPolicy``: a distinct-types soft cap (mining's model).

    ``cap`` defaults to ``PACK_SOFT_CAP`` (40). ``status`` reports ``used`` = the view's
    distinct-type count against ``cap`` — warn-not-block is the caller's policy (the
    contract only measures, per mining's ``capacity.py``).
    """

    def __init__(self, cap: int = PACK_SOFT_CAP) -> None:
        self._cap = cap

    def status(self, view: InventoryView) -> CapStatus:
        return CapStatus(used=view.distinct_types(), cap=self._cap)
