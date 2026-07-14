"""DND scene-graph reachability — every scene is on a path from the start.

``games/dnd/data/scenes.py`` validates transitions at import time, but ONLY
that no edge dangles (``_assert_transitions_resolve``). Nothing checked the
converse structural property: that every registered scene is REACHABLE from
the start scene, so an orphaned scene (registered in ``SCENES`` but pointed
at by nobody) would ship silently — playable copy the player can never see.

This sweep pins the graph truths at HEAD (3 scenes, all reachable):

* BFS over ``next_scene_id`` edges from ``START_SCENE`` covers ``SCENES``.
* Every scene offers at least one option (also enforced per-scene by
  ``Scene.__post_init__``; pinned here at the catalog level so the sweep
  stands alone).
* The model has NO explicit terminal marker — an option with
  ``next_scene_id=None`` "ends the beat" (``dnd_workflow.choose`` sets
  ``ended = next_scene is None``) while the state STAYS at the scene. A
  scene whose options are ALL ``None`` is therefore a sink; the only sink
  today is ``treeline_watch`` (the escort's end-of-beat), and it is pinned
  as deliberate: like every scene, it still offers its narrate-only safe
  default, so a sink is a stay-put ending, never a stuck state.
"""

from __future__ import annotations

from collections import deque

from games.dnd.data.scenes import SCENES
from services.dnd_workflow import START_SCENE


def _edges(scene_id: str) -> set[str]:
    """The scene's outgoing ``next_scene_id`` edges (``None`` = stay/end)."""
    return {
        opt.next_scene_id
        for opt in SCENES[scene_id].options
        if opt.next_scene_id is not None
    }


def _reachable_from_start() -> set[str]:
    seen = {START_SCENE}
    queue = deque([START_SCENE])
    while queue:  # bounded: each scene enqueued at most once
        for target in sorted(_edges(queue.popleft())):
            if target not in seen:
                seen.add(target)
                queue.append(target)
    return seen


def test_start_scene_is_registered() -> None:
    assert START_SCENE in SCENES
    assert START_SCENE == "waystation_road"  # the walking-skeleton anchor


def test_every_scene_is_reachable_from_the_start_scene() -> None:
    reachable = _reachable_from_start()
    orphans = set(SCENES) - reachable
    assert not orphans, (
        f"scenes registered in SCENES but unreachable from {START_SCENE!r} "
        f"via next_scene_id edges: {sorted(orphans)}"
    )
    assert reachable == set(SCENES)


def test_every_scene_offers_at_least_one_option() -> None:
    for scene_id, scene in SCENES.items():
        assert len(scene.options) >= 1, f"scene {scene_id!r} has no options"


def test_no_edge_dangles() -> None:
    # Complements the import-time _assert_transitions_resolve(): keeps the
    # invariant red in CI even if that import-time assert is ever removed
    # (or stripped by python -O, which drops asserts).
    for scene_id in SCENES:
        for target in _edges(scene_id):
            assert target in SCENES, f"{scene_id!r} -> dangling {target!r}"


def test_sink_scenes_are_deliberate_ends_not_dead_ends() -> None:
    sinks = {scene_id for scene_id in SCENES if not _edges(scene_id)}
    # Pin the current graph: exactly one sink — the escort's end-of-beat.
    # A NEW sink appearing here is not necessarily a bug, but it must be a
    # decision: extend this pin if the story means to end there.
    assert sinks == {"treeline_watch"}
    # A sink still ends safely: every scene's clamp default is a stay-put
    # (next_scene_id None) option, so no scene — sink or not — can strand
    # the player mid-transition.
    for scene_id, scene in SCENES.items():
        default = scene.option(scene.default_option_id)
        assert default.next_scene_id is None, (
            f"scene {scene_id!r}: safe default {default.id!r} unexpectedly "
            f"moves the player (next_scene_id={default.next_scene_id!r})"
        )
