"""D&D story game — the AI Dungeon Master as a bounded-menu plugin package.

A pure-domain package in the same three-layer shape mining and fishing ship
(design: ``docs/design/dnd-story-design.md``). It sits on top of the already-shipped
deterministic quest/encounter engine (``games/exploration/quest/**``) and REUSES it
rather than duplicating it — ``DetRng`` / ``derive_seed`` for seeding,
``engine.grant_rewards`` (tier-capped, ``<= GLOBAL_MAX``) for rewards, and
``leverage.menu_width`` for the DM's menu width.

The heart is the **bounded-menu law** (Q-0040 / D-0007): the AI Dungeon Master picks
ONLY from a pre-approved, hard-capped menu enforced by code. It never computes amounts
and never mutates state — deterministic code owns every outcome it narrates. Off-menu,
malformed, or hallucinated DM output CLAMPS to a deterministic no-op
(:func:`games.dnd.core.resolver.resolve`).

This first slice is the **walking skeleton**: one scene, one <=4-option menu, one
deterministic resolver, plus its data catalog. Workflow and host wiring are deferred
(as fishing did). Only ``core`` (+ its ``data`` catalog) ships here — no LLM anywhere
in the resolution loop.
"""

from __future__ import annotations

from games.dnd.core.effects import EFFECTS, Effect, EffectOutcome
from games.dnd.core.models import (
    FLAVOR_CAP,
    MAX_MENU_SIZE,
    DMChoice,
    MenuOption,
    Scene,
)
from games.dnd.core.resolver import Resolution, resolve
from games.dnd.data.scenes import SCENES, WAYSTATION_ROAD, get_scene, text_for

__all__ = [
    # schema
    "Scene",
    "MenuOption",
    "DMChoice",
    "MAX_MENU_SIZE",
    "FLAVOR_CAP",
    # effects
    "Effect",
    "EffectOutcome",
    "EFFECTS",
    # resolver
    "resolve",
    "Resolution",
    # data
    "SCENES",
    "WAYSTATION_ROAD",
    "get_scene",
    "text_for",
]
