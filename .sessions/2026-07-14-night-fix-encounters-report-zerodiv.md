# 2026-07-14 · night fix — guard format_report against zero-action reports (mining encounters sim)

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-13T23:42:47Z · night-fix-encounters-report-zerodiv

Bug-fix slice under the ORDER 008(b) production-grade standing directive,
picking up the one latent bug that #104's coverage slice (merge `a704e96`,
suite 606 passed) found and deliberately pinned rather than fixed:
`format_report` in `games/mining/sim/encounters_sim.py` divided the
kind-frequency lines by `report.actions` with no zero-actions guard —
unlike `SimReport.encounter_rate` (0.0 fallback) and unlike the
per-depth branch (`n/a` on a zero denominator) — so
`format_report(SimReport())` raised `ZeroDivisionError`.

Shipped the minimal guard mirroring the module's own conventions: the
kind rows now render `n/a` (same token, same style as the per-depth
zero-denominator branch) when `report.actions` is 0, via the identical
conditional-expression form used at the per-depth line. The pinning test
`tests/mining/test_encounters_sim.py` flipped from
`pytest.raises(ZeroDivisionError)` to asserting the guarded output
(`encounter rate: 0.0%` plus an `n/a` row for all four kinds); the now
unused `pytest` import was dropped. Nothing else changed: no gameplay
constants, no other renderer lines, non-zero reports byte-identical
(the end-to-end purity and formatting pins from #104 all still pass
unmodified). Verified: full suite **606 passed** locally; coverage
replay `games/mining/sim/encounters_sim.py` **100%** (119 stmts,
0 missed) — the guard's both branches are executed.

## 💡 Session idea

#104 pinned this bug instead of fixing it — the right call for a
tests-only slice, but the handoff only worked because a human-readable
comment happened to say "latent bug". Adopt a **pinned-bug marker
convention + ledger check**: any test that pins known-wrong behavior
must carry a grep-able marker (e.g. `# PINNED-BUG:` with a one-line
description), and a small checker (bootstrap or a meta-test) lists all
markers so every pinned bug is either fixed (marker removed, like this
slice) or consciously re-affirmed — pinned bugs can't silently rot into
"documented behavior". Dedupe check against recent card ideas: the
telemetry outcome backfill, the CI coverage ratchet, the detector-trip
registry, the display-table completeness registry, and the sim-harness
smoke registry are all about keeping *data/tables/harnesses* in sync;
none tracks the lifecycle of deliberately-pinned wrong behavior in
tests. No card idea to date does.

## ⟲ Previous-session review

The previous session is the #103/#104 wave, re-verified against
`origin/main` at `a704e96`: #103 (squash `a7524cb`) released the
night-coverage-mining-core-naming claim exactly as described —
control-only deletion, and the file is absent at HEAD. #104 (squash
`a704e96`) delivered what its card claims: `tests/mining/
test_encounters_sim.py` exists with the promised pins, the suite count
matches (592 → **606 passed**, re-run this session), and a fresh
coverage replay shows `games/mining/sim/encounters_sim.py` at **100%**
(119 stmts, 0 missed) — the 68%→100% delta holds. Its "one latent bug
found, pinned not fixed" claim was accurate and honest — this slice is
that bug's fix, and the pin flipped exactly as the card predicted a fix
would. The wave's structural leftover repeated #101's pattern: the
`night-coverage-encounters-sim` claim file outlived the #104 merge and
was released early this session via **#105** (`3b7811e`, tests run
29293586648 green). One process nit: that's two waves in a row where
the claim release needed a follow-up control PR — the flip commit of a
carded slice could delete its own claim file, which this card's slice
does (claim deleted in this flip commit).
