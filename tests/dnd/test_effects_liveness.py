"""Effects-liveness sweep — every pre-priced EFFECTS row is wired AND runs.

Complements the scene-reachability sweep (#126): that proved every SCENE is
live; `Scene.__post_init__` proves every referenced effect id EXISTS
(referenced-if-used). Nothing proved the converse — that every id in
`games/dnd/core/effects.py`'s `EFFECTS` registry is actually *used*: referenced
by ≥1 option on a scene reachable from `START_SCENE`, and executable through
the audited seam (`services/dnd_workflow.choose`) without raising, minting
exactly what it declares. An orphaned effect would ship silently as dead
pre-priced balance data; a raising one would blow up at play time only.

Read-only over the data + seam; the #83 / VERDICT-044 mint-at-most-once guard
is pinned INTACT here, never weakened. Sweep verdict at HEAD: no orphaned
effect, no raising effect — the value is the tripwire.
"""

from __future__ import annotations

import pytest

from services.audit import InMemorySink
from services.dnd_workflow import START_SCENE, DnDState, choose

from games.dnd.core.effects import EFFECTS
from games.dnd.data.scenes import SCENES, text_for
from games.exploration.quest import catalog
from games.exploration.quest.models import RewardTier

#: Chat-activity XP high enough that leverage.menu_width surfaces every option
#: (width 4 >= the 3 options each scene carries), so the seam can be steered to
#: ANY option id without the clamp. Width is a display/acceptance lever only.
FULL_MENU_XP = 1000


def _reachable_scene_ids() -> set[str]:
    """BFS over the pre-defined ``next_scene_id`` edges from START_SCENE."""
    seen: set[str] = set()
    frontier = [START_SCENE]
    while frontier:
        scene_id = frontier.pop()
        if scene_id in seen:
            continue
        seen.add(scene_id)
        for opt in SCENES[scene_id].options:
            if opt.next_scene_id is not None and opt.next_scene_id not in seen:
                frontier.append(opt.next_scene_id)
    return seen


def _referencing_options() -> dict[str, list[tuple[str, str]]]:
    """effect_id -> [(scene_id, option_id), ...] over REACHABLE scenes only."""
    refs: dict[str, list[tuple[str, str]]] = {}
    for scene_id in sorted(_reachable_scene_ids()):
        for opt in SCENES[scene_id].options:
            refs.setdefault(opt.effect_id, []).append((scene_id, opt.id))
    return refs


def _path_to(scene_id: str) -> list[str]:
    """Option ids that walk a fresh session from START_SCENE to *scene_id* (BFS)."""
    if scene_id == START_SCENE:
        return []
    parents: dict[str, tuple[str, str]] = {}  # scene -> (prev_scene, option_id)
    frontier = [START_SCENE]
    seen = {START_SCENE}
    while frontier:
        current = frontier.pop(0)
        for opt in SCENES[current].options:
            nxt = opt.next_scene_id
            if nxt is not None and nxt not in seen:
                parents[nxt] = (current, opt.id)
                if nxt == scene_id:
                    path: list[str] = []
                    cursor = scene_id
                    while cursor != START_SCENE:
                        prev, opt_id = parents[cursor]
                        path.append(opt_id)
                        cursor = prev
                    return list(reversed(path))
                seen.add(nxt)
                frontier.append(nxt)
    raise AssertionError(f"no path from {START_SCENE} to {scene_id}")


def _fresh(xp: int = FULL_MENU_XP) -> tuple[DnDState, InMemorySink]:
    return DnDState(xp=xp), InMemorySink()


def test_every_effect_is_referenced_on_a_scene_reachable_from_start():
    """The orphan sweep: an EFFECTS row no reachable option references is dead
    pre-priced balance data — a HEADLINE, pinned here, never silently dropped."""
    refs = _referencing_options()
    orphaned = sorted(set(EFFECTS) - set(refs))
    assert orphaned == [], (
        f"orphaned pre-priced effects (registered but referenced by no option on "
        f"any scene reachable from {START_SCENE!r}): {orphaned}"
    )
    # And the sweep is grounded: the registry itself is non-empty and reachable
    # scenes cover the whole catalog at HEAD (the #126 sweep's result, relied on).
    assert set(refs) == set(EFFECTS)


