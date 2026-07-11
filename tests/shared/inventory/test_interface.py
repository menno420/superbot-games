"""Interface types — construction, frozen-ness, id validation, pure helper algebra.

Pins the §2 contract types: each constructs, each is frozen (mutation raises), the
``ItemId`` validation rejects non-neutral display nouns, and the ``Grant`` /
``ProgressionDelta`` helpers are pure and associative where the contract claims it.
"""

from __future__ import annotations

import dataclasses

import pytest

from games.shared.inventory.interface import (
    EMPTY_GRANT,
    CapStatus,
    Grant,
    ItemMeta,
    ProgressionDelta,
    Stack,
    add_delta,
    empty_grant,
    is_valid_item_id,
    item_id,
    merge_grants,
    scale_delta,
)


# --- construction ---------------------------------------------------------


def test_each_type_constructs_with_documented_defaults() -> None:
    assert Stack("ore.diamond").qty == 1
    assert Stack("ore.diamond").attrs == {}
    meta = ItemMeta("ore.diamond", name="Diamond", kind="resource")
    assert meta.stackable is True and meta.value == 1 and meta.emoji == "" and meta.tags == frozenset()
    assert ProgressionDelta() == ProgressionDelta(0, 0, 0, None)
    assert Grant() == Grant(items=(), progression=ProgressionDelta())
    assert CapStatus(2, 40).remaining == 38


def test_stack_carries_per_instance_attrs() -> None:
    fish = Stack("fish.legend_carp", 1, {"size": 74})
    assert fish.attrs["size"] == 74


def test_stack_qty_may_be_negative_to_express_a_loss() -> None:
    # Spec §2c / §6-D: a negative qty is a loss; the contract carries, never polices.
    loss = Stack("ore.iron", -2)
    assert loss.qty == -2


# --- frozen-ness ----------------------------------------------------------


@pytest.mark.parametrize(
    "obj, field_name, value",
    [
        (Stack("ore.diamond", 1), "qty", 9),
        (ItemMeta("ore.diamond", name="Diamond", kind="resource"), "name", "X"),
        (ProgressionDelta(), "global_xp", 5),
        (Grant(), "items", (Stack("ore.diamond"),)),
        (CapStatus(1, 40), "used", 2),
    ],
)
def test_types_are_frozen(obj: object, field_name: str, value: object) -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(obj, field_name, value)


def test_stack_attrs_are_read_only_even_from_the_source_dict() -> None:
    src = {"size": 74}
    fish = Stack("fish.legend_carp", 1, src)
    # Mutating the source dict after construction must not leak into the stack.
    src["size"] = 999
    assert fish.attrs["size"] == 74
    # And the stored proxy itself rejects mutation.
    with pytest.raises(TypeError):
        fish.attrs["size"] = 1  # type: ignore[index]


# --- ItemId validation ----------------------------------------------------


@pytest.mark.parametrize("good", ["ore.diamond", "fish.legend_carp", "curio.coral_idol", "a.b.c"])
def test_neutral_ids_accepted(good: str) -> None:
    assert is_valid_item_id(good)
    assert item_id(good) == good


@pytest.mark.parametrize(
    "bad",
    ["diamond", "Lucky Charm", "lucky charm", "Legendary Carp", "ore.Diamond", "ore diamond", "", "ore.", ".diamond", "ore-diamond"],
)
def test_non_neutral_ids_rejected(bad: str) -> None:
    # These are the §1a display-noun shapes an ItemId must never be.
    assert not is_valid_item_id(bad)
    with pytest.raises(ValueError):
        item_id(bad)


def test_is_valid_item_id_rejects_non_strings() -> None:
    assert not is_valid_item_id(42)
    assert not is_valid_item_id(None)


# --- ProgressionDelta algebra --------------------------------------------


