# 2026-07-14 · night fix — guard format_report against zero-action reports (mining encounters sim)

> **Status:** `in-progress`
>
> 📊 Model: Fable · 2026-07-13T23:42:47Z · night-fix-encounters-report-zerodiv

Bug-fix slice under the ORDER 008(b) production-grade standing directive,
picking up the one latent bug that #104's coverage slice (merge `a704e96`,
suite 606 passed) found and deliberately pinned rather than fixed:

- `games/mining/sim/encounters_sim.py` `format_report` — the
  kind-frequency lines divide by `report.actions` with no zero-actions
  guard, unlike `SimReport.encounter_rate` (which returns 0.0 when
  `actions` is 0) and unlike the per-depth branch (which renders `n/a`
  on a zero denominator). `format_report(SimReport())` therefore raises
  `ZeroDivisionError`, pinned by
  `tests/mining/test_encounters_sim.py::test_format_report_with_zero_actions_raises_zero_division`.

Plan: add the minimal guard mirroring the module's existing
zero-denominator conventions, and flip that one pinning test from
`pytest.raises(ZeroDivisionError)` to asserting the guarded output.
No other behavior changes; no gameplay constants touched.
