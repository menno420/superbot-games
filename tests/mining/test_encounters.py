"""Grid-encounters: determinism, additive-safety, no-pay-to-win, and the
sim-pinned outcome distributions.

The pinned bounds below mirror ``docs/design/mining-grid-encounters.md`` §"Sim-pin
table"; the full-scale evidence lives there. This test re-asserts them over a
smaller fixed sweep so a balance regression reddens CI.
"""

from __future__ import annotations

import inspect
import subprocess
import sys

from games.mining.core import encounters, equipment, grid
from games.mining.sim import encounters_sim as sim

# --- pinned bounds (see the design doc's sim-pin table) ----------------------
_ENCOUNTER_RATE = (0.08, 0.15)  # sparse: ~8–15% of actions trigger anything
_MIN_NONE_SHARE = 0.85  # the baseline dominates
_HAZARD_MAX_SHARE = encounters.HAZARD_MAX_CHANCE  # per-depth hazard share ceiling
_LOOT_CACHE_MEAN = (7.0, 12.0)
_RICH_VEIN_MEAN = (4.0, 8.0)
_HAZARD_LOOT_MEAN = (1.5, 3.5)


def _hazard_cell() -> grid.Cell:
    """A guaranteed-NORMAL cell (so a hazard can fire) at a mid depth."""
    return grid.Cell(0, 0, 8, grid.CellFeature.NORMAL, "iron", 1.0)


# ---------------------------------------------------------------------------
# Determinism — (seed, x, y, z) → the same encounter (matches grid.py).
# ---------------------------------------------------------------------------
def test_resolve_is_deterministic_within_process() -> None:
    cell = grid.cell_at(12345, 3, -7, 5)
    a = encounters.resolve(12345, cell)
    b = encounters.resolve(12345, cell)
    assert a == b
    assert isinstance(a, encounters.EncounterOutcome)
    assert a.kind in encounters.EncounterKind


def test_resolve_process_independent() -> None:
    # A fresh interpreter (PYTHONHASHSEED randomised) must produce the identical
    # outcome — proving the encounter seed never uses str-hashing (splitmix64).
    inproc = encounters.resolve_at(999, -4, 8, 12)
    code = (
        "from games.mining.core import encounters;"
        "o = encounters.resolve_at(999, -4, 8, 12);"
        "print(f'{o.kind.value}|{o.resolution.value}|{o.damage_taken}|"
        "{o.energy_cost}|{tuple((r.item, r.amount) for r in o.rewards)}')"
    )
    out = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=True,
        cwd=_repo_root(),
    ).stdout.strip()
    expected = (
        f"{inproc.kind.value}|{inproc.resolution.value}|{inproc.damage_taken}|"
        f"{inproc.energy_cost}|{tuple((r.item, r.amount) for r in inproc.rewards)}"
    )
    assert out == expected


def test_injected_rng_overrides_default_stream() -> None:
    # A host injecting its own rng (the live-roll path) drives the outcome: over
    # many streams the *same* cell yields a spread of results, proving the roll is
    # rng-driven rather than fixed to the deterministic default.
    import random

    cell = _hazard_cell()
    outs = {
        (o.kind, o.resolution, o.damage_taken)
        for s in range(60)
        for o in [encounters.resolve(1, cell, rng=random.Random(s))]
    }
    assert len(outs) > 1


# ---------------------------------------------------------------------------
# Additive-safety — the baseline is stat-independent; stats only ever help.
# ---------------------------------------------------------------------------
def test_barren_cell_is_the_stat_independent_baseline() -> None:
    barren = grid.Cell(0, 0, 0, grid.CellFeature.BARREN, "stone", 0.5)
    baseline = encounters.resolve(1, barren)
    loaded = encounters.resolve(
        1,
        barren,
        equipment.EffectiveStats(damage=50, defense=50, max_health=200, luck=9, loot_bonus=9),
    )
    assert baseline.kind is encounters.EncounterKind.NONE
    assert baseline == loaded  # stats cannot manufacture an encounter


def test_untriggered_action_returns_byte_identical_none() -> None:
    # Every NONE outcome is the one shared invariant object (no per-call variance).
    seen = {
        id(encounters.resolve_at(7, x, 0, 0))
        for x in range(200)
        if encounters.resolve_at(7, x, 0, 0).kind is encounters.EncounterKind.NONE
    }
    assert len(seen) == 1


def test_stats_are_monotone_improvements_on_hazards() -> None:
    """More earned stats never worsen a hazard: damage taken is non-increasing and
    a win is never lost, cell-for-cell (the additive-safety property for combat)."""
    fresh = equipment.EffectiveStats()
    geared = equipment.compute_stats(sim._TIER_LOADOUTS["geared"])
    veteran = equipment.compute_stats(sim._TIER_LOADOUTS["veteran"])
    checked = 0
    for seed in range(12):
        for x in range(-20, 20):
            for y in (-5, 0, 5):
                cell = grid.cell_at(seed, x, y, 8)
                if cell.feature is not grid.CellFeature.NORMAL:
                    continue
                f = encounters.resolve(seed, cell, fresh)
                if f.kind is not encounters.EncounterKind.HAZARD:
                    continue
                g = encounters.resolve(seed, cell, geared)
                v = encounters.resolve(seed, cell, veteran)
                # Damage taken never increases as gear improves (same monster roll).
                assert v.damage_taken <= g.damage_taken <= f.damage_taken
                # A win is never given back by having more gear.
                won = encounters.Resolution.WON
                if f.resolution is won:
                    assert g.resolution is won and v.resolution is won
                if g.resolution is won:
                    assert v.resolution is won
                checked += 1
    assert checked > 50  # the sample actually exercised hazards


