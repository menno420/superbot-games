"""exploration + world: additive-safety (luck/depth_access zero = baseline)."""

from __future__ import annotations

import random

from games.mining.core import exploration as exp
from games.mining.core import world
from games.mining.core.equipment import EffectiveStats


def test_luck_weighting_byte_identical_at_zero_luck() -> None:
    candidates = list(exp.CATALOG)
    base = [o.weight for o in candidates]
    assert exp._luck_weighted(candidates, 0) == base
    assert exp._luck_weighted(candidates, -3) == base  # non-positive luck = base


def test_luck_lifts_rarer_finds_only() -> None:
    rare = exp.ExploreOutcome("r", "", "diamond", 1, rarity=exp.Rarity.RARE, weight=1.0)
    common = exp.ExploreOutcome("c", "", "wood", 1, rarity=exp.Rarity.COMMON, weight=1.0)
    w = exp._luck_weighted([rare, common], luck=1)
    assert w[0] == 1.0 * (1 + 1 * 0.4)  # rare boosted
    assert w[1] == 1.0  # common unchanged


def test_eligible_outcomes_respect_depth_and_requires() -> None:
    surface = exp.eligible_outcomes(exp.Biome.SURFACE, exp.Loadout())
    keys = {o.key for o in surface}
    assert "hidden_diamond_vein" not in keys  # needs CAVERN + torch
    assert "abandoned_camp" in keys
    # torch at cavern unlocks the torch-gated vein.
    with_torch = exp.eligible_outcomes(
        exp.Biome.CAVERN, exp.Loadout(tools=frozenset({exp.TORCH}))
    )
    assert "hidden_diamond_vein" in {o.key for o in with_torch}


def test_resolve_is_deterministic_with_injected_rng() -> None:
    a = exp.resolve(exp.Biome.SURFACE, exp.Loadout(), rng=random.Random(3))
    b = exp.resolve(exp.Biome.SURFACE, exp.Loadout(), rng=random.Random(3))
    assert a.narration == b.narration and a.outcome.key == b.outcome.key


def test_scale_amount_penalties_never_amplified() -> None:
    hazard = exp.ExploreOutcome("h", "lost {amount} stone", "stone", -2)
    strong = EffectiveStats(mining_power=8, loot_bonus=5)
    assert exp._scale_amount(hazard, strong) == -2  # penalty untouched


def test_world_depth_access_gating_additive_safety() -> None:
    # zero depth_access → only the surface is reachable (baseline).
    zero = EffectiveStats()
    assert world.max_accessible_depth(zero) == 0
    assert world.can_descend(0, zero) is False
    # diamond-lantern-level access (3) reaches the deepest band (MAGMA).
    magma = EffectiveStats(depth_access=3)
    assert world.max_accessible_depth(magma) == world.MAX_DEPTH == 3
    assert world.descend(0, magma) == 1
    assert world.descend(2, magma) == 3


def test_world_ascend_never_above_surface() -> None:
    assert world.ascend(0) == 0
    assert world.ascend(2) == 1
