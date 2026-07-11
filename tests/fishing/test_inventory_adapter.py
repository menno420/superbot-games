"""Tests for the fishing → shared-inventory adapter (contract migration PR-2).

Exercises `games.fishing.inventory.adapter` against the shipped shared contract
(`games/shared/inventory/`) and its reusable §7 conformance suite: every species maps to a
valid neutral `ItemId`, the fishing catalog passes `run_conformance`, `Catch`/`CastOutcome`
map to the expected `Stack`/`Grant` deterministically, grants round-trip through
`ReferenceInventory`, and the reachable item ids stay pinned to `species.py` data (Q-0267).
"""

from __future__ import annotations

import dataclasses

import pytest

from games.fishing.core import species as species_table
from games.fishing.core.catch import CAST_COST, Catch, CastOutcome, resolve_cast
from games.fishing.inventory import adapter
from games.shared.inventory import conformance as C
from games.shared.inventory.interface import (
    EMPTY_GRANT,
    Grant,
    ItemMeta,
    ProgressionDelta,
    Stack,
    is_valid_item_id,
)
from games.shared.inventory.reference import (
    DefaultCapacityPolicy,
    DictItemCatalog,
    ReferenceInventory,
)


def _catch(species_id: str, size: int = 42) -> Catch:
    return Catch(species_id=species_id, size=size)


def _all_catches() -> list[Catch]:
    # One catch per species, with a distinct size so attrs differ per species.
    return [_catch(sid, size=10 + i) for i, sid in enumerate(species_table.species_ids())]


def _adapter_grants() -> list[Grant]:
    return [adapter.catch_to_grant(c) for c in _all_catches()]


# --- neutral-id mapping ----------------------------------------------------


def test_every_species_maps_to_a_valid_neutral_item_id() -> None:
    for sid in species_table.species_ids():
        iid = adapter.item_id_for_species(sid)
        assert iid == f"fish.{sid}"
        assert is_valid_item_id(iid), f"{iid!r} is not a neutral ItemId"


def test_species_id_round_trips_through_the_namespace_map() -> None:
    for sid in species_table.species_ids():
        iid = adapter.item_id_for_species(sid)
        assert adapter.species_id_for_item(iid) == sid


def test_species_id_for_item_rejects_a_foreign_namespace() -> None:
    with pytest.raises(ValueError):
        adapter.species_id_for_item("ore.diamond")


# --- catalog ---------------------------------------------------------------


def test_catalog_has_one_row_per_species_with_relayed_nouns() -> None:
    cat = adapter.fishing_catalog()
    assert set(cat.ids()) == {f"fish.{sid}" for sid in species_table.species_ids()}
    for row in species_table.all_species():
        meta = cat.lookup(f"fish.{row.species_id}")
        assert meta is not None
        # Nouns are RELAYED from species.py data, not authored in the adapter.
        assert meta.name == row.name
        assert meta.emoji == row.emoji
        assert meta.value == row.size_rank  # carried data number, never rolled


def test_fishing_catalog_passes_run_conformance() -> None:
    cat = adapter.fishing_catalog()
    inv = ReferenceInventory().add_grant(adapter.catch_to_grant(_catch("bass")))
    # The shipped §7 suite, run against the fishing catalog + adapter grants.
    C.run_conformance(inv, cat, DefaultCapacityPolicy(), grants=_adapter_grants())


def test_grant_ids_are_all_known_to_the_catalog() -> None:
    cat = adapter.fishing_catalog()
    for grant in _adapter_grants():
        C.assert_grant_ids_known(grant, cat)


def test_catalog_ids_are_neutral() -> None:
    C.assert_catalog_ids_neutral(adapter.fishing_catalog())


def test_nouns_are_data_only_under_a_reskin() -> None:
    # A re-skin transform: uppercase every display name. Mechanics (ids) must not move.
    reskin = lambda m: dataclasses.replace(m, name=m.name.upper())  # noqa: E731
    base = adapter.fishing_catalog()
    reskinned = DictItemCatalog(tuple(reskin(base.lookup(i)) for i in base.ids()))
    for grant in _adapter_grants():
        C.assert_nouns_are_data_only(base, grant, reskin, reskinned)


# --- catch_to_stack / catch_to_grant --------------------------------------


def test_catch_to_stack_shapes_the_expected_stack() -> None:
    catch = _catch("legend_carp", size=74)
    stack = adapter.catch_to_stack(catch)
    assert stack.item == "fish.legend_carp"
    assert stack.qty == 1
    assert stack.attrs["size"] == 74
    assert stack.attrs["size_rank"] == species_table.get("legend_carp").size_rank


