"""skills (forced specialization) + character merge (additive-safety)."""

from __future__ import annotations

from games.mining.core import character, skills
from games.mining.core.equipment import EffectiveStats, compute_stats


def test_forced_specialization_cap_relation() -> None:
    # 20 < 4 * 10 = 40 ⇒ a maxed player cannot fill every branch.
    assert skills.SOFT_TOTAL_CAP < len(skills.BRANCHES) * skills.PER_BRANCH_CAP
    assert skills.PER_BRANCH_CAP == 10
    assert skills.SOFT_TOTAL_CAP == 20
    assert skills.BRANCHES == ("mining", "combat", "fortune", "crafting")


def test_branch_stats_mappings_preserved() -> None:
    assert skills.branch_stats("mining", 5) == EffectiveStats(mining_power=5)
    assert skills.branch_stats("combat", 5) == EffectiveStats(damage=2, max_health=10)
    assert skills.branch_stats("fortune", 5) == EffectiveStats(luck=5, loot_bonus=2)
    assert skills.branch_stats("crafting", 5) == EffectiveStats(loot_bonus=5)


def test_branch_stats_nonpositive_and_unknown_are_zero() -> None:
    assert skills.branch_stats("mining", 0) == EffectiveStats()
    assert skills.branch_stats("mining", -3) == EffectiveStats()
    assert skills.branch_stats("nope", 5) == EffectiveStats()


def test_skill_stats_additive_safety_empty_alloc_is_zero() -> None:
    assert skills.skill_stats({}) == EffectiveStats()


def test_skill_stats_sums_branches() -> None:
    total = skills.skill_stats({"mining": 4, "fortune": 6})
    assert total == EffectiveStats(mining_power=4, luck=6, loot_bonus=3)


def test_character_stats_empty_alloc_is_byte_identical_to_gear_only() -> None:
    equipped = {"tool": "diamond pickaxe", "light": "lantern"}
    gear_only = compute_stats(equipped)
    assert character.character_stats(equipped, None) == gear_only
    assert character.character_stats(equipped, {}) == gear_only


def test_character_stats_adds_skills_on_top_of_gear() -> None:
    equipped = {"tool": "pickaxe"}  # mining_power 2
    combined = character.character_stats(equipped, {"mining": 3})
    assert combined.mining_power == 5  # 2 gear + 3 skill
