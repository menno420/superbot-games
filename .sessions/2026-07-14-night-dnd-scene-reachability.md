# 2026-07-14 · night test — test: dnd scene graph — reachability sweep from the start scene

> **Status:** in-progress
>
> 📊 Model: Fable · 2026-07-14T03:14:22Z · night-dnd-scene-reachability

Test slice from `.sessions/2026-07-11-dnd-scene-chaining.md` (verified:
`games/dnd/data/scenes.py:145` `_assert_transitions_resolve()` checks
dangling edges only — nothing checks that every scene is REACHABLE from
the start scene). Plan: a BFS sweep in `tests/dnd/` over the
`next_scene_id` graph from `START_SCENE`, plus data-level pins that
every scene has at least one option and that sink scenes (no outgoing
edges) are deliberate, not dead ends. ≤8 tests.
