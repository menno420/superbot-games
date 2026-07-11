"""THE THEME DATA (Q-0267) — every player-visible string keyed on a neutral id.

Scene prose, option copy, and flavour live here as data rows; the deterministic
resolver / effects reference the neutral ids only (``context_key`` / ``text_key`` /
``scene_id`` / ``option.id``). Re-skinning the game (D&D -> sci-fi -> pirate) is a
data-only edit here — the resolver, effects, and determinism never change (design §5).

The walking-skeleton start scene is ``waystation_road`` (the ESCORT quest
``safe_passage``, ``catalog.py``), ``default_option_id = "make_camp"`` — a
narrate-only no-op that is also the clamp target.

Scene-chaining (this slice): each :class:`MenuOption` may carry a PRE-DEFINED
``next_scene_id`` — plain DATA naming the option's destination scene. The DM never
computes or chooses a transition; it only picks an option id, and that option's edge
is fixed here. Pressing on / scouting from ``waystation_road`` branches into two
follow-on scenes, ``waystation_gate`` and ``treeline_watch``, each a hard-capped menu
with its own narrate-only no-op default. Every referenced ``next_scene_id`` is checked
against :data:`SCENES` at import time by :func:`_assert_transitions_resolve` — no
dangling edge ships.
"""

from __future__ import annotations

from games.dnd.core.models import MenuOption, Scene

# Neutral-id -> player-visible copy. The ONLY place these strings live (Q-0267);
# every noun, flavour beat, and emoji is DATA here, never in the resolver/effects.
SCENE_TEXT: dict[str, str] = {
    # --- scene context prose ------------------------------------------------- #
    "ctx.waystation_road": "🌲 You reach the fork on the waystation road. Dusk is coming.",
    "ctx.waystation_gate": "🏮 The waystation gate looms; a lantern-keeper eyes the dark.",
    "ctx.treeline_watch": "🌙 From the treeline you watch the road below for the escort.",
    # --- option copy (player-visible button text) ---------------------------- #
    "opt.advance_escort": "Press on toward the waystation",
    "opt.scout_ahead": "Scout the treeline first",
    "opt.make_camp": "Make camp and wait for dawn",
    "opt.enter_common_room": "Step into the common room",
    "opt.circle_to_treeline": "Circle back to the treeline",
    "opt.rest_at_gate": "Bed down by the gate",
    "opt.signal_escort": "Signal the escort onward",
    "opt.hold_position": "Hold position and keep watch",
    "opt.fall_back_camp": "Fall back and make camp",
}


def text_for(text_key: str) -> str:
    """Return the player-visible copy for a neutral ``text_key`` or raise ``KeyError``."""
    return SCENE_TEXT[text_key]


# --------------------------------------------------------------------------- #
# The scene chain. Transitions are DATA on each option (``next_scene_id``); the DM
# only ever picks an option id, so it can never steer to a scene that is not one of
# these pre-defined edges. ``None`` = stay / end the scene.
# --------------------------------------------------------------------------- #

WAYSTATION_ROAD = Scene(
    scene_id="waystation_road",
    context_key="ctx.waystation_road",
    options=(
        MenuOption(
            id="advance_escort",
            text_key="opt.advance_escort",
            effect_id="escort_step",
            next_scene_id="waystation_gate",  # pressing on -> the gate
        ),
        MenuOption(
            id="scout_ahead",
            text_key="opt.scout_ahead",
            effect_id="scout_narrate",
            next_scene_id="treeline_watch",  # scouting -> the treeline watch
        ),
        MenuOption(
            id="make_camp",
            text_key="opt.make_camp",
            effect_id="rest_noop",  # narrate-only no-op — the clamp target
            next_scene_id=None,  # camping stays put (the safe default)
        ),
    ),
    default_option_id="make_camp",
)


WAYSTATION_GATE = Scene(
    scene_id="waystation_gate",
    context_key="ctx.waystation_gate",
    options=(
        MenuOption(
            id="enter_common_room",
            text_key="opt.enter_common_room",
            effect_id="scout_narrate",  # narrate-only flavour beat
            next_scene_id=None,  # terminal narrate — stays at the gate
        ),
        MenuOption(
            id="circle_to_treeline",
            text_key="opt.circle_to_treeline",
            effect_id="scout_narrate",
            next_scene_id="treeline_watch",  # cross-link back to the watch
        ),
        MenuOption(
            id="rest_at_gate",
            text_key="opt.rest_at_gate",
            effect_id="rest_noop",  # narrate-only no-op — the clamp target
            next_scene_id=None,  # resting stays put (the safe default)
        ),
    ),
    default_option_id="rest_at_gate",
)


TREELINE_WATCH = Scene(
    scene_id="treeline_watch",
    context_key="ctx.treeline_watch",
    options=(
        MenuOption(
            id="signal_escort",
            text_key="opt.signal_escort",
            effect_id="escort_step",  # reuses the sim-pinned ESCORT reward effect
            next_scene_id=None,  # the escort completes here — end of the beat
        ),
        MenuOption(
            id="hold_position",
            text_key="opt.hold_position",
            effect_id="scout_narrate",
            next_scene_id=None,  # keep watching — stays at the treeline
        ),
        MenuOption(
            id="fall_back_camp",
            text_key="opt.fall_back_camp",
            effect_id="rest_noop",  # narrate-only no-op — the clamp target
            next_scene_id=None,  # falling back stays put (the safe default)
        ),
    ),
    default_option_id="fall_back_camp",
)


# The scene catalog — the bounded surface the DM is offered a menu from.
SCENES: dict[str, Scene] = {
    scene.scene_id: scene
    for scene in (WAYSTATION_ROAD, WAYSTATION_GATE, TREELINE_WATCH)
}


def _assert_transitions_resolve() -> None:
    """Every option's PRE-DEFINED ``next_scene_id`` must name a real scene (no dangling
    edges). Runs at import so a typo'd transition fails LOUDLY at load, never at play
    time. ``None`` (stay/end) is always valid. This is the catalog-level invariant that
    ``models.py`` cannot enforce itself (it stays catalog-free to avoid an import cycle).
    """
    for scene in SCENES.values():
        for opt in scene.options:
            if opt.next_scene_id is not None:
                assert opt.next_scene_id in SCENES, (
                    f"scene {scene.scene_id!r}: option {opt.id!r} points at unknown "
                    f"next_scene_id {opt.next_scene_id!r}"
                )


_assert_transitions_resolve()


def get_scene(scene_id: str) -> Scene:
    """Return the scene for ``scene_id`` or raise ``KeyError``."""
    return SCENES[scene_id]


__all__ = [
    "SCENE_TEXT",
    "text_for",
    "WAYSTATION_ROAD",
    "WAYSTATION_GATE",
    "TREELINE_WATCH",
    "SCENES",
    "get_scene",
    "_assert_transitions_resolve",
]