def test_every_effect_executes_once_via_the_seam_without_raising():
    """Each effect runs end-to-end through choose() — resolver, effect apply,
    fold, audit — from a fresh session steered to a referencing option."""
    for effect_id, sites in sorted(_referencing_options().items()):
        scene_id, option_id = sites[0]
        state, sink = _fresh()
        for step_option in _path_to(scene_id):
            choose(state, step_option, sink=sink)
        assert state.scene_id == scene_id
        before = len(sink.records)
        res = choose(state, option_id, sink=sink)  # must not raise
        assert res.ok, f"effect {effect_id!r} via {scene_id}/{option_id} not ok"
        assert res.resolution.chosen_option_id == option_id  # steered, not clamped
        assert res.message == text_for(SCENES[scene_id].option(option_id).text_key)
        assert len(sink.records) == before + 1  # D2: exactly one row per choose


def test_narrate_only_effects_mint_nothing():
    """rest_noop and scout_narrate declare no reward — pin that executing them
    grants nothing and leaves every running total untouched."""
    narrate_only = {eid for eid in EFFECTS if eid in {"rest_noop", "scout_narrate"}}
    assert narrate_only == {"rest_noop", "scout_narrate"}  # the registry's two no-mint rows
    refs = _referencing_options()
    for effect_id in sorted(narrate_only):
        for scene_id, option_id in refs[effect_id]:
            state, sink = _fresh()
            for step_option in _path_to(scene_id):
                choose(state, step_option, sink=sink)
            # Walking there may have minted (escort edges); snapshot, then act.
            totals_before = (state.global_xp, state.game_xp, state.currency)
            res = choose(state, option_id, sink=sink)
            assert res.reward is None
            assert (state.global_xp, state.game_xp, state.currency) == totals_before
            assert state.capability is None


def test_escort_step_mints_exactly_the_engine_tier_capped_bundle():
    """escort_step's declared grant: the engine's TIER_CAPS[I] bundle VERBATIM,
    folded once into the running totals."""
    cap = catalog.TIER_CAPS[RewardTier.I]
    state, sink = _fresh()
    res = choose(state, "advance_escort", sink=sink)
    assert res.reward == cap
    assert (state.global_xp, state.game_xp, state.currency) == (
        cap.global_xp,
        cap.game_xp,
        cap.currency,
    )
    assert state.bundle_minted is True
    assert res.record.target == f"reward:{START_SCENE}"  # the mint IS the audited mutation


def test_mint_at_most_once_guard_stays_intact_across_both_escort_sites():
    """VERDICT 044 / #83: the second escort_step in one session is suppressed —
    executing the OTHER escort site after the first mint grants nothing."""
    state, sink = _fresh()
    first = choose(state, "advance_escort", sink=sink)  # waystation_road site mints
    assert first.reward is not None
    totals_after_first = (state.global_xp, state.game_xp, state.currency)
    choose(state, "circle_to_treeline", sink=sink)  # -> treeline_watch
    second = choose(state, "signal_escort", sink=sink)  # treeline_watch escort site
    assert second.ok
    assert second.reward is None  # suppressed, not re-minted
    assert (state.global_xp, state.game_xp, state.currency) == totals_after_first
    assert state.bundle_minted is True


def test_effect_apply_is_deterministic_for_a_fixed_seed():
    """Registry-level pin: every effect is a pure function of (seed, player_id)
    — two applies with the same inputs produce equal outcomes."""
    for effect_id, effect in sorted(EFFECTS.items()):
        once = effect.apply(seed=7, player_id="p1")
        twice = effect.apply(seed=7, player_id="p1")
        assert once == twice, f"effect {effect_id!r} not deterministic"
        assert once.effect_id == effect_id


def test_rest_noop_is_live_at_floor_width_via_the_clamp_path():
    """At the xp floor the menu surfaces only 2 options, and every scene's
    rest_noop option sits third — so at floor width rest_noop's liveness is the
    CLAMP path: any off-menu id executes it as the scene's safe default."""
    for scene_id in sorted(_reachable_scene_ids()):
        scene = SCENES[scene_id]
        default_opt = scene.option(scene.default_option_id)
        assert default_opt.effect_id == "rest_noop"  # the clamp target is the no-op
        state, sink = _fresh(xp=0)
        for step_option in _path_to(scene_id):
            choose(state, step_option, sink=sink)
        res = choose(state, "definitely_off_menu", sink=sink)
        assert res.ok
        assert res.resolution.clamped is True
        assert res.resolution.chosen_option_id == scene.default_option_id
        assert res.reward is None
