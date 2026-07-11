# world-games · status
updated: 2026-07-11T19:39:14Z
phase: close-out + archive-prep — session archiving; no new feature work; all deliverables parked on branches for owner merge.
health: green — merged work green; 5 open PRs green+clean; `bootstrap.py check --strict` exit 0.
last-shipped: #49 — D&D menu-balance sim (no-pay-to-win sim-pinned). main HEAD 5d38593, kit substrate-kit v1.12.0.
blockers: none — the only gate is owner merge clicks (agent self-merge is platform-classifier-blocked; do NOT attempt).
orders: acked=001,002,003,004 done=001,002,003,004
⚑ needs-owner: see the OWNER-ACTION block below + docs/retro/archive-ready-2026-07-11.md
notes: self-review + lessons + chat-only knowledge → docs/retro/close-out-world-games-2026-07-11.md · archive resume spec → docs/retro/archive-ready-2026-07-11.md · per-PR state → control/claims/

## Open PRs — all green + clean + parked ⚑ (owner merge is the only path)
- #50 dnd-scene-chaining — D&D data-driven bounded scene transitions (next_scene_id is immutable DATA; DM still can't steer off-menu). Next: owner merge; then trivial tests/dnd floor rebase vs #52.
- #52 dnd-clamp-fuzz — seeded DM-clamp property-fuzzer (~1,200 adversarial cases: never raises, always clamps to no-op) + §9 production-DM-model addendum (Claude Haiku-4.5-class). Next: owner merge; floor rebase vs #50.
- #53 persistence-save-state-contract — save-state contract + owner transfer-policy mapping (docs). Next: owner merge; ⚑ transfer source-debit % OWNER-DECIDES (item 4).
- #54 economy-cross-domain-sim — games/shared/sim/economy_sim.py + invariants (GRANT_WITHIN_GLOBAL_CAP / ITEM_FAUCET_MINTS_NO_CURRENCY / NOOP_MINTS_NOTHING). Next: owner merge; then economy follow-up PR.
- #55 auto-balance-page — tools/gen_balance.py → docs/balance.md + CI freshness --check. Next: owner merge; then economy follow-up PR.

## ⚑ OWNER-ACTION
- WHAT: Squash & merge the 5 open PRs (#50, #52, #53, #54, #55). WHERE: github.com/menno420/superbot-games/pulls. HOW: each is READY+green — open, Squash & merge; if two collide on tests/dnd/EXPECTED_MIN_TESTS.txt, merge one then bump the other's floor 1 line. WHY-IT-MATTERS: agent self-merge is platform-classifier-blocked — only your click (or a direct in-session "merge" turn) lands them. UNBLOCKS: the improvement queue + the CLI demo. VERIFIED-NEEDED: CI green on each head (confirmed).
- WHAT: decide transfer-policy source model — TRUE source-debit vs seeded-credit (persistence §5, #53 OWNER-DECIDES item 4). WHERE: docs/design/persistence-design.md. HOW: reply the choice. WHY-IT-MATTERS: seeded-credit violates the doc's own conservation invariant (reviewer finding); working assumption = TRUE DEBIT. UNBLOCKS: cross-server transfer implementation. VERIFIED-NEEDED: none.
- WHAT (optional): enable a branch-protection merge queue. WHY-IT-MATTERS: serializes merges, removes the floor-file rebase churn between parallel PRs. UNBLOCKS: smoother future batches.
