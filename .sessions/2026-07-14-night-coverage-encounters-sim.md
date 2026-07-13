# 2026-07-14 · night coverage — pin the encounter-sim percentile helper + balance-report renderer (tests)

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-13T23:27:33Z · night-coverage-encounters-sim

Coverage slice under the ORDER 008(b) production-grade standing directive:
the mining grid-encounter balance harness, re-scanned this session at main
`e864a78` (592 passed): `games/mining/sim/encounters_sim.py` at **68%**
(119 stmts, 38 missed; lines 97–101, 172–213) — the sweep loop and the
aggregate dataclasses were pinned by `tests/mining/test_encounters.py`,
but `_percentile` (the reward-yield p50/p90 the design doc quotes) and the
entire `format_report` renderer were not.

Shipped 14 focused tests in `tests/mining/test_encounters_sim.py` (new).
`_percentile`: the empty-list 0.0 guard, singleton at any pct, input
sorting without caller-list mutation, the Python round-half-even median
(p50 of 10 items is the LOWER middle — pinned so a half-up
reimplementation reddens the doc'd yield table), and the clamp that
degrades pct > 1 to the max instead of IndexError. `format_report`:
section order across all seven headers, the fixed
none→hazard→loot_cache→rich_vein kind-row order and fresh→geared→veteran
tier-row order, the per-depth `n/a` zero-denominator branch, zero-total
tier rows rendering 0% via `HazardTierStats`' guards, the
empty-reward-kind skip (no 0-rows), the mean/p50/p90/max reward line at
exact formatting, thousands separators, the
energy-line-only-when-triggered rule, and end-to-end purity (same sweep
bounds → byte-identical report). Coverage: encounters_sim.py 68% →
**100%**; suite 592 → **606 passed**. Tests-only: zero gameplay-constant
changes, no features. **One latent bug found, pinned not fixed:**
`format_report(SimReport())` raises `ZeroDivisionError` — the
kind-frequency lines divide by `report.actions` without the zero-actions
guard that `SimReport.encounter_rate` has; the test pins the current
raise with a comment so a silent behavior change is impossible.

## 💡 Session idea

The `__main__` entry of every balance harness is `pragma: no cover` and
its full-scale run is manual — which is exactly how the
`ZeroDivisionError` above stayed latent: nothing ever executed the
renderer end-to-end in CI. Add a **sim-harness smoke registry**: one
parametrized test module (e.g. `tests/shared/test_sim_harnesses.py`) with
a registry of (sim module, tiny-bounded-sweep kwargs) pairs —
`games/mining/sim/encounters_sim`, `games/shared/sim/economy_sim`, and
every future `*_sim.py` — asserting `format_report(run(**tiny_kw))`
returns a non-empty string. That keeps every design-doc-cited harness
importable and renderable forever at ~0.3s each, and a new sim costs one
registry line. Dedupe check against recent cards: the telemetry outcome
backfill, the CI coverage ratchet, the detector-trip registry, and the
display-table completeness registry are all about data/table/invariant
sync — none executes the sim harnesses' render path; no card idea to
date does.

## ⟲ Previous-session review

The previous session is the #100/#101 wave, re-verified against
`origin/main`: #100 (squash `c27b25a`) released the
night-coverage-economy-sim claim exactly as promised — control-only
deletion, fast lane, and the claim file is indeed absent from HEAD. #101
(squash `e864a78`) delivered the naming/taxonomy slice its card
describes: this session's baseline scan at `e864a78` collected **592
passed** (matching the card's 578→592), and a fresh coverage replay this
session showed `games/mining/core/names.py` **100%** (19 stmts, 0
missed) and `games/mining/core/taxonomy.py` **100%** (60 stmts, 0
missed) — both deltas (37%→100%, 63%→100%) hold. The wave's one
structural leftover — the `night-coverage-mining-core-naming` claim file
outliving the #101 merge — was released early this session via **#103**
(`323ccd3`, tests run 29292963205 green, auto-merged by the enabler at
23:25:40Z). #101's card idea (the display-table completeness registry)
was honestly deduped against here, not recycled. Nothing overstated.
