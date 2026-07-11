"""Catch-model simulation — pins the fishing balance numbers **per spot biome**.

Pure + seeded: runs :func:`games.fishing.core.catch.resolve_cast` over a large,
reproducible sweep of ``(seed, spot_id)`` casts × representative gear tiers and aggregates
the outcomes — bite rate, the per-species catch distribution, mean caught size, and the
energy economy — **per (spot, tier)** and in aggregate across spots. Every balance constant
in ``catch.py`` and every spot profile in ``spots.py`` is justified by this harness's
output; the numbers + pinned bounds are pasted into
``docs/design/fishing-catch-skeleton.md`` §5. The default deterministic stream (``rng=None``
would fix every cast to one value, so the sweep instead **injects** a per-cast
``random.Random`` seeded from ``(seed, spot, i)``) makes the whole sweep a pure function of
its inputs — the same call always yields the same report, and the matching fast test
(``tests/fishing/test_catch_sim.py``) re-asserts the bounds over a smaller subset.

Run it:  ``python3 -m games.fishing.sim.catch_sim``
"""

from __future__ import annotations

import random
from collections import Counter
from dataclasses import dataclass, field

from games.fishing.core import catch, species, spots
from games.mining.core import equipment

# Representative earned-gear tiers, built through the real equipment model (so the stats
# are exactly what a player who earned that fishing gear in-domain would have — no invented
# numbers, nothing purchasable-for-power). "fresh" is the bare baseline; the others equip
# one CHARM-slot fishing charm each (fishing gear is a single-slot ladder).
_TIER_LOADOUTS: dict[str, dict[str, str]] = {
    "fresh": {},
    "geared": {equipment.CHARM: "fishing charm"},        # fishing_power 2 / bite_luck 1
    "master": {equipment.CHARM: "master angler charm"},  # fishing_power 6 / bite_luck 3
}

# The spot biomes the sweep casts at — the real spots.py table ids (each carries its own
# catch profile now, so the spot is a first-class sweep dimension, not just seed entropy).
_SPOTS: tuple[str, ...] = spots.spot_ids()


def tier_stats() -> dict[str, equipment.EffectiveStats]:
    """The representative tiers as :class:`EffectiveStats` (order: fresh→master)."""
    return {name: equipment.compute_stats(eq) for name, eq in _TIER_LOADOUTS.items()}


@dataclass
class CatchTierStats:
    """Aggregated cast outcomes for one (spot, tier) — or one tier across spots."""

    casts: int = 0
    bites: int = 0
    species_counts: Counter[str] = field(default_factory=Counter)
    size_total: int = 0

    @property
    def bite_rate(self) -> float:
        return self.bites / self.casts if self.casts else 0.0

    @property
    def mean_size(self) -> float:
        return self.size_total / self.bites if self.bites else 0.0

    def species_share(self, species_id: str) -> float:
        return self.species_counts.get(species_id, 0) / self.bites if self.bites else 0.0

    def rare_share(self, rare_ids: tuple[str, ...]) -> float:
        """Share of bites that landed one of *rare_ids* (the big/rare tail)."""
        rare = sum(self.species_counts.get(r, 0) for r in rare_ids)
        return rare / self.bites if self.bites else 0.0

    def record(self, out: catch.CastOutcome) -> None:
        """Fold one resolved cast into this bucket."""
        self.casts += 1
        if out.bit and out.catch is not None:
            self.bites += 1
            self.species_counts[out.catch.species_id] += 1
            self.size_total += out.catch.size


@dataclass
class SimReport:
    casts_per_tier: int = 0
    spots: tuple[str, ...] = ()
    tiers: tuple[str, ...] = ()
    # Per (spot, tier) buckets — the spot-biome evidence the design doc §5 pins.
    by_spot_tier: dict[tuple[str, str], CatchTierStats] = field(default_factory=dict)
    # Per-tier aggregate across spots (kept for the whole-economy view).
    by_tier: dict[str, CatchTierStats] = field(default_factory=dict)
    energy_cost_total: int = 0
    energy_cost_n: int = 0

    @property
    def mean_energy_cost(self) -> float:
        return self.energy_cost_total / self.energy_cost_n if self.energy_cost_n else 0.0

    def spot_tier(self, spot: str, tier: str) -> CatchTierStats:
        """The bucket for one (spot, tier)."""
        return self.by_spot_tier[(spot, tier)]


