"""Survival difficulty tunables — the Energy axis scales the *shipped* bars.

Per **D-0004** (``docs/design/survival-d1-rebaseline.md``, option (a) — the
recommended re-baseline): **Easy ≡ today's shipped per-game energy bars,
byte-identical.** The survival Energy axis does NOT introduce a third global
energy bar — it only *modifies* the existing shipped bars (tighter cap, higher
cost, slower regen) for Medium/Hard, driven through the same
``games.mining.core.energy`` engine the base game already runs.

To keep the byte-identical pin meaningful and *provable*, ``EASY`` imports
mining's shipped constants directly rather than restating them — so a change to
the shipped bars can never silently drift Easy away from the base game (the
``test_easy_is_byte_identical_to_shipped_bars`` test re-asserts the identity).
Medium/Hard are the first-candidate gradient (sim-pinned here; exact tuning is
consolidation-phase work).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from games.mining.core import energy


class Difficulty(Enum):
    """Survival difficulty. One-way ascent (Q-0078): upgrade, never downgrade."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass(frozen=True)
class SurvivalTunables:
    """The three Energy-axis knobs the difficulty scales on the shipped bar."""

    max_energy: int
    regen_seconds: int
    cost: int


# EASY imports mining's shipped constants so it is provably byte-identical to the
# base game (D-0004). Medium/Hard tighten the bar (smaller cap, slower regen).
TUNABLES: dict[Difficulty, SurvivalTunables] = {
    Difficulty.EASY: SurvivalTunables(
        max_energy=energy.MAX_ENERGY,
        regen_seconds=energy.REGEN_SECONDS,
        cost=energy.DIG_COST,
    ),
    Difficulty.MEDIUM: SurvivalTunables(max_energy=50, regen_seconds=15, cost=1),
    Difficulty.HARD: SurvivalTunables(max_energy=40, regen_seconds=20, cost=1),
}
