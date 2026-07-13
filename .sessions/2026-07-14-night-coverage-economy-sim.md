# 2026-07-14 · night coverage — pin the economy ledger seam's untested paths (tests)

> **Status:** `in-progress`
>
> 📊 Model: Fable · 2026-07-13T22:59:58Z · night-coverage-economy-sim

Coverage slice under the ORDER 008(b) production-grade standing directive:
`games/shared/sim/economy_sim.py` — the cross-domain economy ledger that
enumerates every reward faucet and computes the three named global
invariants — sits at **75% coverage** (150 stmts, 37 missed) at main
`8b0b476` (re-verified this session; matches the 2026-07-13 scan at
`511fa91`). The missed lines are exactly the seam's alarm wiring: the
FAIL branches of all three invariant detectors (lines 323, 339, 345,
352–353 — never exercised, so a detector that silently returns True on a
violation would pass today's suite), the `_mean_surface_ore_coin_value`
empty-weights guard (173), the `report.domains` property (100), and the
entire `format_report` renderer (358–397).

Plan: focused tests only — prove each invariant detector actually trips
on a violating report (constructed via `dataclasses.replace` / targeted
monkeypatch, never by editing shipped constants), pin the report-shape
invariants, and pin `format_report`'s load-bearing lines (per-domain
rows, host-vs-numeric ceilings, PASS flags, pinned bands). Zero
gameplay-constant changes, no sim-verdict-needing surface.
