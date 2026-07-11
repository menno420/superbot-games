"""THE THEME DATA (Q-0267) — every player-visible string keyed on a neutral id.

Scene prose, option copy, and flavour live here as data rows; the deterministic
resolver / effects reference the neutral ids only (``context_key`` / ``text_key`` /
``scene_id`` / ``option.id``). Re-skinning the game (D&D -> sci-fi -> pirate) is a
data-only edit here — the resolver, effects, and determinism never change (design §5).

The one walking-skeleton scene is ``waystation_road`` (the ESCORT quest
``safe_passage``, ``catalog.py``), ``default_option_id = "make_camp"`` — a
narrate-only no-op that is also the clamp target.
"""

from __future__ import annotations

from games.dnd.core.models import MenuOption, Scene

# Neutral-id -> player-visible copy. The ONLY place these strings live (Q-0267).
SCENE_TEXT: dict[str, str] = {
    # scene context prose
    "ctx.waystation_road": "You reach the fork on the waystation road. Dusk is coming.",
    # option copy (player-visible button text)
    "opt.advance_escort": "Press on toward the waystation",
    "opt.scout_ahead": "Scout the treeline first",
    "opt.make_camp": "Make camp and wait for dawn",
}


def text_for(text_key: str) -> str:
    """Return the player-visible copy for a neutral ``text_key`` or raise ``KeyError``."""
    return SCENE_TEXT[text_key]


WAYSTATION_ROAD = Scene(
    scene_id="waystation_road",
    context_key="ctx.waystation_road",
    options=(
        MenuOption(
            id="advance_escort",
            text_key="opt.advance_escort",
            effect_id="escort_step",
        ),
        MenuOption(
            id="scout_ahead",
            text_key="opt.scout_ahead",
            effect_id="scout_narrate",
        ),
        MenuOption(
            id="make_camp",
            text_key="opt.make_camp",
            effect_id="rest_noop",  # narrate-only no-op — the clamp target
        ),
    ),
    default_option_id="make_camp",
)


# The scene catalog — the bounded surface the DM is offered a menu from.
SCENES: dict[str, Scene] = {WAYSTATION_ROAD.scene_id: WAYSTATION_ROAD}


def get_scene(scene_id: str) -> Scene:
    """Return the scene for ``scene_id`` or raise ``KeyError``."""
    return SCENES[scene_id]


__all__ = ["SCENE_TEXT", "text_for", "WAYSTATION_ROAD", "SCENES", "get_scene"]
