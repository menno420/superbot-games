"""No pay-to-win — ``fishing_power`` BIASES the catch, it never GATES access (Q-0039/Q-0190).

A zero-gear angler still catches across the common range and can even land the rare tail;
earned gear only shifts the distribution toward bigger/rarer fish and quickens bites — and
the gear stats stay within the sim-pinned caps. The resolver exposes no coin/spend lever.
"""

from __future__ import annotations

import inspect

from games.fishing.core import catch, species
from games.mining.core import equipment


def _dist(stats: equipment.EffectiveStats, n: int = 3000) -> dict[str, int]:
    counts: dict[str, int] = {}
    for s in range(n):
        o = catch.resolve_cast(s, "dock", stats)
        if o.bit and o.catch is not None:
            counts[o.catch.species_id] = counts.get(o.catch.species_id, 0) + 1
    return counts


def test_zero_gear_catches_across_the_common_range() -> None:
    # A bare angler (no stats) still lands the common species in quantity — access is
    # never gated behind gear.
    fresh = _dist(equipment.EffectiveStats())
    assert fresh.get("minnow", 0) > 0
    assert fresh.get("bass", 0) > 0
    # …and the rare tail is still *reachable* bare-handed (biased-down, never locked out).
    assert fresh.get("pike", 0) > 0
    assert fresh.get("legend_carp", 0) > 0


def test_fishing_power_biases_toward_the_rare_tail() -> None:
    # More earned fishing_power raises the rare-tail share of catches — a bias, not a gate.
    rare = tuple(s.species_id for s in species.all_species() if s.size_rank >= 3)

    def rare_share(counts: dict[str, int]) -> float:
        total = sum(counts.values())
        return sum(counts.get(r, 0) for r in rare) / total if total else 0.0

    fresh = _dist(equipment.EffectiveStats())
    master = _dist(equipment.compute_stats({equipment.CHARM: "master angler charm"}))
    assert rare_share(master) > rare_share(fresh)
    # But the common species are never eliminated — minnow/bass stay reachable even maxed.
    assert master.get("minnow", 0) > 0
    assert master.get("bass", 0) > 0


def test_bite_luck_raises_bite_chance_without_guaranteeing_it() -> None:
    def bite_rate(stats: equipment.EffectiveStats, n: int = 3000) -> float:
        bites = sum(1 for s in range(n) if catch.resolve_cast(s, "dock", stats).bit)
        return bites / n

    fresh = bite_rate(equipment.EffectiveStats())
    master = bite_rate(equipment.compute_stats({equipment.CHARM: "master angler charm"}))
    assert 0.0 < fresh < master  # zero-gear still bites; gear quickens it
    assert master < 1.0  # never a guaranteed bite (honest variance)


def test_fishing_stats_cannot_exceed_the_sim_pinned_caps() -> None:
    # The best fishing loadout (single master angler charm) is the ceiling the caps pin —
    # no gear combination can push fishing past the sim's bounds.
    best_fp = 0
    best_bl = 0
    for name in equipment.gear_names():
        st = equipment.item_stats(name)
        best_fp = max(best_fp, st.fishing_power)
        best_bl = max(best_bl, st.bite_luck)
    assert best_fp == catch.MAX_FISHING_POWER
    assert best_bl == catch.MAX_BITE_LUCK
    # And an equipped-best player lands exactly at the cap (fishing gear is single-slot).
    maxed = equipment.compute_stats({equipment.CHARM: "master angler charm"})
    assert maxed.fishing_power == catch.MAX_FISHING_POWER
    assert maxed.bite_luck == catch.MAX_BITE_LUCK


def test_resolver_exposes_no_spend_or_purchase_lever() -> None:
    forbidden = ("coin", "cost", "pay", "purchase", "spend", "premium", "price", "buy", "gem")
    params = set(inspect.signature(catch.resolve_cast).parameters)
    assert not any(bad in p for p in params for bad in forbidden), params
    # The only advantage lever is the earned EffectiveStats block.
    assert "stats" in params
