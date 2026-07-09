# 2026-07-09 · Adopt substrate-kit into superbot-games (mining lane, ORDER 001)

> **Status:** `in-progress`
>
> 📊 Model: Claude Opus 4.8 (1M context) · lane: game-mining · branch: mining/adopt-substrate-kit

## Goal

Execute mining inbox **ORDER 001** (P1): stand the mining Project up on its lane by adopting
`menno420/substrate-kit` (first adopter — no `.substrate/` existed) through `check --strict`
green, then correct the seeded `control/status-mining.md`. ORDER 002 acked in the same pass.

## What shipped

- **substrate-kit v1.2.0 adopted** — vendored `dist/bootstrap.py` at repo root; ran
  `bootstrap.py adopt` (planted CONSTITUTION.md, the binding-doc skeletons, living ledgers,
  `docs/AGENT_ORIENTATION.md`, `.sessions/`, `.session-journal.md`, `project.index.json`, and
  staged `.substrate/` packs).
- **Interview complete** — mode set to `active`; all 13 content slots filled with
  superbot-games-accurate content; `render --live` filled every planted doc (0 placeholders).
- **Engagement gate cleared** — wired the CI gate (`.github/workflows/substrate-gate.yml`
  runs `check --strict`); first session card (this file); real heartbeat in `control/status.md`.
- **Repo doc hygiene** — added a `Status: binding` badge to `docs/lanes.md`; linked the five
  repo docs (lanes, both founding plans, both buildability maps) from `AGENT_ORIENTATION.md`
  so they are reachable; stamp-discipline exception recorded for the external `D-0043`
  reference (a superbot-next decision cited in this repo's seed research/plan docs).
- **Status corrected** — `control/status-mining.md` rewritten to reality; ORDER 001 & 002 acked.

## First-adopter rough edges fixed

- **Heartbeat checker vs. multi-Project lanes.** `check_status_current` hardcodes
  `control/status.md`, but this repo's control/README multi-Project extension uses per-lane
  status files. Kept `control/status.md` as an aggregate heartbeat pointer to the per-lane
  files so `check --strict` stays green; flagged as a kit-side follow-up in the status file.
- **`render --live` is fill-only.** Re-answering an already-filled slot does not re-render its
  doc; corrected the one affected line in `docs/collaboration-model.md` by hand.

## Guard recipe (follow-up for the kit, not this repo)

Teach `src/engine/checks/check_status_current.py` per-lane heartbeat awareness (accept
`control/status-*.md` when a multi-Project `control/README.md` extension is present). Test
target: `tests/unit/substrate_kit/checks/test_status_current.py`. Until then, the aggregate
`control/status.md` pointer is the local workaround.

## 💡 Session idea

**Per-lane heartbeat awareness in the kit's status checker.** A shared repo hosting N
cohabiting Projects has N heartbeats, not one; the checker should recognise
`control/status-<lane>.md` files (gated on a multi-Project `control/README.md`) instead of a
single hardcoded `control/status.md`. Worth having because the multi-Project cohabitation
experiment this repo *is* will recur across the fleet, and the aggregate-pointer workaround
is drift-prone (two writers, one file).

## ⟲ Previous-session review

The previous session (#2, "buildability maps + ORDER 002") did the research and planning
well — the mining buildability map is thorough, source-pinned (superbot@7480a5f), and its
five recommended defaults map cleanly onto ORDER 002, which made acking 002 mechanical. What
it could have done better: it seeded `control/status-mining.md` with a placeholder but left
the kit unadopted, so the first real session inherited both the adoption *and* a status file
that failed the (not-yet-installed) heartbeat check. **System improvement:** the seed
templates and the kit's `check_status_current` disagree on the control-file layout for
multi-Project repos — resolving that in the kit (per-lane awareness) removes a guaranteed
first-adopter red for every future shared repo.

## Verification

`python3 bootstrap.py check --strict` → green (0 findings). CI: `substrate-gate` workflow runs
the same command on the PR.
