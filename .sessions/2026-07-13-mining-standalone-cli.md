# 2026-07-13 · mining standalone CLI (playable loop · build)

> **Status:** 🚧 `in-progress`
>
> 📊 Model: Opus 4.8 · 2026-07-13T01:17:35Z · mining standalone CLI

## 💡 Session idea

Give the mining ladder its missing player loop. Rung 1 shipped the pure core
(`games/mining/core/`), rung 2 shipped the audited WORKFLOW seam
(`services/mining_workflow.py`), but nothing actually *drove* the seam — mining
was pure functions with no way to sit down and play. This session builds a
STANDALONE text CLI: `python3 -m games.mining` (`games/mining/__main__.py` +
`games/mining/cli.py`). It holds one mutable `MiningState` (assembled from REAL
core defaults — full energy bar, depth 0, 0 coins, the entry-tier pickaxe at
its core-defined max durability) plus a module-level `InMemorySink`, prints a
status header (coins / energy / tool+durability / depth / pack), and dispatches
a full command set — `mine`, `harvest`, `sell`, `buy`, `repair`, `descend`,
`ascend`, `build`, `vault`, `skill`, `status`/`inv`, `help`, `quit` — straight
to the ten seam actions. After each action it prints the seam's Result message
and the refreshed status; a blocked action prints the seam's honest message
(the torch-less descend surfaces `world.descend_hint` — the surface lock is now
DISCOVERABLE). The loop is factored so a test drives a scripted, TTY-free
session via `run_commands(commands, *, sink, state, now, rng)`; `__main__` wraps
an `input()` loop around the same `step`, handling EOF/quit cleanly and printing
a friendly session summary (actions taken, audit-record count, coins earned).
NO balance number is changed — every price/cost/weight/gate is quoted verbatim
from the seam/core; the only additions are UX/orchestration (economy tuning
stays a SIM-REQUEST in `control/outbox.md`). Tests land in
`tests/mining/test_cli.py` (+15), bumping the `tests/mining` floor 88 → 103.

## ⟲ Previous-session review

Builds directly on the 2026-07-13 mining WORKFLOW seam card
(`.sessions/2026-07-13-mining-workflow-seam.md`, #68), which landed
`services/mining_workflow.py` + the game-neutral `services/audit.py`
(`AuditRecord` / `Sink` / `InMemorySink`) and the ten wired actions. That card
explicitly deferred the host-adapter rung and left the seam un-driven; this
session adds the smallest honest driver — a standalone CLI — so the seam is
provably playable end to end without waiting for the plugin host. The purity
guard (`tests/mining/test_purity.py`, 19 modules) stays intact: the CLI lives at
`games/mining/` (not under `core/`) and imports the seam, never the reverse.
The `tests/mining` floor is bumped only for this suite; `services/tests` is left
untouched (a concurrent PR edits that floor).