def test_catch_to_grant_wraps_one_stack_with_empty_progression() -> None:
    catch = _catch("pike", size=40)
    grant = adapter.catch_to_grant(catch)
    assert len(grant.items) == 1
    assert grant.items[0].item == "fish.pike"
    assert grant.items[0].qty == 1
    # Fishing defines no XP/currency today — progression is the empty identity.
    assert grant.progression == ProgressionDelta()


def test_catch_to_grant_is_deterministic() -> None:
    catch = _catch("bass", size=33)
    assert adapter.catch_to_grant(catch) == adapter.catch_to_grant(catch)
    C.assert_deterministic_construction(lambda: adapter.catch_to_grant(catch))


# --- cast_to_grant ---------------------------------------------------------


def test_cast_to_grant_no_bite_is_empty_grant() -> None:
    no_bite = CastOutcome(bit=False, catch=None, narration="nothing", energy_cost=CAST_COST)
    assert adapter.cast_to_grant(no_bite) is EMPTY_GRANT


def test_cast_to_grant_too_tired_outcome_is_empty_grant() -> None:
    # A real resolver no-bite (too tired to cast) maps to the empty grant.
    outcome = resolve_cast(seed=1, spot_id="pond", energy=CAST_COST - 1)
    assert outcome.bit is False
    assert adapter.cast_to_grant(outcome) is EMPTY_GRANT


def test_cast_to_grant_bite_yields_a_single_stack_grant() -> None:
    catch = _catch("minnow", size=15)
    outcome = CastOutcome(bit=True, catch=catch, narration="🐟 land it", energy_cost=CAST_COST)
    grant = adapter.cast_to_grant(outcome)
    assert len(grant.items) == 1
    assert grant.items[0].item == "fish.minnow"
    assert grant == adapter.catch_to_grant(catch)


def test_cast_to_grant_from_a_real_resolved_bite() -> None:
    # Drive the real resolver until a bite lands, then adapt its outcome.
    bite = None
    for i in range(50):
        out = resolve_cast(seed=i, spot_id="deep")
        if out.bit and out.catch is not None:
            bite = out
            break
    assert bite is not None, "expected at least one bite across the seed sweep"
    grant = adapter.cast_to_grant(bite)
    assert len(grant.items) == 1
    assert grant.items[0].item == f"fish.{bite.catch.species_id}"
    assert grant.items[0].attrs["size"] == bite.catch.size


# --- round-trip through the reference inventory ----------------------------


def test_grants_round_trip_into_reference_inventory() -> None:
    inv = ReferenceInventory()
    for grant in _adapter_grants():
        inv = inv.add_grant(grant)
    # One catch per species → one of each distinct type, each held qty 1.
    assert inv.distinct_types() == len(species_table.species_ids())
    for sid in species_table.species_ids():
        assert inv.held(f"fish.{sid}") == 1


def test_repeated_catches_stack_by_id() -> None:
    inv = ReferenceInventory()
    for _ in range(3):
        inv = inv.add_grant(adapter.catch_to_grant(_catch("bass")))
    assert inv.held("fish.bass") == 3
    assert inv.distinct_types() == 1


def test_default_capacity_policy_status_over_adapter_grants() -> None:
    inv = ReferenceInventory()
    for grant in _adapter_grants():
        inv = inv.add_grant(grant)
    status = DefaultCapacityPolicy().status(inv)
    assert status.used == inv.distinct_types()
    assert status.at_cap is False  # four fish species is far under the 40-type soft cap
    assert status.remaining == status.cap - status.used


# --- theme-data guard: reachable ids live in species.py --------------------


def test_reachable_item_ids_are_exactly_the_species_keys() -> None:
    reachable = adapter.reachable_item_ids()
    assert set(reachable) == {f"fish.{sid}" for sid in species_table.species_ids()}
    # Every reachable id's suffix is a key in species.py — nouns/identities stay in data.
    for iid in reachable:
        assert species_table.is_species(adapter.species_id_for_item(iid))


def test_reachable_ids_track_the_species_table(monkeypatch: pytest.MonkeyPatch) -> None:
    # Remove a species row → the reachable item ids and catalog shrink to match, proving the
    # identities are driven by species.py DATA, not hardcoded in the adapter.
    trimmed = tuple(r for r in species_table.all_species() if r.species_id != "pike")
    monkeypatch.setattr(species_table, "_SPECIES", trimmed)
    monkeypatch.setattr(species_table, "_BY_ID", {r.species_id: r for r in trimmed})
    assert "fish.pike" not in adapter.reachable_item_ids()
    assert "fish.pike" not in adapter.fishing_catalog().ids()
    assert "fish.bass" in adapter.reachable_item_ids()