def test_loot_reward_never_shrinks_with_earned_luck() -> None:
    # A TREASURE cell's cache pays at least as much with a lucky charm (earned).
    treasure = grid.Cell(0, 0, 5, grid.CellFeature.TREASURE, "gold", 2.0)
    bare = encounters.resolve(3, treasure)
    lucky = encounters.resolve(3, treasure, equipment.EffectiveStats(luck=3, loot_bonus=2))
    assert bare.kind is encounters.EncounterKind.LOOT_CACHE
    assert lucky.rewards[0].amount >= bare.rewards[0].amount


# ---------------------------------------------------------------------------
# No pay-to-win — the resolver takes no spend/purchase lever.
# ---------------------------------------------------------------------------
def test_resolver_exposes_no_spend_or_purchase_lever() -> None:
    forbidden = ("coin", "cost", "pay", "purchase", "spend", "premium", "price", "buy", "gem")
    for fn in (encounters.resolve, encounters.resolve_at):
        params = set(inspect.signature(fn).parameters)
        assert not any(bad in p for p in params for bad in forbidden), params
    # The only advantage lever is the earned EffectiveStats block.
    assert "stats" in inspect.signature(encounters.resolve).parameters


def test_rewards_only_use_the_existing_item_vocabulary() -> None:
    # Encounters never mint a parallel currency: every reward item is a known ore
    # (the depth-weighted table) — no bespoke premium token.
    known = set(grid.ore_weights_for_depth(0)) | set(grid.ore_weights_for_depth(15))
    for seed in range(4):
        for x in range(-10, 10):
            for z in (0, 8, 15):
                out = encounters.resolve_at(seed, x, 0, z)
                for reward in out.rewards:
                    assert reward.item in known, reward.item
                    assert reward.amount >= 1


# ---------------------------------------------------------------------------
# Sim-pinned distributions — the numbers land in the documented bounds.
# ---------------------------------------------------------------------------
def test_outcome_distributions_within_pinned_bounds() -> None:
    report = sim.run(seeds=range(8), coord=range(-16, 16), depths=(0, 3, 6, 10, 15))

    # Sparse by construction.
    assert _ENCOUNTER_RATE[0] <= report.encounter_rate <= _ENCOUNTER_RATE[1]
    assert report.kind_counts["none"] / report.actions >= _MIN_NONE_SHARE

    # Deeper = more dangerous: per-depth hazard share is capped and rises overall.
    shares = {
        z: counts.get("hazard", 0) / sum(counts.values())
        for z, counts in report.depth_kind_counts.items()
    }
    assert all(s <= _HAZARD_MAX_SHARE for s in shares.values())
    assert shares[15] > shares[0]

    # Earned-gear gradient (the whole no-pay-to-win point): win rate strictly
    # improves with earned gear; a competent player is never overwhelmed.
    tier = report.hazard_by_tier
    win = {name: hz.rate(hz.won) for name, hz in tier.items()}
    assert win["veteran"] > win["geared"] > win["fresh"]
    assert tier["geared"].rate(tier["geared"].lost) <= 0.05
    assert tier["veteran"].rate(tier["veteran"].lost) <= 0.01
    assert tier["veteran"].mean_damage < tier["fresh"].mean_damage

    # Surface is survivable bare-handed; the deep is not.
    depth = report.baseline_hazard_by_depth
    assert depth[0].rate(depth[0].won) >= 0.9
    assert depth[15].rate(depth[15].won) <= 0.05
    assert depth[15].rate(depth[15].lost) >= 0.5

    # Reward yields sit in their pinned bands (baseline tier).
    def _mean(vals: list[int]) -> float:
        return sum(vals) / len(vals)

    assert _LOOT_CACHE_MEAN[0] <= _mean(report.reward_amounts["loot_cache"]) <= _LOOT_CACHE_MEAN[1]
    assert _RICH_VEIN_MEAN[0] <= _mean(report.reward_amounts["rich_vein"]) <= _RICH_VEIN_MEAN[1]
    assert _HAZARD_LOOT_MEAN[0] <= _mean(report.reward_amounts["hazard"]) <= _HAZARD_LOOT_MEAN[1]


def test_sim_report_is_deterministic() -> None:
    kw = dict(seeds=range(4), coord=range(-8, 8), depths=(0, 8, 15))
    a = sim.run(**kw)
    b = sim.run(**kw)
    assert a.kind_counts == b.kind_counts
    assert a.reward_amounts == b.reward_amounts


def _repo_root() -> str:
    import os

    # tests/mining/ -> repo root is two levels up.
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
