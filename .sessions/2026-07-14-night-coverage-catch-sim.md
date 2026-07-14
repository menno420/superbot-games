# 2026-07-14 · night coverage — games/fishing/sim/catch_sim (tests)

> **Status:** `in-progress`
>
> 📊 Model: Fable · 2026-07-14T00:08:44Z · night-coverage-catch-sim

Coverage slice, re-confirmed this session at main `24f6e04` (the 606-test
HEAD) before acting: `games/fishing/sim/catch_sim.py` sits at **69%**
(97 stmts, 30 missed: 65, 104, 150–187). The existing sim-pin suite
(`tests/fishing/test_catch_sim.py`, 12 tests) exercises `run()` and the
`CatchTierStats` gradient properties thoroughly, but leaves three seams
dark:

- line 65 — `CatchTierStats.species_share` (per-species share of bites,
  incl. its zero-bites guard),
- line 104 — `_rare_ids()` (the size_rank ≥ 3 rare tail read off species
  DATA, not hard-coded),
- lines 150–187 — the entire `format_report` renderer (header lines,
  per-spot sections, the species-share table, the cross-spot aggregate,
  the trailing energy line).

Plan: ≤14 focused tests in a new `tests/fishing/test_catch_sim_report.py`
(mirroring #104's `tests/mining/test_encounters_sim.py` pattern) pinning
real behavior at EXISTING constants — renderer section order and line
grammar over a tiny deterministic sweep, hand-built zero-bites /
empty-report buckets for the guard paths, and renderer purity. Tests
only; a genuine bug would be pinned + HEADLINED, not fixed here.
