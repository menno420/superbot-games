# 2026-07-14 · night test — test: dnd effects liveness — every effect reachable and executable

> **Status:** in-progress
>
> 📊 Model: Fable · 2026-07-14T03:45:24Z · night-dnd-effects-liveness

Test slice from #126's card idea (`.sessions/2026-07-14-night-dnd-scene-
reachability.md`, verified fresh: nothing in `tests/dnd/` sweeps
`games/dnd/core/effects.py`'s `EFFECTS` registry against the reachable
scene graph). `Scene.__post_init__` validates referenced-if-used, never
*used* — an orphaned pre-priced effect would ship silently as dead balance
data, and nothing executes each effect through the seam. Plan (≤8 tests in
`tests/dnd/`): every `EFFECTS` id is referenced by ≥1 option on a scene
BFS-reachable from `START_SCENE`; each effect executes once via
`services/dnd_workflow.choose` without raising; declared grant/mint
behavior pinned (narrate-only effects mint nothing; `escort_step` mints
exactly the engine's tier-capped bundle, and the #83 mint-at-most-once
guard stays intact — not weakened). An orphaned or raising effect is a
HEADLINE (pin + report, don't delete).
