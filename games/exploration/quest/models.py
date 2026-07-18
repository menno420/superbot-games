"""Enums and frozen dataclasses for the deterministic quest engine.

All state is immutable (frozen dataclasses); the engine's transition functions
return NEW instances rather than mutating. Objective ``params`` are stored as a
tuple of (key, value) pairs so a template/instance stays hashable and frozen.

A ``params`` value is sometimes itself a mapping (e.g. the ``match`` payload).
A plain ``dict`` is unhashable, which would break the very hashable-and-frozen
invariant the tuple-of-pairs shape exists to protect, so nested mappings are
normalized at construction into ``_FrozenMap`` — a hashable, ordered wrapper —
and ``params_dict()`` reconstructs the plain ``dict`` on read so every consumer
sees the identical content.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


@dataclass(frozen=True)
class _FrozenMap:
    """A hashable, order-preserving stand-in for a nested mapping ``params`` value.

    Stores the mapping as a tuple of ``(key, value)`` pairs (recursively frozen),
    so an ``Objective``/``QuestTemplate`` holding one stays hashable. It is never
    handed to consumers directly: ``params_dict()`` thaws it back to a ``dict``.
    """

    items: tuple[tuple[object, object], ...]


def _freeze(value: object) -> object:
    """Recursively convert unhashable mappings into hashable ``_FrozenMap`` values."""
    if isinstance(value, _FrozenMap):
        return value
    if isinstance(value, dict):
        return _FrozenMap(tuple((k, _freeze(v)) for k, v in value.items()))
    return value


def _thaw(value: object) -> object:
    """Inverse of :func:`_freeze`: reconstruct plain ``dict`` values on read."""
    if isinstance(value, _FrozenMap):
        return {k: _thaw(v) for k, v in value.items}
    return value


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

    def __post_init__(self) -> None:
        # Freeze any nested mapping values so the objective stays hashable even
        # when a caller passes a plain dict (e.g. ``("match", {...})``). The
        # frozen dataclass forbids normal assignment, hence ``object.__setattr__``.
        frozen = tuple((key, _freeze(value)) for key, value in self.params)
        object.__setattr__(self, "params", frozen)

    def params_dict(self) -> dict[str, object]:
        """Return ``params`` as a plain dict for predicate evaluation."""
        return {key: _thaw(value) for key, value in self.params}


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
