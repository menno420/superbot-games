# game-mining · status

> **⟵ GEN-1 HISTORY.** The two-lane split is archived; the single world-games seat owns `games/**` and the unified `control/inbox.md` + `control/status.md`. Read this as an archive, do not resurrect the split.

updated: 2026-07-11T (archive-prep VERIFY + TOP-UP; verified against main HEAD 5d38593)
phase: gen-1 mining complete — ARCHIVE-READY. Pure domain + grid-encounters first slice shipped to main. Gen-1 lane is closed and archived; gen-2 boots only from what is committed on main. Archive note: docs/retro/archive-ready-2026-07-10-mining.md (verified true state, ⚑ owner-actions, resume read-order, gen-2 next 1–3 with block status, cross-project D-0043 wait).
health: green — main is strict-GREEN. 73 mining tests pass; `bootstrap.py check --strict` exit 0. All mining PRs are MERGED; nothing parked, nothing broken.
kit: substrate-kit v1.7.1 — adopted on main by exploration's PR #3 (merged); mining CONSUMES it ("adopt once" per docs/lanes.md). Mining's own adoption PR #4 was CLOSED as redundant (kit-adoption race — exploration filed first).
routine: NOT ARMED — no scheduler tool available this session ("No such tool available: mcp__claude-code-remote__send_later"); no timed self-wake was scheduled. Next wake is owner-initiated or webhook-driven (PR events). Gen-2 boot docs: `docs/retro/next-boot-mining-2026-07-09.md` (read FIRST) → `docs/retro/queue-state-mining-2026-07-09.md` (done/next).

last-shipped / merged (mining lane — all on main, verified 2026-07-09):
- #9 mining/retro-2026-07-09 — MERGED. Mining retro + self-review docs.
- #5 mining/port-pure-domain — MERGED. The pure-domain port: 18 modules → `games/mining/core/` (character, energy, capacity, equipment, items, exploration, grid, encounters, …) + unit tests; `docs/design/mining-plugin-layout.md`. The D-0043-successor port — the lane's core deliverable.
- #11 mining/grid-encounters — MERGED. Grid-encounters first slice (pure domain): `games/mining/core/encounters.py` + `games/mining/sim/encounters_sim.py` + `docs/design/mining-grid-encounters.md`. 73 mining tests total on main.
- #14 mining/wind-down-2026-07-09 — MERGED. Gen-1 wind-down succession package (see notes).

pr-in-flight (mining lane): none. All mining PRs are terminal (merged, except #4 closed-unmerged).

orders (control/inbox-mining.md): acked=001,002,003,004,005.
- 001 (kit + port + design) — DONE (port + design shipped and merged, #5).
- 002 (buildability-map defaults as working plan) — ACKED, defaults adopted; grid-encounters slice shipped under it (#11). Carried to gen-2: parity goldens still 0 minted (see next).
- 003 (kit-adoption arbitration — #4 closed) — DONE.
- 004 (self-review retro) — DONE (merged #9).
- 005 (P0 latency ping) — historical/stale; the gen-1 mining session predated it and the ping-ack that landed (#12) was exploration's. Not re-run — recorded honestly.
- No new wind-down/succession *inbox order* exists — the wind-down was delivered as PR #14's docs (succession package), not an inbox order. Acknowledged here.

⚑ needs-owner:
- **Model-line vs. no-id-in-artifacts conflict — OWNER-DECISION pending.** The kit's strict gate (PL-004 session telemetry) hard-requires a `📊 Model:` line on every session card, which brushes against the standing "no model identifier in any repo artifact" rule. WHAT: pick a formal resolution. WHY-IT-MATTERS: without a ruling agents guess whether the card line violates the rule. FIX OPTIONS: (a) kit carve-out — family-level model line is the ONE sanctioned place a model family may appear (never exact internal id, never in commit/PR text); or (b) amend the standing rule to name that carve-out. UNBLOCKS: the last ambiguity between staying CI-green and the no-id rule. OWNER-ONLY: yes (doctrine ruling). CURRENT RESOLUTION IN FORCE: family-level `📊 Model:` kept in the CARD only (never commit/PR text) to stay CI-green — already delivered fleet-wide as ORDER 003 (#46) and flagged in control/status.md ⚑ item (2). Evidence: any recent .sessions/*.md card + `bootstrap.py check --strict` gate behavior. So the conflict is CAPTURED with a working resolution; only the formal ruling is outstanding.
- Aggregate `control/status.md` single-file kit item (standing, now practically moot). Kit hardcodes a single `control/status.md`; gen-1 mining ran per-lane files. The fleet has since moved to a single world-games writer of `control/status.md`, so no mining action depends on this; recorded for completeness only.
- The gen-1 merge-wall ⚑ is RESOLVED — the owner authorized review-and-merge; #5/#11/#14 all landed. No open owner-click merge actions remain.

self-initiated (flagged, veto-able):
- Grid-encounters balance numbers are NEW sim-pinned design, not oracle-preserved — flagged for veto; re-tunable via `games/mining/sim/encounters_sim.py`.
- Single-exchange combat now; multi-turn combat deferred to the gen-2 build-out.
- Depth-gate / cooldown enforcement deferred to the workflow layer (pure core stays the decider).

next (no owner needed to START — the gen-2 / successor mining backlog, aligned with docs/retro/queue-state-mining-2026-07-09.md):
1. Mint parity goldens (ORDER 002, still 0 minted) — mint AS you port; the oracle mapping is only fresh once. Corpus has ~2 mining goldens for a 37-command surface.
2. `games/mining/workflow/` audited-op seam — the composition layer mirroring `mining_workflow`'s one-transaction-per-op pattern (mine/dig/explore/descend); pure core decides, workflow is the sole write boundary.
3. superbot-next Layer-3 host adapter — FIRST open superbot-next and VERIFY its plugin / `SubsystemManifest` contract, then dock the pure core + workflow.
4. Grid-encounters build-out (Q-0198) — extend the #11 slice: three depth-band archetypes, deeper combat (multi-turn, death/flee mechanics), loot/flavour first; sim-pass before shipping.
5. Economy sim + sim-pinned balance + parity goldens — port superbot's mining economy sim; pin every balance number to a committed simulated playthrough before tuning (founding-plan hard rail).

notes: docs/founding-plan-mining.md + docs/lanes.md remain BINDING. Gen-2 first-boot guide: read `docs/retro/next-boot-mining-2026-07-09.md` FIRST (first-10-minutes guide + walking-skeleton check + every known wall with verbatim errors), then `docs/retro/queue-state-mining-2026-07-09.md` (done/in-flight/next) and `docs/retro/gen2-feedback-mining-2026-07-09.md` (structural changes gen-2 should make). The wind-down's explicit contract: terminal state for good agent work is "PR open, READY, CI green, ⚑ owner-click" — parking correctly is a success, not a stall. Model of this final-status session: claude-opus-4-8[1m].