# The rare/big tail (size_rank ≥ 3) — read off the species data, not hard-coded.
def _rare_ids() -> tuple[str, ...]:
    return tuple(s.species_id for s in species.all_species() if s.size_rank >= 3)


def run(
    *,
    seeds: range = range(400),
    spots: tuple[str, ...] = _SPOTS,
    casts_per_spot: int = 40,
) -> SimReport:
    """Sweep casts × spots × gear tiers and aggregate the catch distribution per (spot, tier).

    Deterministic: each cast injects ``random.Random(hash-free seed from (seed, spot, i))``
    so the whole sweep is a pure function of its bounds (the same tier faces the same cast
    stream at a given spot — an apples-to-apples comparison across gear). Bite rate, species
    distribution, mean size and the energy economy are measured per (spot, tier) and per
    tier overall.
    """
    tiers = tier_stats()
    report = SimReport()
    report.spots = tuple(spots)
    report.tiers = tuple(tiers)
    report.by_tier = {name: CatchTierStats() for name in tiers}
    report.by_spot_tier = {
        (spot, name): CatchTierStats() for spot in spots for name in tiers
    }

    for seed in seeds:
        for spot in spots:
            for i in range(casts_per_spot):
                # A per-cast stream shared across tiers (same rolls face each tier), derived
                # deterministically from the fishing seed helper so the sweep is reproducible.
                base = catch.fishing_seed(seed, f"{spot}:{i}")
                for name, stats in tiers.items():
                    out = catch.resolve_cast(
                        seed, spot, stats, rng=random.Random(base)
                    )
                    report.energy_cost_total += out.energy_cost
                    report.energy_cost_n += 1
                    report.by_spot_tier[(spot, name)].record(out)
                    report.by_tier[name].record(out)

    report.casts_per_tier = next(iter(report.by_tier.values())).casts
    return report


def format_report(report: SimReport) -> str:
    rare = _rare_ids()
    ids = species.species_ids()
    lines: list[str] = []
    lines.append(f"casts per tier: {report.casts_per_tier:,}")
    lines.append(f"spots: {', '.join(report.spots)}")
    lines.append(f"species table: {', '.join(ids)}")
    lines.append(f"rare tail (size_rank ≥ 3): {', '.join(rare)}")
    lines.append("")

    # Per-spot × tier: bite rate · rare-tail share · mean size — the spot-biome evidence.
    for spot in report.spots:
        lines.append(f"[{spot}] (bite rate · rare-tail share of bites · mean size):")
        for name in report.tiers:
            st = report.spot_tier(spot, name)
            lines.append(
                f"  {name:<8} bite {st.bite_rate:6.2%}  rare {st.rare_share(rare):6.2%}  "
                f"size {st.mean_size:5.1f}  (bites={st.bites:,})"
            )
        header = "    " + " " * 6 + "".join(f"{sid:>13}" for sid in ids)
        lines.append("    species share of bites:")
        lines.append(header)
        for name in report.tiers:
            st = report.spot_tier(spot, name)
            row = "".join(f"{st.species_share(sid):>13.2%}" for sid in ids)
            lines.append(f"    {name:<8}{row}")
        lines.append("")

    # Cross-spot aggregate per tier (the whole-economy view).
    lines.append("aggregate across spots (bite rate · rare-tail share · mean size):")
    for name in report.tiers:
        st = report.by_tier[name]
        lines.append(
            f"  {name:<8} bite {st.bite_rate:6.2%}  rare {st.rare_share(rare):6.2%}  "
            f"size {st.mean_size:5.1f}  (bites={st.bites:,})"
        )
    lines.append("")
    lines.append(f"mean energy cost per cast: {report.mean_energy_cost:.2f}")
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    print(format_report(run()))
