# superbot-games · status

updated: 2026-07-10T23:57:37Z
phase: single-seat unification — ORDER 001 (CI collection-scope fix + seat unification) in flight as a READY PR
health: green — main is strict-GREEN on kit v1.7.1; all 121 pure-domain tests pass locally
orders: acked=001,002 done=002

## Boot record
Landed on origin/main HEAD `b134961` (substrate-kit v1.7.1). This is the **unified
single-seat status file**, replacing the gen-1 pointer stub — one seat owns all of
`games/**` and reports here. The per-lane `control/status-mining.md` /
`control/status-exploration.md` files are now **GEN-1 HISTORY archives** (banners added
this session); do not resurrect the two-lane split.

## Orders
`orders: acked=001,002 done=002`
- ORDER 001 — **in progress → done-on-merge** of this PR (CI collection-scope fix + seat
  unification; see below).
- ORDER 002 — **done**.

### ORDER 001 — PR state
- branch: `order-001-collection-scope`
- what it changes: CI now collects **all** pure-domain suites (`tests/` +
  `games/exploration/tests/`) with a **121-count floor** so a dropped/renamed suite fails
  loudly instead of shrinking coverage silently; GEN-1 HISTORY banners on the five lane
  files; kit-version drift fix (v1.2.0 → v1.7.1) in the two archived status files; root
  README rewritten to single-seat reality (Q-0267 theme-readiness); this status file
  converted from the gen-1 pointer stub to unified status.
- PR: #24 https://github.com/menno420/superbot-games/pull/24
- CI: https://github.com/menno420/superbot-games/pull/24/checks

### ORDER 002 — supersession note
ORDER 002 predates owner directive Q-0265; Q-0265's continuous send_later-chain +
cron-failsafe shape supersedes 002's hourly-Class-A cadence, not its task — routine
"superbot-games failsafe wake" (cron `15 */2 * * *`) armed by the coordinator seat.

## Routine / wake mechanics
Routine armed 2026-07-10T23:47:02Z by coordinator worker seat, verified via list_triggers (never trusted creation output alone):
- create_trigger(name="superbot-games failsafe wake", cron_expression="15 */2 * * *", persistent_session_id=coordinator session, prompt=exact Q-0265 failsafe text) → trigger id trig_019ZgWyL78Rx1sr6LhvL8NE3, enabled=true, next_run_at=2026-07-11T00:15:00Z, persist_session=true.
- list_triggers verification: matching entry confirmed; embedded prompt verified byte-for-byte: "FAILSAFE WAKE (superbot-games, Q-0265): if your send_later continuation chain is alive, verify that in one line and end. If it stalled, resume the work loop (sync HEAD -> inbox -> slice after slice, each merged-on-green) and re-arm the chain (~15 min) before ending."
- send_later chain link armed: message "continue the work loop", delay 15 min → {"fire_at":"2026-07-11T00:03:00Z","trigger_id":"trig_01KojfxKVb9sx63LPntSL9SJ"}.
- No denials; no walls hit.

## Queue (inherited)
- next: fishing walking skeleton reusing mining's encounter/energy substrate;
- then: unified inventory/resource contract;
- then: theme-slot audit per Q-0267.
