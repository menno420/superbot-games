"""Data-driven scene chaining — transitions are PRE-DEFINED DATA, never DM-computed.

The scene-chaining slice extends the bounded-menu law (Q-0040 / D-0007, §4.4) to
navigation: an option's destination (``next_scene_id``) is fixed DATA on the button,
so the AI DM — which may only pick an option id — can never steer to an arbitrary
scene. The headline is the **deterministic traversal** test: a fixed sequence of
valid choices from the start scene walks a pinned scene PATH. The safety headline is
that a hallucinated choice clamps to the default option and takes only the DEFAULT's
own pre-defined edge (here: stay), leaving state consistent.
"""

from __future__ import annotations

from games.dnd.core.models import DMChoice, MenuOption, Scene
from games.dnd.core.resolver import resolve
from games.dnd.data.scenes import (
    SCENES,
    TREELINE_WATCH,
    WAYSTATION_GATE,
    WAYSTATION_ROAD,
    get_scene,
)

# High XP surfaces the full menu (menu_width caps at 4 >= each scene's 3 options).
FULL_XP = 5000
SEED = 424242


def _walk(start: Scene, option_ids: list[str]) -> list[str]:
    """Traverse the chain following a fixed sequence of VALID option ids.

    Returns the scene PATH actually visited (the start scene plus each destination the
    chosen option's DATA pointed at). Stops when a chosen option's ``next_scene_id`` is
    ``None`` (stay/end) or the id list is exhausted.
    """
    path = [start.scene_id]
    scene = start
    for oid in option_ids:
        res = resolve(scene, DMChoice(option_id=oid), xp=FULL_XP, seed=SEED)
        assert res.clamped is False, f"expected {oid!r} to be a valid, surfaced option"
        if res.next_scene_id is None:
            break
        scene = get_scene(res.next_scene_id)
        path.append(scene.scene_id)
    return path


# --------------------------------------------------------------------------- #
# 1. Deterministic traversal — a fixed choice sequence yields a PINNED path.
# --------------------------------------------------------------------------- #

def test_fixed_choices_yield_deterministic_pinned_path() -> None:
    # Press on -> gate; circle back -> treeline; hold -> stay/end.
    path = _walk(
        WAYSTATION_ROAD,
        ["advance_escort", "circle_to_treeline", "hold_position"],
    )
    assert path == ["waystation_road", "waystation_gate", "treeline_watch"]


def test_traversal_is_repeatable() -> None:
    seq = ["scout_ahead", "signal_escort"]
    assert _walk(WAYSTATION_ROAD, seq) == _walk(WAYSTATION_ROAD, seq)
    # scout_ahead -> treeline_watch, then signal_escort ends the beat (next=None).
    assert _walk(WAYSTATION_ROAD, seq) == ["waystation_road", "treeline_watch"]


# --------------------------------------------------------------------------- #
# 2. Transition is DATA-driven — the destination comes off the option, not the DM.
# --------------------------------------------------------------------------- #

def test_next_scene_comes_from_the_chosen_options_data() -> None:
    for scene in SCENES.values():
        for opt in scene.options:
            res = resolve(scene, DMChoice(option_id=opt.id), xp=FULL_XP, seed=SEED)
            if not res.clamped:  # a surfaced, valid option
                # The resolution's destination is byte-identical to the option's DATA.
                assert res.next_scene_id == opt.next_scene_id


def test_dmchoice_cannot_introduce_a_next_scene_not_on_the_option() -> None:
    # A DMChoice carries ONLY an option id (+ display flavour). There is no field on it
    # through which the model could inject a destination — the resolution's next_scene_id
    # is drawn solely from the option's fixed DATA.
    assert not hasattr(DMChoice(option_id="advance_escort"), "next_scene_id")
    res = resolve(
        WAYSTATION_ROAD,
        DMChoice(option_id="advance_escort", flavor="teleport me to the throne room"),
        xp=FULL_XP,
        seed=SEED,
    )
    # Flavour is display-only; the destination is exactly the option's pre-defined edge.
    assert res.next_scene_id == WAYSTATION_ROAD.option("advance_escort").next_scene_id
    assert res.next_scene_id == "waystation_gate"


# --------------------------------------------------------------------------- #
# 3. Clamp still chains SAFELY — a hallucinated choice takes only the default's edge.
# --------------------------------------------------------------------------- #

def test_hallucinated_choice_clamps_and_takes_default_edge_only() -> None:
    # Mid-chain, at the gate, the DM invents an off-menu id.
    res = resolve(
        WAYSTATION_GATE,
        DMChoice(option_id="fly_over_the_wall"),
        xp=FULL_XP,
        seed=SEED,
    )
    assert res.clamped is True
    assert res.chosen_option_id == WAYSTATION_GATE.default_option_id == "rest_at_gate"
    assert res.effect_id == "rest_noop"
    assert res.reward is None  # mints nothing
    assert res.event is None  # advances no quest
    # The destination is the DEFAULT option's OWN pre-defined edge — here None (stay),
    # NOT anything the hallucinated input suggested.
    default_opt = WAYSTATION_GATE.option(WAYSTATION_GATE.default_option_id)
    assert res.next_scene_id == default_opt.next_scene_id is None


def test_malformed_choice_clamps_to_default_edge_across_scenes() -> None:
    # None / wrong-type payloads clamp to the default in every chain scene, and the
    # destination is always the default option's own edge (state stays consistent).
    for scene in (WAYSTATION_ROAD, WAYSTATION_GATE, TREELINE_WATCH):
        default_opt = scene.option(scene.default_option_id)
        for bad in (None, {}, "advance_escort", DMChoice(option_id="")):
            res = resolve(scene, bad, xp=FULL_XP, seed=SEED)
            assert res.clamped is True
            assert res.chosen_option_id == scene.default_option_id
            assert res.next_scene_id == default_opt.next_scene_id


# --------------------------------------------------------------------------- #
# 4. No dangling edges — every referenced next_scene_id resolves to a real scene.
# --------------------------------------------------------------------------- #

def test_every_transition_resolves_to_a_real_scene() -> None:
    for scene in SCENES.values():
        for opt in scene.options:
            if opt.next_scene_id is not None:
                assert opt.next_scene_id in SCENES
                # get_scene must actually return the destination (no dangling edge).
                assert get_scene(opt.next_scene_id).scene_id == opt.next_scene_id


def test_load_time_guard_rejects_a_dangling_transition() -> None:
    # The catalog invariant (_assert_transitions_resolve) is the load-time guard; a
    # scene whose option points at a non-existent scene must be catchable. We mimic the
    # check against the live catalog to prove a dangling edge would NOT resolve.
    ghost = Scene(
        scene_id="ghost_scene",
        context_key="ctx.waystation_road",
        options=(
            MenuOption(
                id="into_the_void",
                text_key="opt.make_camp",
                effect_id="rest_noop",
                next_scene_id="scene_that_does_not_exist",
            ),
        ),
        default_option_id="into_the_void",
    )
    dangling = ghost.options[0].next_scene_id
    assert dangling is not None and dangling not in SCENES
