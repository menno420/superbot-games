# game-mining — founding plan

> **Status:** `plan` — founding brief, manager-seeded 2026-07-09

## Mission

Own the **mining domain** end-to-end: re-home superbot's deepest game system as a clean,
Discord-free plugin package that superbot-next consumes, then grow it — grid encounters, a
shared encounter engine, and eventually a paper-doll character renderer. Mining is
superbot's richest domain (equipment/wear, energy, grid dig, vault, structures, skills,
forge/workshop, titles, loadouts, descend/ascend, character); this Project makes it a
product of its own instead of a pending tail.

## The work

### 1. The deep-systems port (the D-0043 successor port)

superbot-next's decision D-0043 shipped mining's core loop and declared the full
37-command surface, leaving the 27 deep-system commands as honest pending terminals — the
**named successor port**. That port is this Project's first deliverable:

- **Oracle:** the old superbot code — `disbot/utils/mining/` (17 modules, ~4,895 lines by
  D-0043's accounting) plus `disbot/services/mining_workflow.py` (~1,430 lines) in
  `menno420/superbot`. Shipped behavior is the spec; when a doc and the oracle disagree,
  the oracle wins.
- **Target:** superbot-next's manifest/plugin contract. That contract is **in flight**
  there (superbot-next's inbox ORDER 002). **Until it lands, work stays plugin-side:** a
  pure-domain package — Discord-free core, injectable RNG/clock, unit-tested against
  oracle behavior — whose host-facing seams are designed to dock onto the contract when it
  arrives, never blocked waiting on it.
- **Shape:** `games/mining/` — pure domain core (grid, energy, wear, skills, structures,
  workshop, market, rewards, titles, loadouts, character…), a workflow layer mirroring
  `mining_workflow`'s audited op seams, and a thin adapter boundary left open for the
  host contract.

### 2. Grid encounters — Q-0198 (BINDING)

Depth-gated sparse encounters on the grid mine, per the owner's decision (superbot router
Q-0198, 2026-06-28):

- **Loot/flavour-only first.** Combat is a **fast-follow that reuses the
  creature/deathmatch engine — never a third combat model.**
- **Live roll, not per-cell-deterministic** — the grid itself stays seed-deterministic,
  but encounters differ between two players' runs.
- Depth threshold / per-action chance / cooldown are config-driven and **sim-tuned**
  (sparse and gated, always: the surface bands stay calm so casual play is unchanged).
- Resolution via navigator buttons. Design capture: superbot
  `docs/ideas/mining-grid-encounters-2026-06-22.md`.

### 3. Shared encounter engine — `games/shared/`

Grid encounters (this Project), exploration encounters (the sibling Project), and
superbot's Q-0186 wild-encounters lane all want **one** encounter-resolution engine with
different triggers. It lives under `games/shared/`; **mining implements it first** (for
grid encounters), **exploration consumes it**. `games/shared/` is **claim-first** per
[docs/lanes.md](lanes.md) — claim before touching; interface changes are announced in
BOTH status files.

### 4. Later: paper-doll renderer

A character/paper-doll renderer (equipment visualization) is a named later layer. Capture
it as a design doc when its turn comes; do not schedule it ahead of the port.

## Hard rails — BINDING

- **No pay-to-win (Q-0039 / Q-0190).** The product is free for everyone, forever; power
  is earned, never bought.
- **All balance numbers sim-pinned before shipping** — superbot's `tools/sim` discipline:
  a tuning change cites simulated playthrough numbers committed alongside the change.
- **Q-0087 dual-track balance:** a few casual minutes a day earn real *capability*
  progression; grind earns *prestige and surplus*; grind is **never mandatory** for
  levels or core capability. A number that gates core capability behind grind-hours
  fails review.
- **Deterministic core:** pure, seedable state machines; RNG injected; playthroughs
  reproducible; balance changes testable.
- No production-bot writes; forward-only git; decide-and-flag, never wait.

## Roadmap

- **P0** — kit adoption per inbox ORDER 001 (adopt only if `.substrate/` doesn't exist
  yet — kit adoption happens ONCE per lanes.md; otherwise verify engagement); lane claim;
  oracle code study (`utils/mining` + `mining_workflow`, module by module); package-layout
  design doc.
- **P1** — the pure-domain port, with tests: module by module, oracle-behavior-pinned,
  Discord-free.
- **P2** — workflow seams mapped to the plugin contract (adapter boundary documented
  against superbot-next's contract as it lands).
- **P3** — grid encounters (loot/flavour first per Q-0198), built on the shared engine
  under `games/shared/`.
- **P4** — host integration when the superbot-next plugin contract lands.
- **P5** — live-test in the test guild.
