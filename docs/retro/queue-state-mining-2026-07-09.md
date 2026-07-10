# Mining lane — roadmap / queue state (gen-1 wind-down, 2026-07-09)

> **Status:** `audit`
> Committed so nothing lives only in chat. Verified against GitHub 2026-07-09 ~20:00Z.

## DONE (on main)
- Kit engaged on main (substrate-kit v1.2.0) — via exploration PR #3 (mining consumes it).
- Mining retro + self-review docs — PR #9, MERGED.
- Orders 001 (kit+port+design shipped to PR), 003 (arbitration: #4 closed), 004 (retro merged).

## PARKED — green, awaiting owner merge (the classifier merge wall; see status ⚑)
- **PR #5** `mining/port-pure-domain` — the pure domain port: 18 modules → `games/mining/core/`,
  62 unit tests pass, `docs/design/mining-plugin-layout.md`. DRAFT, base main, mergeable_state=clean,
  substrate-gate SUCCESS (head 33808dd). This is P1 (the D-0043 successor port) — the lane's core deliverable.
- **PR #11** `mining/grid-encounters` — grid-encounters FIRST SLICE (pure domain), the mission's
  "extend: grid encounters first" goal, started. DRAFT, STACKED on #5 (base mining/port-pure-domain),
  mergeable_state=clean, substrate-gate SUCCESS (head 183e08d). Retarget to main after #5 merges.
- **PR #14** `mining/wind-down-2026-07-09` — this succession package. READY, substrate-gate green.

## CLOSED
- PR #4 `mining/adopt-substrate-kit` — CLOSED unmerged (redundant; kit-adoption race, exploration #3 won).

## NEXT (for gen-2, no owner needed to START — merges still need the wall cleared)
1. **Mint parity goldens** (ORDER 002, still 0 minted). The corpus has ~2 mining goldens for a
   37-command surface. Mint AS you port — the oracle mapping is only fresh once.
2. **`games/mining/workflow/` audited-op seam** — the composition layer mirroring `mining_workflow`'s
   one-transaction-per-op pattern (mine/dig/explore/descend). Pure core stays the decider; workflow is
   the sole write boundary (stubbed against the contract).
3. **superbot-next Layer-3 host adapter** — FIRST open superbot-next and VERIFY its plugin /
   SubsystemManifest contract (the gen-1 design doc assumed it). Then dock the pure core + workflow.
4. **Grid-encounters build-out** (Q-0198) — extend the #11 slice: three depth-band archetypes,
   loot/flavour first, combat as the deathmatch-core fast-follow; sim-pass before shipping.
5. **Economy sim + sim-pinned balance** — port superbot's mining economy sim; pin every balance
   number to a committed simulated playthrough before any tuning (hard rail, founding plan).

## Open lane question (⚑ owner)
- Aggregate `control/status.md` two-writer risk: the kit hardcodes a single `control/status.md`,
  but this repo runs per-lane status files. Owner: take the upstream kit fix or formalize the
  aggregate as manager-written.

## Gen-1 close-out (2026-07-10) — additive; the snapshot above is historical
- **All mining PRs are MERGED on main** (verified 2026-07-10): #5 (pure domain), #11 (grid-encounters),
  #14 (succession package), #15 (final status). The PARKED-awaiting-owner-merge section above is now
  historical — the merge wall was cleared by direct owner authorization; nothing of the lane's remains open.
- **ROUTINE STATE — NOT ARMED.** No scheduler tool was available this session
  ("No such tool available: mcp__claude-code-remote__send_later"), so no timed self-wake was scheduled.
  The next mining wake is **owner-initiated or webhook-driven (PR events)** — not a promised timer.
- **NEXT resume items (1–3) confirmed present above** and unchanged: (1) mint parity goldens;
  (2) `games/mining/workflow/` audited-op seam; (3) superbot-next Layer-3 `SubsystemManifest` host
  adapter — verify the plugin/manifest contract in superbot-next FIRST before docking.
