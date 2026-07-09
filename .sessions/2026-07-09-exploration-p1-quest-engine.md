# 2026-07-09 · exploration P1 — quest/encounter engine + kit adoption

> **Status:** `complete`

📊 Model: Claude Opus (Claude Code) — game-exploration lane

## Scope
Adopt substrate-kit (first-mover); build the deterministic quest/encounter engine (Lane C:
quest_service + EventBus-predicate progress, engine-not-content) with the v1 bounded-menu
catalog (5 templates x 3 reward tiers x Q-0087-band caps); define the shared encounter
interface in games/shared/encounter/; draft the D&D story-game plan (Q-0040 posture);
re-baseline survival D1 against shipped per-game energy.

## Progress
- **Kit adopted** (substrate-kit v1.2.0, first-mover); docs rendered, engagement scaffold
  in place; CI enforcement gate left STAGED under `.substrate/ci/` (cross-lane — flagged
  for coordination with the mining lane rather than installed unilaterally).
- **Engine shipped** — `games/exploration/quest/{rng,models,predicates,catalog,engine,leverage}.py`:
  pure/seedable, immutable state, engine-not-content. v1 bounded-menu catalog = 5 templates
  (fetch·escort·hunt·rescue·mystery) × 3 reward tiers, hard-capped + sim-pinned. Message-XP →
  DM menu-width leverage (`leverage.py`, 2→4, +1/500 XP, cap 4). 48 tests green incl. the
  balance-pin sim.
- **Shared encounter seam** — `games/shared/encounter/interface.py` (`EncounterResolver`
  Protocol + `EncounterRequest`/`EncounterOutcome` + `EncounterTrigger`
  GRID_ROAM/EXPLORE_ACTION/CHAT_ACTIVITY) with a deterministic reference resolver; mining
  owns the production core and replaces the reference via the Protocol. Announced in
  `control/status-exploration.md`.
- **Docs (this closing session):** wrote `docs/planning/dnd-story-game-plan.md` (closes the
  Q-0040 ship-gate, routes the bounded-authority decision to the owner) and
  `docs/design/survival-d1-rebaseline.md` (resolves the D1 byte-identical contradiction,
  recommends option (a)). Doc hygiene: added the "Lane docs, designs & plans" index to
  `docs/current-state.md`, a pointer in `docs/AGENT_ORIENTATION.md`, five decision-ledger
  entries (D-0002…D-0006), badge fix on the engine design doc, and the generic
  `control/status.md` thin pointer. Final `control/status-exploration.md` heartbeat written.

## Commits
- `55999f3` — D&D story-game plan + survival D1 re-baseline + doc hygiene + final status.
- (session-close commit flips this card to `complete` + deletes the two claim files.)

## 💡 Session idea
A deterministic **encounter/quest replay tool** — a tiny debug harness that takes a stored
`(world_seed, player_id, template_id, tier)` (and an event trace) and re-runs the pure engine
to reproduce the *exact* outcome for balance QA and bug repro. Because the core is pure and
seedable, any reported outcome is byte-reproducible offline — worth having so balance
regressions and "the DM gave me X" reports become one-command repros instead of guesswork.

## Previous-session review
This is the first real working session on the exploration lane, so the "previous session" is
the seed/adopt setup. It did the setup well: the seed commits (#1 founding plans + lanes
contract, #2 buildability maps + ORDER 002, plus the kit adopt) set up **clean, non-colliding
lanes** — the one-writer-per-file control protocol and the claim-first shared-code rule meant
this session never contended with the mining lane. One concrete workflow improvement surfaced:
the born-red session card + claim-first flow worked exactly as intended (the PR was visible
in-flight and the lane was claimed before building), but the **cross-lane CI-gate ownership**
was ambiguous — installing `substrate-gate.yml` would gate BOTH lanes' PRs, so a single lane
shouldn't install it unilaterally. Now explicitly flagged in `status-exploration.md`
(⚑ (4)) for manager coordination; the durable fix is for the fleet protocol to name which
actor installs shared/cross-lane enforcement.
