"""PUBLIC shared encounter-resolution seam (claim-first per docs/lanes.md).

This is the shared surface both lanes consume: mining owns the PRODUCTION
encounter resolver; exploration consumes it via the ``EncounterResolver``
Protocol. Any change to this interface's public surface is an INTERFACE CHANGE
and must be announced in BOTH lanes' status files (``control/status-mining.md``
AND ``control/status-exploration.md``) in the same session it ships.

One resolution core serves all three Q-0186 encounter triggers (grid roaming,
explore actions, chat activity).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Protocol, runtime_checkable


class EncounterTrigger(str, Enum):
    """The three Q-0186 triggers, resolved by one shared core."""

    GRID_ROAM = "grid_roam"
    EXPLORE_ACTION = "explore_action"
    CHAT_ACTIVITY = "chat_activity"


@dataclass(frozen=True)
class EncounterRequest:
    """A request to resolve an encounter, made by a host lane."""

    trigger: EncounterTrigger
    player_id: str
    world_seed: object
    context: Mapping[str, object]


@dataclass(frozen=True)
class EncounterOutcome:
    """The deterministic result of resolving an ``EncounterRequest``."""

    encounter_id: str
    kind: str
    payload: Mapping[str, object]
    seed: int


@runtime_checkable
class EncounterResolver(Protocol):
    """Contract for any encounter resolver (reference or production)."""

    def resolve(self, request: EncounterRequest) -> EncounterOutcome:
        """Resolve a request into a deterministic outcome."""
        ...
