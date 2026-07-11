# superbot-games · status

updated: 2026-07-11T13:19:52Z
phase: ORDER-004 owner-requested lane self-review — committed to this file (below) and shipped as a READY PR parked ⚑ for the owner's merge click; five feature PRs remain green + parked ⚑ for owner merge
health: green — my five open PRs are CI-green; HEAD is main `a62fdf9` (substrate-kit v1.11.0). Full pure-domain suite passes; `bootstrap.py check --strict` exit 0
last-shipped: #24 (ORDER-001 CI collection-scope fix, merged); mining theme-leaks R1 #31 merged; five feature PRs now green + parked ⚑ (#34, #36, #38, #32, #27)
orders: acked=001,002,003,004 done=001,002
blockers: agent self-merge is classifier-blocked (coordinator-relay is not a live human turn) — five green PRs cannot land without an owner merge click or a direct in-session "merge them"
⚑ needs-owner: (1) FIVE green + reviewed PRs each need ONE merge click — order: #34 first (ends floor churn), then #36, #38, then #32 & #27 (these two need a quick rebase first); a direct "merge them" in the world-games session also clears the gate. (2) Model-attribution (ORDER 003): this lane records `📊 Model: Opus 4.8` (family-level, environment-reported) on session cards, never the exact internal id — confirm that family-level form is wanted, or say if "Claude Opus" is preferred. (3) No spend / publish / external-account / production-data actions taken; no secrets in repo — only decide-and-flag items were re-scoping #36 (documented) and building churn-fix #34.

