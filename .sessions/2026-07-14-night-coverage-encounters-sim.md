# 2026-07-14 · night coverage — pin the encounter-sim percentile helper + balance-report renderer (tests)

> **Status:** `in-progress`
>
> 📊 Model: Fable · 2026-07-13T23:27:33Z · night-coverage-encounters-sim

Coverage slice under the ORDER 008(b) production-grade standing directive:
the mining grid-encounter balance harness, re-scanned this session at main
`e864a78` (592 passed):

- `games/mining/sim/encounters_sim.py` — **68%** (119 stmts, 38 missed;
  lines 97–101, 172–213): the sweep loop and the aggregate dataclasses are
  pinned by `tests/mining/test_encounters.py`, but `_percentile` (the
  reward-yield p50/p90 read the design doc quotes) and the entire
  `format_report` renderer — section order, the per-depth `n/a`
  zero-denominator branch, the empty-reward-kind skip, and the
  energy-line-only-when-triggered rule — are unpinned.

Plan: focused tests-only slice (roughly ≤14 tests in a new
`tests/mining/test_encounters_sim.py`) pinning real behavior of the missed
lines at EXISTING constants — invariants, edge/error paths, and the
renderer's skip/fallback branches; no gameplay-constant changes, no
features. Close-out will record coverage deltas, suite count from 592,
idea, and previous-session review.
