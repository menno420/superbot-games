# 2026-07-14 · night test — sim-harness smoke registry: every sim's render path executes in CI

> **Status:** `in-progress`
>
> 📊 Model: Fable · 2026-07-14T02:15:35Z · night-sim-smoke-registry

Test slice implementing the sim-harness smoke registry idea from
`.sessions/2026-07-14-night-coverage-encounters-sim.md` (verified
unimplemented at main `5fde718` — no `test_sim_harnesses.py` exists).
The gap it closes is exactly how #106's `format_report(SimReport())`
`ZeroDivisionError` stayed latent: every balance harness's `__main__`
entry is `pragma: no cover` and its full-scale run is manual, so nothing
executed the render paths end-to-end in CI.

Plan: one parametrized registry of (sim module, tiny sweep kwargs)
pairs — `games/mining/sim/encounters_sim`,
`games/shared/sim/economy_sim`, `games/fishing/sim/catch_sim`,
`games/dnd/sim/menu_sim`, and the exploration survival sim (exact
module path confirmed this session: `games/exploration/survival/sim.py`
— NOT a `*_sim.py` name) — asserting `format_report(run(**tiny_kw))`
returns non-empty text without raising. Kwargs kept tiny (each sim
measured <0.05s at the chosen bounds this session). Plus a glob-derived
completeness check: every `*_sim.py` under `games/` (test files
excluded) must be enumerated by the registry, so a new sim cannot dodge
the smoke. Home: `tests/shared/sim/` (the registered shared-sim suite),
floor bumped + `docs/balance.md` regenerated in the same push
(gen-balance gate).

Self-release note: this slice's claim file
(`control/claims/night-sim-smoke-registry.md`) is deleted in this
card's flip commit, per the established precedent.
