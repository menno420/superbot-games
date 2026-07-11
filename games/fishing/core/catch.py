"""Catch resolver — the pure heart of fishing (deterministic; NO LLM anywhere).

Given a world *seed*, a *spot id*, the player's :class:`EffectiveStats`, and their
remaining *energy*, :func:`resolve_cast` decides **one cast**: whether a fish bit, which
species (and how big) it is, the narration, and the energy the cast costs — returned as a
frozen :class:`CastOutcome`. Deterministic code owns every outcome; there is no model call
in the loop.

Design shape (mirrors ``games.mining.core.encounters`` — design doc
``docs/design/fishing-catch-skeleton.md``):

* **Deterministic by default, live-roll by injection.** ``rng=None`` derives a stream from
  :func:`games.fishing.core.rng.fishing_seed` (an *independent* per-spot splitmix64
  stream), so ``(seed, spot_id)`` → the *same* cast (reproducible · testable). A host that
  wants live variance (two casts at the same spot differ) injects its **own**
  ``random.Random`` seeded with player/action entropy — the resolver is pure either way.

* **Theme via data.** Every player-visible noun comes from
  :mod:`games.fishing.core.species` (a data table keyed on neutral ids). The logic branches
  never name a species; narration is assembled from the picked row's ``emoji`` / ``flavor``
  / ``name``. Re-theme by editing the table (Q-0267).

* **Gear via the shared stat model, no pay-to-win.** The only advantage levers are
  :class:`EffectiveStats` ``fishing_power`` (biases the weighted species pick toward the
  bigger/rarer tail) and ``bite_luck`` (raises the bite chance) — the fields shipped in
  ``games.mining.core.equipment`` (Q-0175). They come solely from gear earned in-domain;
  the signature exposes no coin/purchase/spend lever. A zero-gear player still catches
  across the common range — gear *biases*, never *gates* (Q-0039/Q-0190).

* **Reused energy engine, honest states.** A cast spends :data:`CAST_COST` through the
  shared ``games.mining.core.energy`` model (fishing shares the one energy economy). If the
  player lacks the energy to cast, the resolver returns an **honest no-bite** outcome
  (``bit=False``, ``energy_cost=0``) — it never raises.

Pure: stdlib + dataclasses/random only — no Discord, no DB, no IO.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from games.fishing.core import species as species_table
from games.fishing.core.rng import fishing_seed
from games.mining.core import energy as energy_model
from games.mining.core.equipment import EffectiveStats

# ---------------------------------------------------------------------------
# Sim-pinned tunables. Every number below is justified by a committed sim run
# (games/fishing/sim/catch_sim.py) whose output + bounds live in
# docs/design/fishing-catch-skeleton.md §5. New design — NOT preserved-from-oracle.
# ---------------------------------------------------------------------------

# --- Energy -----------------------------------------------------------------
# A cast spends this through the reused games.mining.core.energy engine, so fishing
# shares the one energy economy (a full 60-bar ≈ 30 casts before the passive-regen
# throttle). Kept modest — fishing is a slower, calmer faucet than digging.
CAST_COST = 2

# --- Bite chance ------------------------------------------------------------
# Base chance a cast gets a bite at all (before gear). bite_luck raises it by
# BITE_LUCK_PER_POINT per point, capped at MAX_BITE_CHANCE so a maxed rod still
# sometimes comes up empty (a bite is never guaranteed — honest variance).
BASE_BITE_CHANCE = 0.55
BITE_LUCK_PER_POINT = 0.08
MAX_BITE_CHANCE = 0.90

# --- Species pick bias ------------------------------------------------------
# fishing_power shifts the weighted pick toward bigger/rarer species: a species'
# effective weight is scaled by (1 + fishing_power · POWER_BIAS_PER_POINT · (size_rank−1)),
# so rank-1 (the common minnow) is never boosted and the rare tail grows with power.
# fishing_power=0 → the base rarity weights exactly (byte-identical baseline).
POWER_BIAS_PER_POINT = 0.06

# --- Size -------------------------------------------------------------------
# Reported catch size (arbitrary "cm"): a species' size_rank sets the base, plus a
# deterministic jitter. Bigger species are bigger fish; the pick bias (not a size
# bonus) is fishing_power's lever, keeping the size honest per species.
SIZE_PER_RANK = 12
SIZE_JITTER = 8

# --- Gear caps (sim-pinned; re-asserted by tests) ---------------------------
# The best fishing loadout is a single "master angler charm" (CHARM slot, one at a
# time): fishing_power 6 / bite_luck 3 (games.mining.core.equipment). These caps pin
# that ceiling so a future gear row cannot silently push fishing past the sim's bounds.
MAX_FISHING_POWER = 6
MAX_BITE_LUCK = 3


@dataclass(frozen=True)
class Catch:
    """A landed fish — a neutral species id + its size (display nouns live in the table)."""

    species_id: str
    size: int


@dataclass(frozen=True)
class CastOutcome:
    """The pure result of one cast — a record of what happened (no side effects).

    The workflow layer applies ``energy_cost`` (debit energy) and, on a bite, adds the
    ``catch`` to the player's haul. ``bit`` is whether a fish bit the line; when it is
    ``False`` (an empty cast, or too tired to cast) ``catch`` is ``None``.
    """

    bit: bool
    catch: Catch | None
    narration: str
    energy_cost: int


# The honest "too tired to cast" outcome — no energy spent, no bite. Byte-identical
# regardless of stats (gear can never manufacture a cast you can't afford).
_TOO_TIRED = CastOutcome(
    bit=False,
    catch=None,
    narration="😴 Too tired to cast — you rest a while by the water.",
    energy_cost=0,
)


def _bite_chance(stats: EffectiveStats) -> float:
    """Chance a cast gets a bite, raised by earned ``bite_luck`` (capped)."""
    raised = BASE_BITE_CHANCE + max(0, stats.bite_luck) * BITE_LUCK_PER_POINT
    return min(MAX_BITE_CHANCE, raised)


def _pick_species(stats: EffectiveStats, rng: random.Random) -> species_table.Species:
    """Weighted species pick, biased toward the bigger/rarer tail by ``fishing_power``.

    ``fishing_power=0`` → the base rarity weights exactly (the common species dominate),
    so a zero-gear player still catches across the common range. More power scales the
    higher-``size_rank`` weights up — a bias, never a gate (every species stays reachable).
    """
    power = max(0, stats.fishing_power)
    rows = species_table.all_species()
    weights = [
        row.rarity_weight * (1.0 + power * POWER_BIAS_PER_POINT * (row.size_rank - 1))
        for row in rows
    ]
    return rng.choices(rows, weights=weights, k=1)[0]


def _roll_size(row: species_table.Species, rng: random.Random) -> int:
    """A caught fish's reported size — its ``size_rank`` base plus a deterministic jitter."""
    return row.size_rank * SIZE_PER_RANK + rng.randint(0, SIZE_JITTER)


