# world-games · status
updated: 2026-07-12T10:16:22Z
phase: docs-correction — landed a docs-only PR correcting stale "plugin contract in flight" claims; no feature-code change. Close-out/archive-prep from the prior wake still stands (5 feature PRs parked for owner merge).
ladder (per-slice, all four at PURE CORE — workflow/host-adapter rungs NOT yet built):
  - mining      — PURE CORE shipped (games/mining/core/, 96 tests). workflow (rung 2) = SCOPED-AND-FLAGGED (not built) pending a ⚑ audit-schema decision — see docs/design/mining-workflow-seam.md, PR #60 (READY + green). host-adapter = named-next.
  - exploration — PURE CORE shipped (games/exploration/, 55 tests). workflow + host-adapter = named-next.
  - dnd         — PURE CORE shipped (tests/dnd, 31 tests). workflow + host-adapter = named-next.
  - fishing     — PURE CORE shipped (tests/fishing, 64 tests). workflow + host-adapter = named-next.
  host-facing adapters can now be built against a CONCRETE contract: menno420/superbot-next docs/game-plugin-contract.md@d3dba9b (binding, ledger D-0056, owner decision 2026-07-09) — the "in flight" framing is corrected as of this PR.
health: green — main merged work green; local verify on the PR branch: tests/check_suite_floors.py TOTAL 310 (all floors met), pytest tests/ games/exploration/tests/ = 310 passed, tools/gen_balance.py --check clean, bootstrap.py check --strict exit 0 (after session card flipped complete).
last-shipped: kit substrate-kit v1.12.0 → v1.12.1 (#58). main HEAD 9efe599 (this branch is based on 5ddfbee/#58, which is fine; main has since advanced via fleet-manager PR #61 — see the Archival correction section below), kit substrate-kit v1.12.1.
open-PR (this wake): #59 docs/plugin-contract-binding-correction — docs-only correction of stale "plugin contract in flight" claims (README + docs/founding-plan-mining.md + docs/design/mining-plugin-layout.md §3 shape note). READY (not draft); auto-merge NOT armed. Branch head af8e9f2 (+ this heartbeat commit). CI: opened this wake; a born-red CI webhook right after the first push is expected noise (born-red session card, since flipped complete). Owner merge is the only path (agent self-merge is platform-classifier-blocked; do NOT attempt).
orders: acked=001,002,003,004,005,006 done=001,002,003,005,006 (004 satisfied — see ⚑ below; 006 = NIGHT REPORT section at end of this file)
⚑ needs-owner: ORDER 004 (self-review) — SATISFIED on main: artifact at docs/retro/close-out-world-games-2026-07-11.md (authored 201f8dd/#47, relocated at close-out 3a4eb98/#57); done=004 is backed by real, spec-compliant content, not a bare marker. Remaining owner items: the OWNER-ACTION block below + docs/retro/archive-ready-2026-07-11.md. ⚑ mining WORKFLOW seam (rung 2) — audit-schema decision (D1 which schema / D2 audit item-grants, a divergence from the oracle) needs owner/lab ratification; scoped in docs/design/mining-workflow-seam.md, PR #60.
notes: prior-wake self-review + lessons → docs/retro/close-out-world-games-2026-07-11.md · archive resume spec → docs/retro/archive-ready-2026-07-11.md · per-PR state → control/claims/ · session card → .sessions/2026-07-12-plugin-contract-binding-correction.md · telemetry → telemetry/model-usage.jsonl

## Archival correction — 2026-07-12T10:16:22Z (ORDER 005)
ARCHIVAL CORRECTION ONLY — not a resumption of the close-out lane, no feature work re-added; one dated stamp. The stale heartbeat (updated 2026-07-11T19:39:14Z), whose "5 parked PRs" framing is carried forward into the `## Open PRs` and `## ⚑ OWNER-ACTION` sections below, is SUPERSEDED on two points. Verified against live GitHub 2026-07-12 (GitHub API + `git ls-remote`):

- The five PRs listed as "OPEN, parked for owner merge" are all MERGED — the "Squash & merge the 5 parked feature PRs (#50/#52/#53/#54/#55)" owner ask is DISCHARGED (no owner click owed). Evidence (API-verified `merged_at` UTC · squash-merge commit on main):
  - #50 dnd-scene-chaining — MERGED 2026-07-11T20:25:22Z · commit 3250181
  - #52 dnd-clamp-fuzz — MERGED 2026-07-11T20:36:57Z · commit 7a355dc
  - #53 persistence-save-state-contract — MERGED 2026-07-11T20:25:17Z · commit 87530ba
  - #54 economy-cross-domain-sim — MERGED 2026-07-11T20:41:20Z · commit 2976538
  - #55 auto-balance-page — MERGED 2026-07-11T20:43:18Z · commit 320291b
- The stale `main HEAD 5d38593` claim (that SHA is the old #49 merge) is CORRECTED: live main HEAD is **9efe599** — "control: ORDER 005 — archival truth-stamp of the stale heartbeat (#61)". Main advanced past the five squash-merges above, then close-out #56/#57, kit #58 (5ddfbee), and fleet-manager PR #61 which deposited ORDER 005 into control/inbox.md (the commit main now points at).

Net: the close-out lane's deliverables all LANDED on main; nothing in the sections below remains open for owner merge. Current-state lines (the rung-2 ⚑ mining WORKFLOW/audit-schema decision, #59/#60 status) are unaffected by this stamp.

## Open PRs
- #59 plugin-contract-binding-correction — docs-only "in flight" → "binding at d3dba9b/D-0056" correction. READY + green. THIS WAKE. Next: owner merge (or leave; it's pure docs). Auto-merge NOT armed.
- #50 dnd-scene-chaining — D&D data-driven bounded scene transitions (next_scene_id is immutable DATA; DM still can't steer off-menu). Next: owner merge; then trivial tests/dnd floor rebase vs #52.
- #52 dnd-clamp-fuzz — seeded DM-clamp property-fuzzer (~1,200 adversarial cases: never raises, always clamps to no-op) + §9 production-DM-model addendum (Claude Haiku-4.5-class). Next: owner merge; floor rebase vs #50.
- #53 persistence-save-state-contract — save-state contract + owner transfer-policy mapping (docs). Next: owner merge; ⚑ transfer source-debit % OWNER-DECIDES (item 4).
- #54 economy-cross-domain-sim — games/shared/sim/economy_sim.py + invariants (GRANT_WITHIN_GLOBAL_CAP / ITEM_FAUCET_MINTS_NO_CURRENCY / NOOP_MINTS_NOTHING). Next: owner merge; then economy follow-up PR.
- #55 auto-balance-page — tools/gen_balance.py → docs/balance.md + CI freshness --check. Next: owner merge; then economy follow-up PR.

## ⚑ OWNER-ACTION
- WHAT: Squash & merge the 5 parked feature PRs (#50, #52, #53, #54, #55). WHERE: github.com/menno420/superbot-games/pulls. HOW: each is READY+green — open, Squash & merge; if two collide on tests/dnd/EXPECTED_MIN_TESTS.txt, merge one then bump the other's floor 1 line. WHY-IT-MATTERS: agent self-merge is platform-classifier-blocked — only your click (or a direct in-session "merge" turn) lands them. UNBLOCKS: the improvement queue + the CLI demo. VERIFIED-NEEDED: CI green on each head (confirmed prior wake).
- WHAT: ORDER 004 — owner-requested lane self-review (~24h) is SATISFIED (no action owed). WHERE: docs/retro/close-out-world-games-2026-07-11.md §"Self-review (last ~24h)" on main. HOW: authored 201f8dd/#47, relocated at close-out 3a4eb98/#57 where done=004 was set; the order's spec permits "control/status.md (or this lane's report convention)", so the retro location complies. WHY-IT-MATTERS: done=004 is backed by real, spec-compliant content, not a bare marker. VERIFIED-NEEDED: none.
- WHAT: decide transfer-policy source model — TRUE source-debit vs seeded-credit (persistence §5, #53 OWNER-DECIDES item 4). WHERE: docs/design/persistence-design.md. HOW: reply the choice. WHY-IT-MATTERS: seeded-credit violates the doc's own conservation invariant (reviewer finding); working assumption = TRUE DEBIT. UNBLOCKS: cross-server transfer implementation. VERIFIED-NEEDED: none.
- WHAT (optional): enable a branch-protection merge queue. WHY-IT-MATTERS: serializes merges, removes the floor-file rebase churn between parallel PRs. UNBLOCKS: smoother future batches.

## NIGHT REPORT 2026-07-13T09:22Z (ORDER 006 — owner ask 2026-07-13, fm relay)

> This file is a frozen archive; this section is written ONLY under the explicit
> at-HEAD ORDER 006 (control/inbox.md, landed via PR #78, merged
> 2026-07-13T09:10:43Z — API-verified). Window: 2026-07-12T22:30Z → 2026-07-13T09:22Z.

### SHIPPED (merges API-verified; squash SHA on main · merged_at UTC)
- #67 ci: auto-merge-enabler install (fm ORDER 029) — dd867c8 · 00:03:53Z
- #66 docs: rung-3 host-adapter scoping + ⚑ packaging decision — 60b2773 · 00:10:16Z
- #65 docs: truth-stamp current-state + 5 merged-claim sweep — 64b3371 · 00:14:25Z
- #68 feat(mining): rung-2 WORKFLOW audited seam (§5 D1/D2 default) — 1b09a03 · 01:07:34Z
- #69 feat(fishing): rung-2 WORKFLOW audited seam — 7c13166 · 01:20:15Z
- #70 feat(mining): standalone CLI `python -m games.mining` — da0e47e · 01:23:35Z
- #71 feat(fishing): standalone CLI `python -m games.fishing` — c491bd3 · 01:32:11Z
- #72 feat(hub): world registry + `python -m games` launcher — ef18b4e · 01:42:33Z
- #73 docs(control): persistence owner-queue entry — 6ecd579 · 01:56:10Z
- #74 docs: playable game entrypoints — 0e62ee3 · 02:03:58Z
- #75 feat(dnd): finalize — audited resolver seam + CLI + hub — 0ee7482 · 02:28:32Z
- #76 control: fm ORDER 037 stamp fix (status-mining) — 425a3d7 · 02:42:35Z
- #77 feat(exploration): finalize — audited quest seam + CLI + hub — 5aec110 · 02:46:24Z
- #78 control: ORDER 006 landing (manager-written) — dabba30 · 09:10:43Z
- Suite 310 → **516** — VERIFIED locally at HEAD dabba30: `python3 -m pytest tests/ games/exploration/tests/ services/tests/ -q` → 516 passed; `tests/check_suite_floors.py` TOTAL 516, all floors met.

### OPEN PRs + check states
- None — zero open PRs (API-verified 2026-07-13T09:15Z).

### ORDERS served + outstanding
- 001–005 done pre-window (004 satisfied via docs/retro/close-out-world-games-2026-07-11.md, see ⚑ above).
- fm ORDER 037 (fleet-manager inbox relay) served in-window via #76.
- 006 = this report. Outstanding: none.

### SIM-REQUESTs / asks pending (all in control/outbox.md unless noted)
- DECISION-NOTE D1/D2 — D2 audit-item-grants ratification (reversible divergence; one-line toggle if reversed).
- SIM-REQUEST mining-economy-tuning (descend gate + source/sink gap).
- SIM-REQUEST fishing-economy-tuning (empty economy + no in-domain progression).
- SIM-REQUEST dnd-escort-double-mint (one traversal mints safe_passage 2×).
- SIM-REQUEST exploration-reward-bands (Q-0087 reconciliation + survival Medium/Hard gradient).
- OWNER-QUEUE standalone-CLI persistence format-governance decision (3 coupled sub-decisions).
- ⚑ rung-3 packaging decision — docs/design/mining-host-adapter.md (scoped via #66).

### STALLS / denials (verbatim)
- None in this repo this window. (One auto-mode force-push denial occurred in a sibling repo during the night run and was handled by a normal commit — not this repo; lane-reported.)

### Wake-chain health (SEAT-LEVEL — one chain serves games/idle/mineverse; the order asks per-repo, the chain is per-seat)
- Failsafe cron `trig_0131tbQZs8HKmxKR4u5ZD1Hb` "SuperBot World failsafe wake", cron `15 1-23/2 * * *` — API-verified live 2026-07-13T09:16Z: enabled, last fired 09:15:25Z, next 11:15:00Z. Overnight fires 01:15/03:15/05:15/07:15 on schedule (lane-reported; API exposes only the last fire).
- send_later pacemaker chain continuous through the night; current tick `trig_01K5pWUeY1YEM6taMeWmHvG8` fires 09:19Z (API-verified live, bound to the seat coordinator session).
- One duplicate-tick incident ~02:35Z detected and pruned the same wake; anti-stack check added since (lane-reported).

### Next-3
1. Build on the D2/SIM-REQUEST answers as they land (wire sim-pinned numbers verbatim).
2. Rung-3 mining host-adapter if the packaging decision is ratified (docs/design/mining-host-adapter.md).
3. Generative polish wave (playability follow-ups) on owner green-light.
