# control/inbox-exploration.md — orders to game-exploration

> **ONE writer: the manager.** Never edit this file. Report order progress ONLY in
> `control/status-exploration.md` (one writer per file — protocol: `control/README.md`).

## ORDER 001 · 2026-07-09T14:23Z · status: new
priority: P1
do: (1) Verify substrate-kit adoption (`check --strict` green) — adopt from
`menno420/substrate-kit` per its README ONLY if mining hasn't already done it; coordinate
via the docs/lanes.md once-only rule. (2) Read `docs/founding-plan-exploration.md` +
`docs/lanes.md` — both binding. (3) Correct your seeded `control/status-exploration.md`.
(4) Begin roadmap P0→P1: write the design docs for the quest/encounter engine (world
model, engine spec, shared-engine seam), then build the deterministic engine core with
sim tests.
why: founding order — stand the exploration Project up on its lane.
done-when: status-exploration.md reports acked=001 and the engine design doc + the first
engine PR merged.
