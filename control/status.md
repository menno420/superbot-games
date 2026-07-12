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
orders: acked=001,002,003,004,005 done=001,002,003,005
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