def test_add_delta_sums_numeric_fields() -> None:
    a = ProgressionDelta(global_xp=1, game_xp=2, currency=3)
    b = ProgressionDelta(global_xp=10, game_xp=20, currency=30)
    assert add_delta(a, b) == ProgressionDelta(global_xp=11, game_xp=22, currency=33)


def test_add_delta_identity_and_associativity() -> None:
    a = ProgressionDelta(global_xp=1, currency=2)
    b = ProgressionDelta(global_xp=3, capability="fly")
    c = ProgressionDelta(game_xp=5, capability="swim")
    # identity
    assert add_delta(a, ProgressionDelta()) == a
    assert add_delta(ProgressionDelta(), a) == a
    # associativity (incl. capability last-writer-wins)
    assert add_delta(add_delta(a, b), c) == add_delta(a, add_delta(b, c))


def test_add_delta_capability_is_last_writer_wins() -> None:
    a = ProgressionDelta(capability="fly")
    b = ProgressionDelta(capability="swim")
    assert add_delta(a, b).capability == "swim"
    assert add_delta(a, ProgressionDelta()).capability == "fly"  # b carries none -> keep a


def test_scale_delta_scales_numbers_and_leaves_capability() -> None:
    d = ProgressionDelta(global_xp=1, game_xp=2, currency=3, capability="fly")
    assert scale_delta(d, 4) == ProgressionDelta(global_xp=4, game_xp=8, currency=12, capability="fly")
    assert scale_delta(d, 0) == ProgressionDelta(capability="fly")


def test_add_delta_is_pure_no_mutation_of_inputs() -> None:
    a = ProgressionDelta(global_xp=1)
    b = ProgressionDelta(global_xp=2)
    add_delta(a, b)
    assert a == ProgressionDelta(global_xp=1) and b == ProgressionDelta(global_xp=2)


# --- Grant algebra --------------------------------------------------------


def test_empty_grant_is_the_identity_for_merge() -> None:
    assert empty_grant() is EMPTY_GRANT
    g = Grant(items=(Stack("ore.diamond", 3),), progression=ProgressionDelta(game_xp=5))
    assert merge_grants(EMPTY_GRANT, g) == g
    assert merge_grants(g, EMPTY_GRANT) == g


def test_merge_grants_concatenates_items_and_sums_progression() -> None:
    g1 = Grant(items=(Stack("ore.diamond", 3),), progression=ProgressionDelta(game_xp=5))
    g2 = Grant(items=(Stack("fish.bass", 1),), progression=ProgressionDelta(game_xp=2, currency=7))
    merged = merge_grants(g1, g2)
    assert merged.items == (Stack("ore.diamond", 3), Stack("fish.bass", 1))
    assert merged.progression == ProgressionDelta(game_xp=7, currency=7)


def test_merge_grants_is_associative() -> None:
    g1 = Grant(items=(Stack("ore.diamond", 1),), progression=ProgressionDelta(global_xp=1))
    g2 = Grant(items=(Stack("fish.bass", 1),), progression=ProgressionDelta(currency=2, capability="fly"))
    g3 = Grant(items=(Stack("curio.idol", 1),), progression=ProgressionDelta(game_xp=3, capability="swim"))
    assert merge_grants(merge_grants(g1, g2), g3) == merge_grants(g1, merge_grants(g2, g3))


def test_grant_expresses_the_six_shapes_via_stacks_and_progression() -> None:
    # design doc §2c: one Grant subsumes every current reward shape.
    mining_reward = Grant(items=(Stack("ore.diamond", 5),))
    explore_loss = Grant(items=(Stack("ore.iron", -1),))
    caught_fish = Grant(items=(Stack("fish.legend_carp", 1, {"size": 74}),))
    quest_bundle = Grant(progression=ProgressionDelta(global_xp=10, currency=3, capability="fly"))
    assert mining_reward.items[0].qty == 5
    assert explore_loss.items[0].qty == -1
    assert caught_fish.items[0].attrs["size"] == 74
    assert quest_bundle.progression.capability == "fly"
