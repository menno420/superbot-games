"""Catch-model simulation — pins the fishing balance numbers.

Pure + seeded: runs :func:`games.fishing.core.catch.resolve_cast` over a large,
reproducible sweep of ``(seed, spot_id)`` casts × representative gear tiers and aggregates
the outcomes — bite rate, the per-species catch distribution, mean caught size, and the
energy economy — per tier. Every balance constant in ``catch.py`` is justified by this
harness's output; the numbers + pinned bounds are pasted into
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

from games.fishing.core import catch, species
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

# Spots the sweep casts at (spot id only feeds the deterministic seed; the resolver is
# spot-agnostic beyond that, so these just widen the sample).
_SPOTS: tuple[str, ...] = ("dock", "deep_lake", "reef", "river_bend")


def tier_stats() -> dict[str, equipment.EffectiveStats]:
    """The representative tiers as :class:`EffectiveStats` (order: fresh→master)."""
    return {name: equipment.compute_stats(eq) for name, eq in _TIER_LOADOUTS.items()}


@dataclass
class CatchTierStats:
    """Aggregated cast outcomes for one gear tier."""

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


@dataclass
class SimReport:
    casts_per_tier: int = 0
    by_tier: dict[str, CatchTierStats] = field(default_factory=dict)
    energy_cost_total: int = 0
    energy_cost_n: int = 0

    @property
    def mean_energy_cost(self) -> float:
        return self.energy_cost_total / self.energy_cost_n if self.energy_cost_n else 0.0


# The rare/big tail (size_rank ≥ 3) — read off the species data, not hard-coded.
def _rare_ids() -> tuple[str, ...]:
    return tuple(s.species_id for s in species.all_species() if s.size_rank >= 3)


def run(
    *,
    seeds: range = range(400),
    spots: tuple[str, ...] = _SPOTS,
    casts_per_spot: int = 40,
) -> SimReport:
    """Sweep casts × gear tiers and aggregate the catch distribution.

    Deterministic: each cast injects ``random.Random(hash-free seed from (seed, spot, i))``
    so the whole sweep is a pure function of its bounds (the same tier faces the same cast
    stream — an apples-to-apples comparison across gear). Bite rate, species distribution,
    mean size and the energy economy are measured per tier.
    """
    tiers = tier_stats()
    report = SimReport()
    report.by_tier = {name: CatchTierStats() for name in tiers}

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
                    bucket = report.by_tier[name]
                    bucket.casts += 1
                    report.energy_cost_total += out.energy_cost
                    report.energy_cost_n += 1
                    if out.bit and out.catch is not None:
                        bucket.bites += 1
                        bucket.species_counts[out.catch.species_id] += 1
                        bucket.size_total += out.catch.size

    report.casts_per_tier = next(iter(report.by_tier.values())).casts
    return report


def format_report(report: SimReport) -> str:
    rare = _rare_ids()
    ids = species.species_ids()
    lines: list[str] = []
    lines.append(f"casts per tier: {report.casts_per_tier:,}")
    lines.append(f"species table: {', '.join(ids)}")
    lines.append(f"rare tail (size_rank ≥ 3): {', '.join(rare)}")
    lines.append("")
    lines.append("per-tier outcomes (bite rate · rare-tail share of bites · mean size):")
    for name, st in report.by_tier.items():
        lines.append(
            f"  {name:<8} bite {st.bite_rate:6.2%}  rare {st.rare_share(rare):6.2%}  "
            f"size {st.mean_size:5.1f}  (bites={st.bites:,})"
        )
    lines.append("")
    lines.append("per-tier species distribution (share of bites):")
    header = "  " + " " * 8 + "".join(f"{sid:>13}" for sid in ids)
    lines.append(header)
    for name, st in report.by_tier.items():
        row = "".join(f"{st.species_share(sid):>13.2%}" for sid in ids)
        lines.append(f"  {name:<8}{row}")
    lines.append("")
    lines.append(f"mean energy cost per cast: {report.mean_energy_cost:.2f}")
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    print(format_report(run()))
