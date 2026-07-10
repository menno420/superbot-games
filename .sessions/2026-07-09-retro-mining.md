# 2026-07-09 · Mining lane self-review retro (ORDER 004)

> **Status:** `complete`
>
> 📊 Model: Claude Opus 4.8 (1M context) · lane: game-mining · branch: mining/retro-2026-07-09

## Goal

Execute mining inbox **ORDER 004** (P1, self-review retro) plus a wake-up self-unblock pass:
answer every question in `docs/retro/QUESTIONS.md`, reconstruct the Project's verified true
state for the owner's gen-2 redesign, and route the genuinely owner-only actions (the merges
the auto-mode self-approval guardrail blocks) to a click-by-click owner list.

## What shipped

- **`docs/retro/self-review-mining-2026-07-09.md`** — every question ID (A1–G3) answered,
  honest over flattering, each claim tied to a PR/commit/file. Headlines: nothing mining
  reached `main`; 0 parity goldens minted (ORDER 002 asked); the entire kit adoption (PR #4)
  is duplicate work lost to the parallel-adoption collision; the self-approval merge guardrail
  is the single blocker that nullified the session's output.
- **`docs/retro/project-review-2026-07-09-mining.md`** — verified true state (PRs #4/#5 read
  live: #4 is now `dirty` post-#3-merge, #5 clean-vs-#4, both CI-green, 62 tests pass), agent
  audit (coordinator + this session + 5 workers, deliverables verified against the repo),
  efficiency verdict, ⚑ owner actions (with the verbatim classifier denials + click-by-click
  merge steps), and the no-owner continuation plan.
- Linked both from `docs/retro/README.md`; retro PR **#9** opened READY (auto-merge NOT armed
  — merge is an owner action).

## Self-unblock disposition

- **Merge #4 → #5, merge #9:** owner-only under the current platform (the classifier twice
  refused agent self-approval of its own PRs). Routed to owner actions with verbatim denials.
- **ORDER 003 rebase of #4/#5:** agent-doable (not owner-only) but out of this retro's scope;
  flagged as continuation item 0 (it is the precondition for the owner's #4 merge, since #4 is
  conflict-dirty).
- **3 pre-existing `check --strict` findings on main** (lanes.md badge, D-0043 stamp allowlist,
  enforcement-unwired) — main merged the kit via #3 without the hygiene fixes that live on the
  unmerged #4/#8, so main fails its own check and has **no CI enforcement**. Not
  triplicate-fixed here: the CI-workflow install is owner-gated executable config, and the
  doc/allowlist fixes are already carried by the pending #4/#8. Flagged for the owner.

## 💡 Session idea

**Seed-time kit adoption + a real lock, not a convention.** The gen-1 kit-adoption collision
(both lanes adopted `substrate-kit` in parallel; ORDER 003 had to arbitrate) happened because
"adopt once" was a *convention* with no enforcement and the claim-first rule was scoped only to
`games/shared/`, not `.substrate/`. Fix for gen-2: the manager engages `.substrate/` at repo
birth so no lane races to adopt it, and the claim-first rule is reworded to cover **every**
shared surface with a checker-enforced lock file — a mechanism beats a habit.

## ⟲ Previous-session review

The previous mining session (the ORDER 001/002 build, PRs #4/#5) did the *core* work well: the
oracle study is thorough and the pure-domain port is faithful, verbatim, and 62-test-green —
exactly what a port should be. Two things it could have done better, both structural not
sloppy: (1) it adopted the kit without checking `docs/claims/` or open PRs first, so ~19
minutes of W1's work became the duplicate the ORDER 003 arbitration had to unwind — the
claim-first discipline exists precisely to prevent this; (2) it left #4/#5 **draft** awaiting a
merge convention the repo never stated, which stalled the PRs and, combined with the
self-approval guardrail, meant nothing shipped. **System improvement:** define an order's
done-when as an *agent-reachable* state ("PR open, READY, green") and put every merge/human
click the agent can't perform on an explicit owner-actions list at PR-open time — ORDER 001's
"first port PR merged" done-when was literally unreachable by the agent that was given it.

## Verification

`python3 bootstrap.py check --strict` → my additions are drift-neutral (0 new findings); the 3
remaining findings are pre-existing main state (documented above), plus the session-log line
which this completed card clears. Retro doc deliverables verified: `games/mining/core/` = 18
modules, `tests/mining/` = 62 passed, `docs/design/mining-plugin-layout.md` present; PRs
#4/#5/#3/#8/#9 state read live via the GitHub API.
