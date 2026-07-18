# Claim · claude-mining-broke-report-once

- **Branch:** `claude/mining-broke-report-once`
- **Scope:** Fix a real correctness bug in the mining WORKFLOW seam's wear helper
  (`services/mining_workflow.py::_apply_wear`). Its docstring promises `broke`
  names only the items that hit 0 durability "this tick", but the loop
  unconditionally decremented every worn slot with `max(0, durability - 1)` and
  reported any item whose value equalled 0 — so an item already at 0 (a broken
  tool still sitting in the equipped slot, which the seam does not clear on break)
  was RE-REPORTED as freshly broken on EVERY subsequent wearing action
  (`mine` / `explore` / `duel`). A player would see "your iron pickaxe broke!" on
  every dig after the first, not once. Fix: skip an already-broken (`durability
  <= 0`) slot entirely — it does not wear again and is not re-reported, so `broke`
  is honest. Surgical one-branch change + one regression test
  (`test_mine_reports_break_only_on_the_tick_it_breaks`, fails before / passes
  after); `services/tests` floor 216 → 217 + `docs/balance.md` regenerated (its
  Test-suite-floors section pins that count). No balance/economy number change; the
  audited seam's `target`/message strings are untouched.
- **Date:** 2026-07-18 (`date -u` = Sat Jul 18 00:30:49 UTC 2026)
- **Self-initiated:** ⚑ small game-improvement slice (owner night order 2026-07-18).
