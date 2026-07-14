# world-games · status

updated: 2026-07-14T11:41:04Z
phase: EAP final-day closeout (ORDER 009) — COMPLETE: heartbeat truth-stamped (#138 `41e8a5b`), walkthrough doc ON MAIN (#139 `2969034`, docs/eap-closeout-walkthrough-2026-07-14.md), close-out summary + OWNER ACTIONS surfaced (control/outbox.md § EAP CLOSE-OUT); every other (a) item terminal or parked-with-citation below.
health: green — verified locally at HEAD ed2fabb this wake: `python3 -m pytest -q` = **810 passed** (exit 0); `python3 bootstrap.py check --strict` = all checks passed (exit 0); local/CI gate parity is by construction via `tools/preflight.py` (#128/#131/#133).
kit: substrate-kit v1.15.0 · check: green · engaged: yes
last-shipped: #139 — EAP closeout walkthrough docs/eap-closeout-walkthrough-2026-07-14.md (2969034, merged 2026-07-14T11:40:07Z), on top of #137 claim (e3930f1) + #138 heartbeat re-stamp (41e8a5b), all three enabler-merged on green this wake.
blockers: none — the remaining non-terminal items are externally gated and parked with citations (see "Parked" below).
orders: acked=001-009 done=001-007,009 (008 ACKED, not done — its done-when needs the full-roster batch SERVED: the fishing-full-roster + cook-leg SIM-REQUESTs are ROUTED to sim-lab via sim-lab's own ORDER 008 per at-HEAD ORDER 009 @ ed2fabb / fm PR #193 dispatch log, verdict pending, tracked below; 009 DONE — (a) heartbeat re-stamped + every item terminal-or-parked-cited via #138 `41e8a5b`, (b) walkthrough ON MAIN via #139 `2969034` with the OWNER ACTIONS checklist surfaced in control/outbox.md § EAP CLOSE-OUT — all three done-when clauses verified at main `2969034`)
⚑ needs-owner: 4 standing decisions, none new this wake — the OWNER ACTIONS checklist (deep links + bolded recommendations + VERIFY steps) is docs/eap-closeout-walkthrough-2026-07-14.md §C, surfaced verbatim in control/outbox.md § EAP CLOSE-OUT: (1) D2 audit-grants ratification · (2) rung-3 packaging/hermeticity · (3) persistence format-governance (3 sub-decisions) · (4) transfer-policy source model. RISK: all four are ↩️ reversible decision replies; no destructive click owed.
notes: doc-conflict recorded, not silently resolved — the seat brief calls this file an ARCHIVE, but the at-HEAD ORDER 009 (ed2fabb) explicitly requires this re-stamp; the order + the control/README.md bus grammar (this Project overwrites its own status.md each session, one writer per file) outrank the brief — same precedent as the ORDER 006 night-report and ORDER 007 ack sections (acked=007 via #84 9caf1b6). The superseded heartbeat (2026-07-12T10:16:22Z stamp + the ORDER 005/006/007 sections) is preserved in git history at ed2fabb per the overwrite-own grammar. Session card for the walkthrough branch → .sessions/2026-07-14-eap-closeout-walkthrough.md · telemetry → telemetry/model-usage.jsonl · work claim → control/claims/eap-order-009-closeout.md (landed via #137; released at session close on the walkthrough branch).

## Truth-stamp evidence — 2026-07-14T11:32Z (ORDER 009 (a))

Prior stamp: `updated: 2026-07-12T10:16:22Z`. Verified at main HEAD
`ed2fabbef58f3b97a03e6586a4e03ad0ab89c451` (`git ls-remote` 2026-07-14T11:20Z):
**77 squash-merges have landed since that stamp** (`git log
--since=2026-07-12T10:16:22Z origin/main`, subjects spanning #59…#136 — the
ORDER 009 premise "~35 PRs #87–#135" re-verified per Q-0120 and found
UNDERSTATED: #87–#135 alone is 49 merges). Zero open PRs and an empty
`control/claims/` at scan (API-verified 2026-07-14T11:24Z). The arc, wave by
wave (squash SHAs on main; per-PR enumeration lives in
`docs/current-state.md` § "Recently shipped"):

- #59–#64 — docs correction + kit v1.12.1 → v1.15.0 (`0082ee2`).
- #66–#80 — ALL FOUR GAMES PLAYABLE: rung-2 audited seams (#68/#69/#75/#77),
  standalone CLIs (#70/#71), hub `python3 -m games` (#72 `ef18b4e`);
  suite 310 → 516.
- #82–#87 — ORDER 007 sim verdicts V042–V045 consumed: V043 fishing economy +
  V044 dnd mint-once guard wired (#83 `72a94bb`), the four SIM-REQUESTs closed
  with dispositions (#84 `9caf1b6`), economy surfaced on docs/balance.md +
  fishing CLI `sell` (#87 `67de572`); suite → 556.
- #92/#93 — ORDER 008 landed + full-roster fishing SIM-REQUEST filed
  (`21937f3`).
- #95–#107 — night coverage/fix wave (suite → 606; CI-executed test count
  442 → 606 via #107 `24f6e04`).
- #108–#119 — CLI/hub/sim coverage, 3 player-visible fixes (#115/#116/#117),
  README refresh (#118), sim-harness smoke registry (#119); suite → 695.
- #120–#134 — hardening wave: tripwire registries (#122/#123/#126/#129/#132),
  shared REPL + scripted-driver seams (#127/#130/#134), preflight gate parity
  → one-command flip-readiness (#128/#131/#133); suite → **810**, coverage
  ~97% of games/+services at the #120 groom.
- #135 — current-state truth-stamp of that wave (`34c5b98`) · #102 — external
  fleet-cleanup audit doc (`1c323c1`) · #136 — ORDER 009 (`ed2fabb`).

## SIM-REQUEST routing — fishing full-roster + cook leg (ORDER 009 (a))

ROUTED: the `fishing-full-roster-economy` SIM-REQUEST (filed via #92
`21937f3`, folding in `fishing-cook-economy`, #89 `ab442e7`) is routed to the
sim-lab via sim-lab's own ORDER 008 today, per at-HEAD ORDER 009 (`ed2fabb`;
fm PR #193 carries the dispatch log). Both outbox entries flipped
`open` → `routed` this wake. Cross-repo verification of sim-lab's inbox was
attempted once and DENIED on this seat (verbatim: `Access denied: repository
"menno420/sim-lab" is not configured for this session. Allowed repositories:
menno420/superbot-games, menno420/superbot-idle`) — the routing citation is
the at-HEAD order itself. TRACK: wire the verdict's constants VERBATIM on
receipt (ORDER 008 precedence rule (c): correctness > speed; no numbers
invented meanwhile).

## Parked — honest, one line + citation each (ORDER 009 (a))

- exploration numeric band import — PARKED upstream: waits on the superbot P0
  survival balance-sim artifact (Q-0087 methodology / D-0008 artifact); V045
  ratified the placeholders with an honest NULL (control/outbox.md
  § exploration-reward-bands, closed; ORDER 007 item (4)).
- rung-3 host-adapter packaging + hermeticity — PARKED on the owner/lab
  build-model decision (docs/design/mining-host-adapter.md § "⚑ OWNER / LAB
  DECISION REQUIRED", scoped via #66 `60b2773`).
- standalone-CLI persistence (save/load), transfer-policy source model, and
  the D2 audit-grants ratification — PARKED on owner decisions
  (control/outbox.md § OWNER-QUEUE, filed via #73 `6ecd579`;
  docs/design/persistence-design.md §5 OWNER-DECIDES item 4;
  control/outbox.md § DECISION-NOTE · D1/D2).
- fishing full-roster + cook-leg constants — externally gated on the routed
  sim-lab verdict (section above); nothing implementable in-repo until it
  lands.
