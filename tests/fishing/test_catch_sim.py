"""Sim-pinned distributions — re-assert the catch bounds over a smaller, fast sweep.

The pinned bounds below mirror ``docs/design/fishing-catch-skeleton.md`` §5 (full-scale
evidence lives there). For a walking skeleton the bounds are pinned from this slice's sim
run and are **trivially wide** — they exist to redden CI on a balance regression, and
tighten as species/gear grow. Mirrors ``tests/mining/test_encounters.py``'s sim-pin test.
"""

from __future__ import annotations

from games.fishing.core import catch, species
from games.fishing.sim import catch_sim as sim

# --- pinned bounds (see the design doc's sim-pin table; trivially wide for a skeleton) ---
_FRESH_BITE = (0.48, 0.62)  # base bite chance, no gear
_MASTER_BITE = (0.70, 0.88)  # bite_luck-raised, capped below 1.0
_RARE = tuple(s.species_id for s in species.all_species() if s.size_rank >= 3)


def _run() -> sim.SimReport:
    # A smaller, fast sweep than the __main__ default; still enough for stable bounds.
    return sim.run(seeds=range(80), casts_per_spot=20)


def test_bite_rate_gradient_is_monotone_and_bounded() -> None:
    report = _run()
    fresh = report.by_tier["fresh"]
    geared = report.by_tier["geared"]
    master = report.by_tier["master"]
    # bite_luck strictly quickens bites across the gear ladder…
    assert fresh.bite_rate < geared.bite_rate < master.bite_rate
    # …within the pinned bands (and never a guaranteed bite).
    assert _FRESH_BITE[0] <= fresh.bite_rate <= _FRESH_BITE[1]
    assert _MASTER_BITE[0] <= master.bite_rate <= _MASTER_BITE[1]
    assert master.bite_rate < 1.0


def test_rare_tail_share_rises_with_fishing_power() -> None:
    report = _run()
    fresh = report.by_tier["fresh"].rare_share(_RARE)
    geared = report.by_tier["geared"].rare_share(_RARE)
    master = report.by_tier["master"].rare_share(_RARE)
    # fishing_power biases toward the big/rare tail, monotone across the ladder.
    assert fresh < geared < master
    # …but never dominates — the common species still hold the majority of bites.
    assert master < 0.45


def test_common_species_stay_reachable_at_every_tier() -> None:
    report = _run()
    for name, st in report.by_tier.items():
        # Fair access: minnow + bass are landed at every tier (gear biases, never gates).
        assert st.species_counts.get("minnow", 0) > 0, name
        assert st.species_counts.get("bass", 0) > 0, name
    # And a bare angler still reaches the whole table over the sweep.
    fresh = report.by_tier["fresh"].species_counts
    assert set(fresh) == set(species.species_ids())


def test_mean_size_grows_with_gear() -> None:
    report = _run()
    sizes = [report.by_tier[t].mean_size for t in ("fresh", "geared", "master")]
    assert sizes[0] <= sizes[1] <= sizes[2]


def test_energy_cost_per_cast_is_the_cast_cost() -> None:
    from games.fishing.core import catch

    report = _run()
    assert report.mean_energy_cost == float(catch.CAST_COST)


def test_sim_report_is_deterministic() -> None:
    kw = dict(seeds=range(20), casts_per_spot=10)
    a = sim.run(**kw)
    b = sim.run(**kw)
    for name in a.by_tier:
        assert a.by_tier[name].species_counts == b.by_tier[name].species_counts
        assert a.by_tier[name].bites == b.by_tier[name].bites
    for key in a.by_spot_tier:
        assert a.by_spot_tier[key].species_counts == b.by_spot_tier[key].species_counts


# --- per-spot (biome) sim-pins ----------------------------------------------
# Pinned from this slice's sim run (see docs/design/fishing-catch-skeleton.md §5). Honest,
# not trivially wide: the spot biomes give a clear, ordered gradient. Bands carry enough
# margin to absorb the small-sweep sampling noise but would redden on a real profile change.

# Per-spot fresh (zero-gear) bite-rate bands — the tide pool bites readily, deep water is
# stingy (but always well above the honest MIN_BITE_CHANCE floor).
_FRESH_BITE_BY_SPOT = {
    "tide_pool": (0.60, 0.72),
    "dock": (0.48, 0.60),
    "deep_water": (0.40, 0.52),
}
# Per-spot fresh rare-tail share bands — deep water is a rare-tail biome, the tide pool is not.
_FRESH_RARE_BY_SPOT = {
    "tide_pool": (0.03, 0.13),
    "dock": (0.15, 0.27),
    "deep_water": (0.34, 0.48),
}


def test_bite_rate_gradient_across_spots_at_zero_gear() -> None:
    report = _run()
    fresh = {s: report.spot_tier(s, "fresh").bite_rate for s in report.spots}
    # The spot bite_bias orders the biomes: shallow calm > neutral dock > cold deep water.
    assert fresh["tide_pool"] > fresh["dock"] > fresh["deep_water"]
    for spot, (lo, hi) in _FRESH_BITE_BY_SPOT.items():
        assert lo <= fresh[spot] <= hi, (spot, fresh[spot])
    # Even the stingiest biome stays well above the honest floor (fair access, no gating).
    assert fresh["deep_water"] > catch.MIN_BITE_CHANCE


def test_rare_tail_gradient_across_spots_at_zero_gear() -> None:
    report = _run()
    rare = {s: report.spot_tier(s, "fresh").rare_share(_RARE) for s in report.spots}
    # The spot weight profiles order the rare-tail share: deep water >> dock >> tide pool.
    assert rare["deep_water"] > rare["dock"] > rare["tide_pool"]
    for spot, (lo, hi) in _FRESH_RARE_BY_SPOT.items():
        assert lo <= rare[spot] <= hi, (spot, rare[spot])


def test_mean_size_gradient_across_spots_at_zero_gear() -> None:
    report = _run()
    size = {s: report.spot_tier(s, "fresh").mean_size for s in report.spots}
    # Bigger fish live in deeper water — the size gradient follows the rare-tail gradient.
    assert size["deep_water"] > size["dock"] > size["tide_pool"]


def test_gear_gradient_holds_within_every_spot() -> None:
    report = _run()
    for spot in report.spots:
        fresh = report.spot_tier(spot, "fresh")
        geared = report.spot_tier(spot, "geared")
        master = report.spot_tier(spot, "master")
        # Within each biome, gear still quickens bites and biases toward the rare tail…
        assert fresh.bite_rate < geared.bite_rate < master.bite_rate, spot
        assert fresh.rare_share(_RARE) < geared.rare_share(_RARE) < master.rare_share(_RARE), spot
        # …and a bite is never guaranteed even at the calmest biome, best gear.
        assert master.bite_rate < 1.0, spot


def test_fair_access_at_every_spot_and_tier() -> None:
    report = _run()
    for (spot, tier), st in report.by_spot_tier.items():
        # The common minnow and the legendary carp are BOTH landed at every (spot, tier) —
        # no biome and no gear tier gates a species out of reach.
        assert st.species_counts.get("minnow", 0) > 0, (spot, tier)
        assert st.species_counts.get("legend_carp", 0) > 0, (spot, tier)
