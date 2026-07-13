# 2026-07-13 · fishing standalone CLI (playable loop · build)

> **Status:** 🚧 `in-progress`
>
> 📊 Model: Opus 4.8 · 2026-07-13T01:26:25Z · fishing standalone CLI

## 💡 Session idea

Give the fishing ladder its missing player loop. Rung 1 shipped the pure core
(`games/fishing/core/` — the stateless catch resolver + species/spot data
tables), rung 2 shipped the audited WORKFLOW seam
(`services/fishing_workflow.py`, the single `cast` action over the game-neutral
`services/audit.py`), but nothing actually *drove* the seam — fishing was pure
functions with no way to sit down and cast a line. This session builds a
STANDALONE text CLI: `python3 -m games.fishing` (`games/fishing/__main__.py` +
`games/fishing/cli.py`), mirroring the just-landed mining standalone CLI's
structure exactly. It holds one mutable `FishingState` (assembled from REAL
core defaults — a full energy bar via `games.mining.core.energy.MAX_ENERGY`, the
in-table neutral `dock` spot, an empty haul) plus a module-level `InMemorySink`,
prints a status header (energy / current spot / haul summary), and dispatches a
focused command set — `cast`, `spot <id>`, `spots`, `status`/`haul`, `help`,
`quit` — to the one audited seam action. After each cast it prints the seam's
`FishingResult` narration, the updated energy, and the running haul; a too-tired
cast prints the core's honest 😴 no-bite message and records NOTHING (no crash).
On quit it prints a session summary (casts made, fish caught by species, audit
records recorded by the sink). The loop is factored so a test drives a scripted,
TTY-free session via `run_commands(commands, *, sink, state, now, rng)`;
`__main__` wraps an `input()` loop around the same `step`, handling EOF/quit
cleanly. NO balance number is changed — every bite chance / cost / weight / narration
is quoted verbatim from the seam/core; the only additions are UX/orchestration
(spot discoverability via the `spots` command + valid-id hints, a clear help
screen, and the session summary). Fishing tuning stays a SIM-REQUEST in
`control/outbox.md`. Tests land in `tests/fishing/test_cli.py`, bumping the
`tests/fishing` floor from 65.

## ⟲ Previous-session review

Builds directly on the 2026-07-13 fishing WORKFLOW seam card
(`.sessions/2026-07-13-fishing-workflow-seam.md`, #69), which landed
`services/fishing_workflow.py` (the single audited `cast` action) reusing the
game-neutral `services/audit.py` (`AuditRecord` / `Sink` / `InMemorySink`), and
on the mining standalone CLI card (`.sessions/2026-07-13-mining-standalone-cli.md`,
#70), whose `games/mining/cli.py` is the STYLE TEMPLATE mirrored here (a
`run_commands(commands, *, sink, state)` testable core + an `input()` loop in
`__main__`). The fishing seam card explicitly deferred any driver and left the
seam un-driven; this session adds the smallest honest driver — a standalone CLI —
so the fishing seam is provably playable end to end without waiting for the
plugin host. The fishing purity guard stays intact: the CLI lives at
`games/fishing/` (not under `core/`) and imports the seam, never the reverse.
The `tests/fishing` floor is bumped only for this suite; `services/tests` and the
other suites are left untouched.