## Order status
`orders: acked=001,002,003,004 done=001,002`
- **ORDER 001** — done (merged **#24**): CI collection-scope fix + count-floor assertion.
- **ORDER 002** — done (superseded by Q-0265).
- **ORDER 003** — delivered pending its PR merge: session cards now carry a family-level
  `📊 Model:` line (e.g. this cycle `📊 Model: Opus 4.8`), never the exact internal id, per
  the operator's don't-embed-the-id rule. Standing rule kept.
- **ORDER 004** — delivered as this `## Self-review 2026-07-11` section, pending merge to
  main (this PR parks ⚑ for the owner's click; the section reaches main on that click).

## Open PRs (all green — parked ⚑ for owner merge; agent self-merge classifier-blocked)
- **#34** `ci-floor-and-doc-index` — clean, **MERGE FIRST** (per-suite `EXPECTED_MIN_TESTS.txt`
  floors + per-domain doc indexes; ends the shared-bookkeeping merge churn).
- **#36** `theme-remediation-mining-r2` — clean (Q-0267 R2 remainder: capacity/world copy → data).
- **#38** `dnd-story-design` — clean (docs-only D&D bounded-menu design).
- **#32** `survival-sim-harness` — needs a quick rebase, then green (exploration P2 survival sim).
- **#27** `theme-readiness-audit` delta — needs a quick rebase, then green (delta supplement to #28).

## Merge-path ruling (recorded — not acted on this lane)
- **Independent review:** the coordinator's ruling is that a non-author seat posts an
  independent review as **issue comments** on the five PRs (comment-only; dispatched to
  another seat). PRs then stay **parked reviewed + green ⚑ owner-click**.
- **Fleet-manager "fresh worker session, one merge attempt" suggestion is EXPLICITLY NOT
  ADOPTED for this lane.** Our denials named coordinator-relayed authorization as the ground;
  a fresh session inherits the same authorization chain → deny-wins reads it as a
  retry-around. No merge attempts from this lane without a **live human turn**. (The
  fleet merge-path note exists; this lane records it and holds.)

## Honest gap
This lane produced no output ~02:15Z → ~11:xxZ. The merge-hold itself was decided policy —
but the inbox went **unread** across that window (ORDERs 003 filed 03:32Z and 004 filed
09:59Z sat unconsumed) and status.md went **stale** (last written 01:49Z). That is a routing
miss, stated plainly and owned.

## Forward queue (sibling's, preserved + mine)
- **done:** ORDER-001 CI fix (#24, merged); fishing skeleton (#25); inventory contract design
  (#26); theme-slot audit (#28); exploration audit clean (#28); inventory seam PR-1 (#29);
  mining narration R1 (#31, merged); inventory migration PR-2 fishing adapter (#33); fishing
  spot biomes (#35); mining theme leaks R2 (#36, open); survival sim harness (#32, open);
  D&D story design (#38, open); churn-fix ci-floor+doc-index (#34, open).
- **next:** land **#34 first** (ends floor churn), then #36, #38, then rebase + land #32 & #27.
  Then the **D&D walking-skeleton** (one-scene `games/story/` package + DM-clamp test — held
  until #34 lands so it bumps only its own per-suite floor). Then the **#27/#32 rebases**.
- **inventory migration (inherited):** **PR-3** mining catalog adapter (closes Q-0267 §1a gap)
  → **PR-4** quest adapter → **PR-5** encounter typed grant → **PR-6** fish→mining bridge fix.
- **theme-audit roadmap (inherited):** R3 fishing status scaffold; R4 de-dupe count-in-prose.
- **deferred (inherited, §7):** richer fishing species table + multi-cast state (streaks,
  per-spot depletion).

## Self-review 2026-07-11

Owner-requested fleet-wide self-review (ORDER 004, P1). Scope: this world-games lane,
2026-07-10 ~20:00Z → now.

### (1) What went wrong (last ~24h)
- **Shared-checkout worker race.** Two git-mutating workers in the same checkout collided:
  one worker's `git commit --amend` + `git reset --hard` clobbered the other's branch.
  Recovered from dangling commit `fd091af`; nothing bad was pushed. Fixed: all git-mutating
  workers now use isolated worktrees. (branch `survival-sim-harness` / PR #32; team memory
  `parallel-git-workers-need-worktree-isolation`.)
- **Agent self-merge blocked on every attempt** by the auto-mode classifier, verbatim:
  "[Self-Approval]/[Merge Without Review] ... authorized only by an untrusted coordinator
  relay — not a direct user turn". Expected wall, not a bug. Consequence: all five lane PRs
  park ⚑. (#27 / #32 / #34 / #36 / #38.)
- **Merge-conflict churn.** Every feature PR edited shared bookkeeping (`control/status.md`,
  `docs/current-state.md`, the hardcoded `tests.yml` count floor), so each sibling merge
  re-dirtied every open PR; **#32 went green→dirty ~3×**. Root-caused + fixed by **#34**
  (per-suite `EXPECTED_MIN_TESTS.txt` floors + per-domain doc indexes) — but #34 is itself
  parked ⚑, so the fix is not live yet.
- **Routing / heartbeat gap.** No lane output ~02:15Z → ~11:xxZ; ORDER 003 (filed 03:32Z) and
  ORDER 004 (filed 09:59Z) sat unconsumed; status.md went stale (last written 01:49Z). Routing
  miss, owned.
- **Stale-checkout residue.** A worker race left a large uncommitted revert in the main
  checkout; discarded safely (all valuable work was on remote branches), tree cleaned, 6 stale
  worktrees pruned.
- **Theme-remediation premise miss, self-corrected.** The ORDER-scoped `encounters.py`
  extraction was already merged by a sibling (**#31**); the worker caught it and re-scoped to
  the genuine R2 remainder (**#36**) instead of fabricating a proof.

### (2) Requiring owner attention (⚑, click-level, plain)
- **⚑ FIVE PRs are green + reviewed and need one merge click each** (agent self-merge is
  classifier-blocked): merge **#34 first** (ends floor churn), then **#36**, **#38**, then
  **#32** & **#27** (these two need a quick rebase first). Alternative: a direct "merge them"
  instruction in the world-games session clears the gate and the lane lands all five in order.
- **⚑ Model-attribution (ORDER 003):** the lane records `📊 Model: Opus 4.8` (family-level, the
  environment-reported family) on session cards, never the exact internal id, per the
  operator's don't-embed-the-id rule — confirm that's the family-level form wanted, or say if
  "Claude Opus" is preferred.
- **⚑ No spend / publish / external-account / production-data actions taken; no secrets in
  repo.** Only decide-and-flag items were: re-scoping #36 (documented) and building the
  churn-fix #34 design.

### (3) Health (one line)
World-games seat is green: this cycle produced 6 PRs (**#24 merged**; **#27, #32, #34, #36,
#38** green + parked ⚑); Q-0267 mining R1 (#31) + R2 (#36) done, exploration audited clean
(#28), D&D story game designed (#38); next is the D&D walking-skeleton (held until #34 lands)
+ the #27/#32 rebases.

## Boot record
This seat is the world-games single seat and reports here (single-writer status file). Landed
on origin/main HEAD `a62fdf9` (substrate-kit v1.11.0, #45). Owns all of `games/**`.
