"""Shared sweep + serialisation for the encounter narration golden test.

The golden fixture (``_encounter_golden.json``) is captured from the resolver
*before* the Q-0267 narration-data extraction and pins the FULL
:class:`EncounterOutcome` — kind, resolution, rewards, damage, energy_cost, **and**
the assembled narration string — byte-identical across a fixed sweep of
seeds × coords × depths × stat tiers × energy levels. The extraction is
behaviour-preserving iff the post-change sweep reproduces this fixture exactly.

Kept as a plain module (not a test) so both the one-off capture script and
``test_encounter_narration_golden`` iterate the *identical* sweep.
"""

from __future__ import annotations

from games.mining.core import encounters, equipment, grid
from games.mining.sim import encounters_sim as sim

# Fixed sweep — chosen to exercise every _resolve_* branch, including the
# energy-starved forced-retreat (energy=0 < HAZARD_ENERGY_COST) and the deep
# LOST path (z=15, fresh stats). Reuses the sim's representative stat tiers.
_SEEDS = range(5)
_XS = range(-12, 12)
_DEPTHS = (0, 3, 8, 15)
_ENERGIES = (0, 100)


def _stat_tiers() -> dict[str, equipment.EffectiveStats]:
    """The sim's representative stat tiers (fresh→geared→veteran, order-stable)."""
    return sim.tier_stats()


def _serialise(out: encounters.EncounterOutcome) -> list:
    """A JSON-safe, order-stable record of the full outcome (narration included)."""
    return [
        out.kind.value,
        out.resolution.value,
        out.damage_taken,
        out.energy_cost,
        [[r.item, r.amount] for r in out.rewards],
        out.narration,
    ]


# Explicit per-feature cells guarantee the rarer branches (TREASURE→LOOT_CACHE is
# a 2% grid feature and would otherwise be absent from a lean coordinate sweep).
def _explicit_cells() -> list[tuple[str, grid.Cell]]:
    out: list[tuple[str, grid.Cell]] = []
    for z in (0, 5, 12):
        out.append((f"treasure@{z}", grid.Cell(0, 0, z, grid.CellFeature.TREASURE, "gold", 2.0)))
        out.append((f"rich@{z}", grid.Cell(0, 0, z, grid.CellFeature.RICH, "iron", 2.0)))
        out.append((f"normal@{z}", grid.Cell(0, 0, z, grid.CellFeature.NORMAL, "iron", 1.0)))
        out.append((f"barren@{z}", grid.Cell(0, 0, z, grid.CellFeature.BARREN, "stone", 0.5)))
    return out


def sweep_records() -> list[list]:
    """Deterministic list of ``[key, serialised-outcome]`` over the fixed sweep."""
    tiers = _stat_tiers()
    records: list[list] = []
    for seed in _SEEDS:
        for x in _XS:
            for z in _DEPTHS:
                cell = grid.cell_at(seed, x, 0, z)
                for tier_name, stats in tiers.items():
                    for energy in _ENERGIES:
                        out = encounters.resolve(seed, cell, stats, energy=energy)
                        key = f"grid|{seed}|{x}|{z}|{tier_name}|{energy}"
                        records.append([key, _serialise(out)])
    # Explicit feature cells across many rng streams — pins every branch.
    for label, cell in _explicit_cells():
        for stream in range(40):
            for tier_name, stats in tiers.items():
                for energy in _ENERGIES:
                    import random

                    out = encounters.resolve(
                        0, cell, stats, energy=energy, rng=random.Random(stream)
                    )
                    key = f"explicit|{label}|{stream}|{tier_name}|{energy}"
                    records.append([key, _serialise(out)])
    return records
