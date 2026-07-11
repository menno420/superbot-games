"""Survival sim harness (exploration P2) — public surface.

Proves a survival-difficulty *energy* tuning meets the Q-0087 dual-track bar
before it ships, by driving the shipped mining energy engine
(``games.mining.core.energy``) through per-difficulty tunables. Easy is
byte-identical to the shipped bars (D-0004); Medium/Hard only scale the shipped
bars — no third global energy bar. See ``docs/design/survival-sim-harness.md``.
"""

from __future__ import annotations

from games.exploration.survival.difficulty import (
    TUNABLES,
    Difficulty,
    SurvivalTunables,
)
from games.exploration.survival.sim import (
    DifficultyStats,
    SurvivalReport,
    format_report,
    run,
)

__all__ = [
    "Difficulty",
    "SurvivalTunables",
    "TUNABLES",
    "DifficultyStats",
    "SurvivalReport",
    "run",
    "format_report",
]
