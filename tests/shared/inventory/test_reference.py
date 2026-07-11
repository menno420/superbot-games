"""Reference impls — round-trips, catalog lookup, capacity status, Protocol conformance.

Pins ``reference.py``: the dict-backed ``ReferenceInventory`` add/query round-trips and
stays pure (immutable), ``DictItemCatalog`` looks meta up by neutral id, the
``DefaultCapacityPolicy`` reports the right ``CapStatus`` under/at/over cap, and each
reference satisfies its Protocol via ``isinstance`` (runtime_checkable).
"""

from __future__ import annotations

from games.shared.inventory.interface import (
    CapacityPolicy,
    Grant,
    InventoryView,
    ItemCatalog,
    ItemMeta,
    ProgressionDelta,
    Stack,
)
from games.shared.inventory.reference import (
    PACK_SOFT_CAP,
    DefaultCapacityPolicy,
    DictItemCatalog,
    ReferenceInventory,
)


def _catalog() -> DictItemCatalog:
    return DictItemCatalog(
        (
            ItemMeta("ore.diamond", name="Diamond", kind="resource", value=50, emoji="💎"),
            ItemMeta("fish.legend_carp", name="Legendary Carp", kind="resource", value=30),
        )
    )


# --- DictItemCatalog ------------------------------------------------------


def test_catalog_lookup_by_neutral_id() -> None:
    cat = _catalog()
    meta = cat.lookup("ore.diamond")
    assert meta is not None and meta.name == "Diamond" and meta.value == 50


def test_catalog_lookup_unknown_returns_none() -> None:
    assert _catalog().lookup("ore.unobtanium") is None


def test_catalog_ids_are_sorted_and_complete() -> None:
    assert _catalog().ids() == ("fish.legend_carp", "ore.diamond")


def test_catalog_accepts_a_mapping_too() -> None:
    m = ItemMeta("ore.iron", name="Iron", kind="resource")
    cat = DictItemCatalog({"ore.iron": m})
    assert cat.lookup("ore.iron") is m


# --- ReferenceInventory ---------------------------------------------------


def test_add_and_query_round_trip() -> None:
    inv = ReferenceInventory().add(Stack("ore.diamond", 3)).add(Stack("ore.diamond", 2))
    assert inv.held("ore.diamond") == 5
    assert inv.held("ore.iron") == 0
    assert inv.distinct_types() == 1


def test_add_grant_folds_every_stack() -> None:
    grant = Grant(
        items=(Stack("ore.diamond", 3), Stack("fish.legend_carp", 1), Stack("ore.diamond", 1)),
        progression=ProgressionDelta(game_xp=10),
    )
    inv = ReferenceInventory().add_grant(grant)
    assert inv.held("ore.diamond") == 4
    assert inv.held("fish.legend_carp") == 1
    assert inv.distinct_types() == 2


def test_add_is_pure_original_unchanged() -> None:
    base = ReferenceInventory().add(Stack("ore.diamond", 3))
    grown = base.add(Stack("ore.diamond", 5))
    assert base.held("ore.diamond") == 3  # original snapshot untouched
    assert grown.held("ore.diamond") == 8


def test_negative_qty_reduces_and_clamps_at_zero() -> None:
    inv = ReferenceInventory().add(Stack("ore.diamond", 3)).add(Stack("ore.diamond", -5))
    assert inv.held("ore.diamond") == 0
    assert inv.distinct_types() == 0  # item drops out once it hits zero


def test_stacks_are_sorted_and_reflect_counts() -> None:
    inv = ReferenceInventory().add(Stack("ore.iron", 2)).add(Stack("ore.diamond", 1))
    assert inv.stacks() == (Stack("ore.diamond", 1), Stack("ore.iron", 2))


# --- DefaultCapacityPolicy ------------------------------------------------


def test_capacity_status_under_cap() -> None:
    inv = ReferenceInventory().add(Stack("ore.diamond", 1)).add(Stack("ore.iron", 1))
    st = DefaultCapacityPolicy().status(inv)
    assert st.used == 2 and st.cap == PACK_SOFT_CAP
    assert st.remaining == PACK_SOFT_CAP - 2 and not st.at_cap


def test_capacity_status_at_cap() -> None:
    counts = {f"ns.item_{i}": 1 for i in range(PACK_SOFT_CAP)}
    inv = ReferenceInventory(counts)
    st = DefaultCapacityPolicy().status(inv)
    assert st.used == PACK_SOFT_CAP and st.remaining == 0 and st.at_cap


def test_capacity_status_over_cap() -> None:
    counts = {f"ns.item_{i}": 1 for i in range(PACK_SOFT_CAP + 3)}
    st = DefaultCapacityPolicy().status(ReferenceInventory(counts))
    assert st.used == PACK_SOFT_CAP + 3 and st.remaining == 0 and st.at_cap


def test_default_cap_is_mining_pack_soft_cap() -> None:
    # Regression pin (spec §7.5): promoting capacity.py must not move the cap.
    assert PACK_SOFT_CAP == 40
    assert DefaultCapacityPolicy().status(ReferenceInventory()).cap == 40


def test_capacity_policy_accepts_a_custom_cap() -> None:
    st = DefaultCapacityPolicy(cap=5).status(ReferenceInventory({"ns.a": 1}))
    assert st.cap == 5 and st.used == 1


# --- Protocol conformance (runtime_checkable) -----------------------------


def test_reference_impls_satisfy_their_protocols() -> None:
    assert isinstance(ReferenceInventory(), InventoryView)
    assert isinstance(DictItemCatalog(), ItemCatalog)
    assert isinstance(DefaultCapacityPolicy(), CapacityPolicy)
