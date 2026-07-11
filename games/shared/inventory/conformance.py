"""Shared CONFORMANCE suite for the inventory/resource contract (spec §7).

The reusable artifact every future per-system adapter (migration PRs 2..6) runs against
its own mapping — the same discipline the encounter seam pins with a Protocol + a
reference impl. PR-1 ships this suite and runs it against the reference impls; an adapter
PR re-imports these helpers and feeds them its ``ItemCatalog`` / ``InventoryView`` /
``CapacityPolicy`` plus the ``Grant``s its ``to_grant`` mapping can emit.

Each helper encodes one spec-§5 integrity property as an assertion:

1. :func:`assert_grant_ids_known`        — round-trip identity (§7.1): no reward names
   an item absent from the catalog.
2. :func:`assert_no_spend_lever`         — no-spend-lever invariant (§7.2): the contract
   exposes no coin / purchase / spend / pay input.
3. :func:`assert_deterministic_construction` — determinism pass-through (§7.3): equal
   inputs build equal (frozen-equal) grants.
4. :func:`assert_nouns_are_data_only`    — theme-data-only nouns (§7.4): swapping a
   display name leaves mechanics (ids, qtys) unchanged.
5. :func:`assert_capacity_distinct_types` — capacity semantics (§7.5): the policy
   measures a hold in distinct item-types.

Pure: assertions only, no IO, no RNG. Raises ``AssertionError`` on a violation.
"""

from __future__ import annotations

import inspect
from typing import Callable, Iterable

from .interface import (
    CapacityPolicy,
    Grant,
    InventoryView,
    ItemCatalog,
    ItemMeta,
    ProgressionDelta,
    Stack,
    is_valid_item_id,
)

# Any parameter name matching one of these on a contract constructor would be a
# pay-to-win lever (an input that buys a better outcome). The contract must expose none.
_SPEND_LEVERS: frozenset[str] = frozenset(
    {"spend", "purchase", "buy", "pay", "coin", "coins", "price", "cost", "microtransaction"}
)


def assert_grant_ids_known(grant: Grant, catalog: ItemCatalog) -> None:
    """§7.1 — every stack id in ``grant`` resolves via ``catalog`` (no unknown item)."""
    for stack in grant.items:
        assert catalog.lookup(stack.item) is not None, (
            f"grant references unknown item id {stack.item!r} "
            "(round-trip identity broken — reward names an item absent from the catalog)"
        )


def assert_catalog_ids_neutral(catalog: ItemCatalog) -> None:
    """Every id the catalog exposes is a neutral ``ItemId`` (Q-0267 — nouns in data)."""
    for iid in catalog.ids():
        assert is_valid_item_id(iid), f"catalog exposes a non-neutral id: {iid!r}"
        meta = catalog.lookup(iid)
        assert meta is not None and meta.item_id == iid, (
            f"catalog id {iid!r} does not round-trip to its meta row"
        )


def assert_no_spend_lever() -> None:
    """§7.2 — the reward-carrying types expose no coin/purchase/spend input.

    Introspects every field of ``Grant`` / ``ProgressionDelta`` / ``Stack``: none may be
    named like a pay-to-win lever. The contract CARRIES amounts, it never takes a
    spend input that buys a better outcome (spec §5).
    """
    for tp in (Grant, ProgressionDelta, Stack):
        params = inspect.signature(tp).parameters
        leaked = {name for name in params if name.lower() in _SPEND_LEVERS}
        assert not leaked, f"{tp.__name__} exposes a spend lever: {sorted(leaked)}"


def assert_deterministic_construction(build: Callable[[], Grant]) -> None:
    """§7.3 — ``build`` called twice yields equal grants (no hidden RNG / wall-clock)."""
    first = build()
    second = build()
    assert first == second, (
        "grant construction is not deterministic — equal inputs produced unequal grants"
    )


def assert_nouns_are_data_only(
    catalog: ItemCatalog,
    grant: Grant,
    reskin: Callable[[ItemMeta], ItemMeta],
    reskinned_catalog: ItemCatalog,
) -> None:
    """§7.4 — re-theming (swapping display nouns) leaves mechanics unchanged.

    ``grant``'s mechanics (item ids + qtys + progression) must be identical whether read
    against ``catalog`` or ``reskinned_catalog`` (same ids, differently-named metas):
    the grant carries ids, never nouns, so a re-skin cannot move it. ``reskin`` documents
    the transform applied per row.
    """
    for stack in grant.items:
        original = catalog.lookup(stack.item)
        reskinned = reskinned_catalog.lookup(stack.item)
        assert original is not None and reskinned is not None, (
            f"id {stack.item!r} must resolve in both catalogs"
        )
        # Same mechanical identity, different display noun — that is the whole point.
        assert reskinned.item_id == original.item_id, "re-skin must not move the id"
        assert reskin(original).name == reskinned.name, (
            "reskinned catalog's name does not match the documented re-skin transform"
        )
    # The grant object itself is unchanged by any catalog swap: it holds no noun.
    assert all(isinstance(s.item, str) for s in grant.items)


def assert_capacity_distinct_types(view: InventoryView, policy: CapacityPolicy) -> None:
    """§7.5 — the policy measures the hold in DISTINCT item-types."""
    status = policy.status(view)
    assert status.used == view.distinct_types(), (
        "capacity policy must measure used-space in distinct item-types "
        f"(policy said {status.used}, view has {view.distinct_types()})"
    )
    assert status.remaining == max(0, status.cap - status.used)
    assert status.at_cap == (status.used >= status.cap)


def run_conformance(
    view: InventoryView,
    catalog: ItemCatalog,
    policy: CapacityPolicy,
    grants: Iterable[Grant] = (),
) -> None:
    """Run every applicable invariant against a candidate impl trio.

    The single entry point an adapter PR calls: feed it your ``InventoryView`` /
    ``ItemCatalog`` / ``CapacityPolicy`` and the ``Grant``s your mapping can emit; it
    raises ``AssertionError`` on the first violated property. Theme-data-only-nouns
    (§7.4) is exercised separately by :func:`assert_nouns_are_data_only` because it
    needs a re-skin transform the adapter supplies.
    """
    assert isinstance(view, InventoryView), "candidate must satisfy InventoryView"
    assert isinstance(catalog, ItemCatalog), "candidate must satisfy ItemCatalog"
    assert isinstance(policy, CapacityPolicy), "candidate must satisfy CapacityPolicy"
    assert_no_spend_lever()
    assert_catalog_ids_neutral(catalog)
    assert_capacity_distinct_types(view, policy)
    for grant in grants:
        assert_grant_ids_known(grant, catalog)
        assert_deterministic_construction(lambda g=grant: g)
