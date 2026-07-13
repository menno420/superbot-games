# 2026-07-14 · night coverage — pin the economy ledger seam's untested paths (tests)

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-13T23:04:36Z · night-coverage-economy-sim

Coverage slice under the ORDER 008(b) production-grade standing directive:
`games/shared/sim/economy_sim.py` — the cross-domain economy ledger that
enumerates every reward faucet and computes the three named global
invariants — sat at **75% coverage** (150 stmts, 37 missed) at main
`8b0b476` (re-verified this session; matches the 2026-07-13 scan at
`511fa91`). The missed lines were exactly the seam's alarm wiring: the
FAIL branches of all three invariant detectors (323, 339, 345, 352–353 —
never exercised, so a detector rotting to always-True would have passed
the suite), the `_mean_surface_ore_coin_value` empty-weights guard (173),
the `report.domains` property (100), and the entire `format_report`
renderer (358–397).

Shipped 11 focused tests in `tests/shared/sim/test_economy_sim.py`: each
named invariant detector now provably TRIPS on a constructed violation —
`ITEM_FAUCET_MINTS_NO_CURRENCY` on any single nonzero currency/xp figure
on either item faucet (6 doctored reports via `dataclasses.replace`);
`NOOP_MINTS_NOTHING` on a minting dnd narrate effect (both ids), a
mining BARREN cell resolving to NONE-with-rewards or non-NONE, and a
too-tired fishing cast granting items or progression (targeted
monkeypatch, restored per test — no shipped constant edited). Also
pinned: the documented defensive branch (a value-equal empty `Grant`
that is not the `EMPTY_GRANT` sentinel still passes), the empty-weights
0.0 guard, `report.domains` ordering, and `format_report`'s load-bearing
lines (domain rows, numeric-vs-`host` ceilings, PASS and FAIL rendering
both ways, per-completion bundles + `GLOBAL_MAX`, pinned bands with
observed figures). Module coverage 75% → **100%** (150/150 stmts); suite
567 → **578 passed**; `python3 bootstrap.py check --strict` pre-flip
showed only this card's designed born-red HOLD. Tests-only: zero
gameplay-constant changes, no sim-verdict-needing surface. No bug found —
every FAIL path behaved exactly as the module docstring promises.

## 💡 Session idea

This slice's core finding generalizes: all three invariant detectors had
their FAIL branches at 0% coverage, meaning any of them could have rotted
to an always-True stub without a single red test. Add a **detector-trip
registry**: a tiny test-support convention (e.g. a
`tests/shared/sim/test_invariants_trip.py` registry list) that names
every exported invariant predicate across the sims — `economy_sim`'s
three, plus the per-domain sims' verdict helpers — and asserts, for each,
that at least one registered *tripping* construction returns False. New
invariant functions fail the registry test until they ship with a proven
trip. That is checkable without any CI change and is strictly about
assertion strength, not line coverage. Dedupe check: recent cards seeded
the telemetry outcome backfill, the coverage ratchet vs a committed
baseline (line-coverage regression gating — adjacent but distinct: a
ratchet can be satisfied by trivially executing lines; this registry
demands a False-returning witness per detector), the machine-readable
truth-stamp anchor, the ledger-drift check, and the cook-leg SIM-REQUEST
— none requires a violation witness per invariant; no card idea to date
does.

## ⟲ Previous-session review

The previous session is the #96/#97 wave, re-verified against
`origin/main`: #96 (`ca2184e`, squash `511fa91`) released the
night-truth-stamp claim exactly as promised — a 3-line control-only
deletion, fast-lane, nothing else touched. #97 (squash `8b0b476`)
delivered the loadout coverage slice it claimed: `tests/mining/
test_loadout.py` with 11 tests landed, and its local-state claims replay
exactly — this session's baseline scan at `8b0b476` found **567 passed**
(matching the card's 556→567) and economy_sim at 75% (matching the
card's next-rung table). The wave's one structural leftover — the
`night-coverage-mining-loadout` claim file outliving the merge — was
released this session via **#98** (`e1a638d`, squash `07be6ed`, tests
run 29291538389 green), merged by the auto-merge enabler, keeping the
claims ledger clean. Its card idea (the coverage ratchet) was honestly
deduped against, not recycled. Nothing overstated.