def resolve_cast(
    seed: int,
    spot_id: str,
    stats: EffectiveStats | None = None,
    *,
    energy: int = energy_model.MAX_ENERGY,
    rng: random.Random | None = None,
) -> CastOutcome:
    """Resolve one cast at *spot_id* in world *seed*.

    *stats* is the player's :class:`EffectiveStats` (``None`` = a bare baseline angler);
    only ``fishing_power`` / ``bite_luck`` are read. *energy* is remaining energy (a cast
    needs :data:`CAST_COST`; too little → an honest no-bite, no exception). *rng* is
    injected for live-roll variance / tests; ``None`` derives the deterministic default
    stream from :func:`fishing_seed`, so ``(seed, spot_id)`` → the same cast.

    Always returns a :class:`CastOutcome`; it never raises for an out-of-energy player.
    """
    effective = stats or EffectiveStats()

    # Honest energy gate — can't afford the cast → rest, spend nothing, catch nothing.
    if energy < CAST_COST:
        return _TOO_TIRED

    chooser = rng or random.Random(fishing_seed(seed, spot_id))

    if chooser.random() >= _bite_chance(effective):
        return CastOutcome(
            bit=False,
            catch=None,
            narration="🎣 You cast out and wait… but nothing bites this time.",
            energy_cost=CAST_COST,
        )

    row = _pick_species(effective, chooser)
    size = _roll_size(row, chooser)
    catch = Catch(species_id=row.species_id, size=size)
    narration = f"{row.emoji} {row.flavor} — you land a {row.name} ({size} cm)!"
    return CastOutcome(
        bit=True,
        catch=catch,
        narration=narration,
        energy_cost=CAST_COST,
    )


__all__ = [
    "CAST_COST",
    "BASE_BITE_CHANCE",
    "BITE_LUCK_PER_POINT",
    "MAX_BITE_CHANCE",
    "POWER_BIAS_PER_POINT",
    "SIZE_PER_RANK",
    "SIZE_JITTER",
    "MAX_FISHING_POWER",
    "MAX_BITE_LUCK",
    "Catch",
    "CastOutcome",
    "resolve_cast",
]
