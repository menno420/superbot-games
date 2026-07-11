"""Conformance suite — the reusable §7 artifact, run against the reference impls.

This exercises ``conformance.py`` end to end: every invariant a future per-system adapter
must satisfy (round-trip identity, no-spend-lever, determinism, theme-data-only nouns,
capacity semantics) asserted against the reference ``ReferenceInventory`` /
``DictItemCatalog`` / ``DefaultCapacityPolicy``. An adapter PR re-imports these helpers
and feeds them its own trio — this test is the template.
"""

from __future__ import annotations

import dataclasses

import pytest

from games.shared.inventory import conformance as C
from games.shared.inventory.interface import (
    Grant,
    ItemMeta,
    ProgressionDelta,
    Stack,
)
from games.shared.inventory.reference import (
    DefaultCapacityPolicy,
    DictItemCatalog,
    ReferenceInventory,
)


def _catalog() -> DictItemCatalog:
    return DictItemCatalog(
        (
            ItemMeta("ore.diamond", name="Diamond", kind="resource", value=50),
            ItemMeta("fish.legend_carp", name="Legendary Carp", kind="resource", value=30),
        )
    )


def _sample_grants() -> list[Grant]:
    return [
        Grant(items=(Stack("ore.diamond", 5),)),
        Grant(items=(Stack("fish.legend_carp", 1, {"size": 74}),), progression=ProgressionDelta(game_xp=10)),
        Grant(items=(Stack("ore.diamond", -1),)),  # a loss
        Grant(progression=ProgressionDelta(global_xp=3, currency=2, capability="fly")),
    ]


# --- the full suite against the reference impls ---------------------------


def test_reference_impls_pass_full_conformance() -> None:
    cat = _catalog()
    inv = ReferenceInventory().add_grant(Grant(items=(Stack("ore.diamond", 3),)))
    C.run_conformance(inv, cat, DefaultCapacityPolicy(), grants=_sample_grants())


# --- §7.1 round-trip identity ---------------------------------------------


def test_round_trip_identity_passes_for_known_ids() -> None:
    cat = _catalog()
    for grant in _sample_grants():
        C.assert_grant_ids_known(grant, cat)


def test_round_trip_identity_fails_for_unknown_id() -> None:
    cat = _catalog()
    with pytest.raises(AssertionError):
        C.assert_grant_ids_known(Grant(items=(Stack("ore.unobtanium", 1),)), cat)


def test_catalog_ids_must_be_neutral() -> None:
    C.assert_catalog_ids_neutral(_catalog())
    # A catalog carrying a display-noun key trips the neutral-id assertion.
    bad = DictItemCatalog({"Lucky Charm": ItemMeta("Lucky Charm", name="Lucky Charm", kind="tool")})
    with pytest.raises(AssertionError):
        C.assert_catalog_ids_neutral(bad)


# --- §7.2 no-spend-lever --------------------------------------------------


def test_no_spend_lever_invariant() -> None:
    # The contract types expose no coin/purchase/spend input at all.
    C.assert_no_spend_lever()


# --- §7.3 determinism pass-through ----------------------------------------


def test_determinism_pass_through() -> None:
    C.assert_deterministic_construction(lambda: Grant(items=(Stack("ore.diamond", 3),)))


# --- §7.4 theme-data-only nouns -------------------------------------------


def test_nouns_are_data_only_under_a_reskin() -> None:
    cat = _catalog()

    def reskin(meta: ItemMeta) -> ItemMeta:
        # A pure re-theme: swap the display noun, keep the mechanical id.
        return dataclasses.replace(meta, name=f"Reskinned {meta.name}", emoji="✨")

    reskinned = DictItemCatalog(tuple(reskin(cat.lookup(i)) for i in cat.ids()))  # type: ignore[arg-type]
    grant = Grant(items=(Stack("ore.diamond", 5), Stack("fish.legend_carp", 1)))
    # Mechanics (ids) unchanged across the re-skin; only nouns moved.
    C.assert_nouns_are_data_only(cat, grant, reskin, reskinned)


def test_reskin_that_moves_the_id_is_rejected() -> None:
    cat = _catalog()

    def reskin(meta: ItemMeta) -> ItemMeta:
        return dataclasses.replace(meta, name=f"Reskinned {meta.name}")

    # A catalog whose ids DON'T match (id moved) must fail the mechanics-unchanged check.
    moved = DictItemCatalog((ItemMeta("ore.moved", name="Reskinned Diamond", kind="resource"),))
    grant = Grant(items=(Stack("ore.diamond", 1),))
    with pytest.raises(AssertionError):
        C.assert_nouns_are_data_only(cat, grant, reskin, moved)


# --- §7.5 capacity semantics ----------------------------------------------


def test_capacity_distinct_types_semantics() -> None:
    inv = ReferenceInventory({"ns.a": 3, "ns.b": 1})
    C.assert_capacity_distinct_types(inv, DefaultCapacityPolicy())
