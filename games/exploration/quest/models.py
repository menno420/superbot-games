"""Enums and frozen dataclasses for the deterministic quest engine.

All state is immutable (frozen dataclasses); the engine's transition functions
return NEW instances rather than mutating. Objective ``params`` are stored as a
tuple of (key, value) pairs so a template/instance stays hashable and frozen.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class QuestKind(str, Enum):
    FETCH = "fetch"
    ESCORT = "escort"
    HUNT = "hunt"
    RESCUE = "rescue"
    MYSTERY = "mystery"


class QuestState(str, Enum):
    OFFERED = "offered"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class RewardTier(str, Enum):
    I = "I"  # casual
    II = "II"  # standard
    III = "III"  # prestige


class QuestStateError(Exception):
    """Raised on an illegal quest state transition or a reward on an incomplete quest."""


@dataclass(frozen=True)
class Objective:
    """A single quest objective, matched against game events by ``predicate``."""

    key: str
    description: str
    predicate: str
    params: tuple[tuple[str, object], ...] = ()
    required: int = 1

    def params_dict(self) -> dict[str, object]:
        """Return ``params`` as a plain dict for predicate evaluation."""
        return dict(self.params)


@dataclass(frozen=True)
class RewardBundle:
    """A code-owned, capped reward. The AI never sets these amounts (Q-0040)."""

    global_xp: int
    game_xp: int
    currency: int
    capability: Optional[str] = None


@dataclass(frozen=True)
class ObjectiveProgress:
    key: str
    current: int
    required: int

    @property
    def done(self) -> bool:
        return self.current >= self.required


@dataclass(frozen=True)
class QuestTemplate:
    """Static quest content (data). The engine supplies the logic."""

    template_id: str
    kind: QuestKind
    title: str
    summary: str
    objectives: tuple[Objective, ...]
    prestige_capability: Optional[str] = None


@dataclass(frozen=True)
class QuestInstance:
    """A player's live quest, derived deterministically from a template + seed."""

    instance_id: str
    template_id: str
    kind: QuestKind
    player_id: str
    seed: int
    tier: RewardTier
    state: QuestState
    progress: tuple[ObjectiveProgress, ...] = field(default_factory=tuple)
    step: int = 0
