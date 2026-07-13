"""Encounter-model simulation — pins the grid-encounter balance numbers.

Pure + seeded: runs :func:`games.mining.core.encounters.resolve` over a large,
reproducible sweep of ``(seed, x, y, z)`` cells × representative character tiers
and aggregates the outcome distributions — encounter-kind frequency (overall and
per depth), hazard win/flee/lose rates per tier, reward-yield percentiles, mean
damage, and the energy economy.

Every balance constant in ``encounters.py`` is justified by this harness's output;
the numbers + the pinned bounds are pasted into
``docs/design/mining-grid-encounters.md``. The default deterministic encounter
stream (``rng=None``) means the whole sweep is a pure function of its inputs — the
same call always yields the same report, and the matching fast test
(``tests/mining/test_encounters.py``) re-asserts the bounds over a fixed subset.

Run it:  ``python3 -m games.mining.sim.encounters_sim``
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from games.mining.core import encounters, equipment, grid

# Representative earned-gear tiers (built through the real equipment model, so the
# stats are exactly what a player who earned that gear in-domain would have — no
# invented numbers, and nothing purchasable-for-power). "fresh" is the bare
# baseline; the others are full same-tier sets + matching tools.
_TIER_LOADOUTS: dict[str, dict[str, str]] = {
    "fresh": {},
    "geared": {
        equipment.TOOL: "iron pickaxe",
        equipment.CHARM: "lucky charm",
        equipment.WEAPON: "iron sword",
        equipment.SHIELD: "iron shield",
        equipment.HELMET: "iron helmet",
        equipment.CHESTPLATE: "iron chestplate",
        equipment.LEGGINGS: "iron leggings",
        equipment.BOOTS: "iron boots",
    },
    "veteran": {
        equipment.TOOL: "diamond pickaxe",
        equipment.CHARM: "lucky charm",
        equipment.WEAPON: "diamond sword",
        equipment.SHIELD: "diamond shield",
        equipment.HELMET: "diamond helmet",
        equipment.CHESTPLATE: "diamond chestplate",
        equipment.LEGGINGS: "diamond leggings",
        equipment.BOOTS: "diamond boots",
    },
}


def tier_stats() -> dict[str, equipment.EffectiveStats]:
    """The representative tiers as :class:`EffectiveStats` (order: fresh→veteran)."""
    return {name: equipment.compute_stats(eq) for name, eq in _TIER_LOADOUTS.items()}


@dataclass
class HazardTierStats:
    won: int = 0
    fled: int = 0
    lost: int = 0
    damage_total: int = 0

    @property
    def total(self) -> int:
        return self.won + self.fled + self.lost

    def rate(self, n: int) -> float:
        return n / self.total if self.total else 0.0

    @property
    def mean_damage(self) -> float:
        return self.damage_total / self.total if self.total else 0.0


@dataclass
class SimReport:
    actions: int = 0
    kind_counts: Counter[str] = field(default_factory=Counter)
    depth_kind_counts: dict[int, Counter[str]] = field(default_factory=dict)
    hazard_by_tier: dict[str, HazardTierStats] = field(default_factory=dict)
    # baseline-tier hazard resolution split by depth (the depth-danger gradient).
    baseline_hazard_by_depth: dict[int, HazardTierStats] = field(default_factory=dict)
    reward_amounts: dict[str, list[int]] = field(default_factory=dict)  # kind → amounts
    energy_costs: list[int] = field(default_factory=list)  # triggered encounters

    @property
    def encounter_rate(self) -> float:
        triggered = self.actions - self.kind_counts.get("none", 0)
        return triggered / self.actions if self.actions else 0.0


def _percentile(values: list[int], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    k = min(len(ordered) - 1, int(round(pct * (len(ordered) - 1))))
    return float(ordered[k])


def run(
    *,
    seeds: range = range(24),
    coord: range = range(-24, 24),
    depths: tuple[int, ...] = (0, 3, 6, 10, 15),
    baseline_tier: str = "fresh",
) -> SimReport:
    """Sweep ``(seed, x, y, z)`` cells and aggregate encounter outcomes.

    Deterministic: every encounter uses the default ``(seed, x, y, z)`` stream, so
    the sweep is a pure function of its bounds. Kind frequency, reward yields and
    the energy economy are read off the *baseline_tier* run (stat-independent
    trigger + a bare player), while hazard win/flee/lose rates are measured for
    **every** tier over the identical hazard cells (trigger is stat-independent, so
    the same monster rolls face each tier — an apples-to-apples comparison).
    """
    tiers = tier_stats()
    report = SimReport()
    report.hazard_by_tier = {name: HazardTierStats() for name in tiers}
    report.baseline_hazard_by_depth = {z: HazardTierStats() for z in depths}
    report.depth_kind_counts = {z: Counter() for z in depths}
    report.reward_amounts = {"loot_cache": [], "rich_vein": [], "hazard": []}
    base_stats = tiers[baseline_tier]

    for seed in seeds:
        for x in coord:
            for y in coord:
                for z in depths:
                    cell = grid.cell_at(seed, x, y, z)
                    # Baseline resolution drives kind/reward/energy aggregates.
                    out = encounters.resolve(seed, cell, base_stats)
                    report.actions += 1
                    report.kind_counts[out.kind.value] += 1
                    report.depth_kind_counts[z][out.kind.value] += 1
                    if out.kind is not encounters.EncounterKind.NONE:
                        report.energy_costs.append(out.energy_cost)
                    if out.kind is encounters.EncounterKind.LOOT_CACHE:
                        report.reward_amounts["loot_cache"].append(out.rewards[0].amount)
                    elif out.kind is encounters.EncounterKind.RICH_VEIN:
                        report.reward_amounts["rich_vein"].append(out.rewards[0].amount)

                    # Per-tier hazard resolution — only for hazard cells.
                    if out.kind is encounters.EncounterKind.HAZARD:
                        for name, stats in tiers.items():
                            hz = encounters.resolve(seed, cell, stats)
                            bucket = report.hazard_by_tier[name]
                            if hz.resolution is encounters.Resolution.WON:
                                bucket.won += 1
                                if name == baseline_tier and hz.rewards:
                                    report.reward_amounts["hazard"].append(hz.rewards[0].amount)
                            elif hz.resolution is encounters.Resolution.FLED:
                                bucket.fled += 1
                            elif hz.resolution is encounters.Resolution.LOST:
                                bucket.lost += 1
                            bucket.damage_total += hz.damage_taken
                            if name == baseline_tier:
                                dz = report.baseline_hazard_by_depth[z]
                                if hz.resolution is encounters.Resolution.WON:
                                    dz.won += 1
                                elif hz.resolution is encounters.Resolution.FLED:
                                    dz.fled += 1
                                else:
                                    dz.lost += 1
                                dz.damage_total += hz.damage_taken
    return report


def format_report(report: SimReport) -> str:
    lines: list[str] = []
    lines.append(f"actions sampled: {report.actions:,}")
    lines.append(f"overall encounter rate: {report.encounter_rate:.1%}")
    lines.append("")
    lines.append("kind frequency (overall):")
    for kind in ("none", "hazard", "loot_cache", "rich_vein"):
        n = report.kind_counts.get(kind, 0)
        lines.append(
            f"  {kind:<11} {n / report.actions:6.2%}  ({n:,})"
            if report.actions
            else f"  {kind:<11}   n/a"
        )
    lines.append("")
    lines.append("hazard chance by depth (share of actions that are hazards):")
    for z, counts in report.depth_kind_counts.items():
        tot = sum(counts.values())
        haz = counts.get("hazard", 0)
        lines.append(f"  z={z:<3} {haz / tot:6.2%}" if tot else f"  z={z:<3}   n/a")
    lines.append("")
    lines.append("hazard resolution by tier (won / fled / lost · mean dmg):")
    for name, hz in report.hazard_by_tier.items():
        lines.append(
            f"  {name:<8} won {hz.rate(hz.won):5.1%}  fled {hz.rate(hz.fled):5.1%}  "
            f"lost {hz.rate(hz.lost):5.1%}  dmg {hz.mean_damage:4.1f}  (n={hz.total:,})"
        )
    lines.append("")
    lines.append("baseline-tier hazard resolution by depth (won / fled / lost · mean dmg):")
    for z, hz in report.baseline_hazard_by_depth.items():
        lines.append(
            f"  z={z:<3} won {hz.rate(hz.won):5.1%}  fled {hz.rate(hz.fled):5.1%}  "
            f"lost {hz.rate(hz.lost):5.1%}  dmg {hz.mean_damage:4.1f}  (n={hz.total:,})"
        )
    lines.append("")
    lines.append("reward yield (baseline tier · mean / p50 / p90 / max):")
    for kind, amts in report.reward_amounts.items():
        if amts:
            mean = sum(amts) / len(amts)
            lines.append(
                f"  {kind:<11} {mean:5.1f} / {_percentile(amts, 0.5):4.0f} / "
                f"{_percentile(amts, 0.9):4.0f} / {max(amts):4.0f}  (n={len(amts):,})"
            )
    if report.energy_costs:
        mean_e = sum(report.energy_costs) / len(report.energy_costs)
        lines.append("")
        lines.append(f"mean energy cost per triggered encounter: {mean_e:.2f}")
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    print(format_report(run()))
