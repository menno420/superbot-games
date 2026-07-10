"""rewards: ore-weight/depth reweighting + mine-roll math (preserved verbatim)."""

from __future__ import annotations

import random

from games.mining.core import rewards


def test_surface_ore_weights_are_the_base_table() -> None:
    # depth 0 must be byte-identical to the base weights (the additive baseline).
    assert rewards.ore_weights_for_depth(0) == rewards.ORE_WEIGHTS
    assert rewards.ore_weights_for_depth(0) == {
        "stone": 3,
        "bronze": 2.5,
        "iron": 2,
        "silver": 1.5,
        "gold": 1,
        "diamond": 0.5,
    }


def test_depth_reweights_toward_precious_ore() -> None:
    w1 = rewards.ore_weights_for_depth(1)
    assert w1 == {
        "stone": 2.0,  # max(0.5, 3 - 1)
        "bronze": 2.0,  # max(0.5, 2.5 - 0.5)
        "iron": 2.5,  # 2 + 0.5
        "silver": 2.0,  # 1.5 + 0.5
        "gold": 1.5,  # 1 + 0.5
        "diamond": 1.0,  # 0.5 + 0.5
    }


def test_deep_bands_floor_common_ore_at_half() -> None:
    w = rewards.ore_weights_for_depth(10)
    assert w["stone"] == 0.5  # floored
    assert w["bronze"] == 0.5  # floored
    assert w["iron"] == 7.0
    assert w["silver"] == 6.5
    assert w["gold"] == 6.0
    assert w["diamond"] == 5.5


def test_negative_depth_clamped_to_surface() -> None:
    assert rewards.ore_weights_for_depth(-5) == rewards.ore_weights_for_depth(0)


def test_mine_multiplier_constants_preserved() -> None:
    assert rewards.TOOL_POWER_GAIN == 0.0625
    assert rewards.LEGACY_PICKAXE_MULT == 1.125
    assert rewards.BASE_ROLL_MAX == 2


def test_mine_multiplier_equipped_tool_vs_legacy() -> None:
    # equipped pickaxe (mining_power 2) → 1 + 2*0.0625 = 1.125
    assert rewards.mine_multiplier({"tool": "pickaxe"}, {}) == 1.125
    # equipped diamond pickaxe (mining_power 8) → 1 + 8*0.0625 = 1.5
    assert rewards.mine_multiplier({"tool": "diamond pickaxe"}, {}) == 1.5
    # no tool, but a pickaxe in inventory → the matched legacy bonus
    assert rewards.mine_multiplier({}, {"pickaxe": 1}) == 1.125
    # nothing → 1.0
    assert rewards.mine_multiplier({}, {}) == 1.0


def test_roll_mine_loot_is_rng_deterministic() -> None:
    a = rewards.roll_mine_loot(has_pickaxe=True, depth=2, rng=random.Random(42))
    b = rewards.roll_mine_loot(has_pickaxe=True, depth=2, rng=random.Random(42))
    assert a == b


def test_roll_mine_loot_bounds_and_rounding() -> None:
    for seed in range(200):
        found, amount = rewards.roll_mine_loot(
            has_pickaxe=False, depth=0, rng=random.Random(seed)
        )
        assert found in rewards.ORE_WEIGHTS
        assert amount >= 1
        # base roll is randint(1,2); no multiplier → amount is 1 or 2.
        assert amount in (1, 2)


def test_roll_mine_loot_explicit_multiplier_rounds_never_below_one() -> None:
    # multiplier 0.0 must still floor the amount at 1 (max(1, round(...))).
    _, amount = rewards.roll_mine_loot(
        has_pickaxe=True, multiplier=0.0, rng=random.Random(1)
    )
    assert amount == 1


def test_roll_harvest_amount_axe_doubles_range() -> None:
    for seed in range(100):
        no_axe = rewards.roll_harvest_amount(has_axe=False, rng=random.Random(seed))
        assert 1 <= no_axe <= 3
        axe = rewards.roll_harvest_amount(has_axe=True, rng=random.Random(seed))
        assert axe == no_axe * 2
