# superbot-games · status

updated: 2026-07-11T00:21:47Z
phase: fishing walking skeleton shipped — READY PR to main (green-pending), builds on merged ORDER 001 (#24) unified base
health: green — full suite 147 pure-domain tests pass (99 tests/ [73 mining + 26 fishing] + 48 games/exploration/tests/); `bootstrap.py check --strict` exit 0
orders: acked=001,002 done=002

## Boot record
Landed on origin/main HEAD `b134961` (substrate-kit v1.7.1). This is the **unified
single-seat status file**, replacing the gen-1 pointer stub — one seat owns all of
`games/**` and reports here. The per-lane `control/status-mining.md` /
`control/status-exploration.md` files are now **GEN-1 HISTORY archives** (banners added
this session); do not resurrect the two-lane split.

## Last shipped — fishing walking skeleton (2026-07-11)
- `games/fishing/` pure package (mirrors `games/mining/core`): deterministic catch
  resolver (`resolve_cast`, NO LLM), a neutral-id species theme-data table (Q-0267), an
  independent fishing-salted splitmix64 stream, and a sim-pin harness. 26 tests under
  `tests/fishing/` (collected by the `tests/` root). Design doc
  `docs/design/fishing-catch-skeleton.md`. Branch `feat/fishing-skeleton`, PR to `main`.
- **Substrate REUSED (imported directly):** `games.mining.core.energy` (a cast spends
  `CAST_COST` through the shared engine) + `games.mining.core.equipment.EffectiveStats`
  (`fishing_power`/`bite_luck`, Q-0175 — the only advantage levers). **EXTENDED (new
  independent pattern):** the fishing-salted splitmix64 stream + species theme table +
  catch resolver/sim, mirroring mining's determinism + sim-pin patterns.
- **CI:** fishing tests sit under `tests/fishing/`, already collected by the merged #24
  workflow's hardcoded `tests/` root — the floor was raised 121 → 147 (added
  "+ 26 (tests/fishing/)") so a dropped fishing suite trips it loudly. Builds ON #24's
  all-suites-collection + count-floor, not around it.
- **⚑ needs-owner:** if branch protection walls the merge of an agent-authored unreviewed
  PR (expected Self-Approval wall), the owner clicks Merge once CI is green.

## Orders
`orders: acked=001,002 done=002`
- ORDER 001 — **done** (merged #24: CI collection-scope fix + single-seat unification).
- ORDER 002 — **done**.

### ORDER 001 — PR state
- branch: `order-001-collection-scope`
- what it changed: CI now collects **all** pure-domain suites (`tests/` +
  `games/exploration/tests/`) with a count floor so a dropped/renamed suite fails
  loudly instead of shrinking coverage silently; GEN-1 HISTORY banners on the five lane
  files; kit-version drift fix (v1.2.0 → v1.7.1) in the two archived status files; root
  README rewritten to single-seat reality (Q-0267 theme-readiness); this status file
  converted from the gen-1 pointer stub to unified status.
- PR: #24 https://github.com/menno420/superbot-games/pull/24 — **MERGED**.

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
- done: fishing walking skeleton reusing mining's energy/determinism substrate (this PR).
- next: unified inventory/resource contract;
- then: theme-slot audit per Q-0267.
