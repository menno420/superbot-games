# 2026-07-14 · night CI fix — run services/tests in the tests workflow

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-13T23:48:43Z · night-ci-include-services-tests

CI-gap slice, verified this session at main `a704e96` before acting
(the lead came from PR #102's text and was treated as unverified):

- `.github/workflows/tests.yml`'s pytest step ran
  `python3 -m pytest tests/ games/exploration/tests/ -q` — omitting
  `services/tests/` (164 tests: the five cross-game workflow suites plus
  the world registry).
- The suite IS registered: `tests/EXPECTED_SUITES.txt` lists
  `services/tests` and `services/tests/EXPECTED_MIN_TESTS.txt` pins a
  floor of 164, so `tests/check_suite_floors.py` collection-checked it
  on every CI run — but the tests were never EXECUTED there. Measured:
  the CI invocation collected **442**, the full local suite
  (`pytest tests/ games/exploration/tests/ services/tests/ -q`)
  collects **606**.

Shipped the one-line fix: `services/tests/` added to the workflow's
pytest invocation, matching the existing style — CI now executes the
same 606-test suite the sessions run locally. Verified locally:
`tests/check_suite_floors.py` green (8 suites, TOTAL 606) and the new
invocation collects 606. No test changes, no gameplay changes; branch
merged up over #105/#106 (telemetry append-conflict resolved keeping
both rows in merge order).

## 💡 Session idea

This gap existed because the suite list lives in TWO places that can
drift: `tests/EXPECTED_SUITES.txt` (what must exist) and tests.yml's
pytest line (what actually runs). Make the registry the single source
of execution truth: teach `tests/check_suite_floors.py` a
`--print-suites` mode (or a tiny `tests/run_all.py`) and have the
workflow run `python3 -m pytest $(python3 tests/check_suite_floors.py
--print-suites) -q` — a registered suite is then executed by
construction, and "collected-but-never-run" becomes structurally
impossible instead of one more thing to review. Dedupe check against
recent card ideas: the coverage ratchet became the per-suite floors
(counts, not execution); the telemetry backfill, detector-trip
registry, display-table registry, sim-harness smoke registry, and
pinned-bug marker ledger don't touch which paths CI executes. No card
idea to date does.

## ⟲ Previous-session review

The previous wave is #105/#106 (same night run, slices A and B),
re-verified against `origin/main`: #105 (squash `32e98fd`) released the
night-coverage-encounters-sim claim exactly as described — control-only
deletion, fast lane, tests run 29293586648 green, and the claim file is
absent at HEAD. #106 (squash `43a0cf3`) fixed the ZeroDivisionError
that #104 pinned: at HEAD, `format_report`'s kind-frequency lines carry
the `n/a` zero-actions guard in the same conditional-expression style
as the per-depth branch, the pinning test now asserts the guarded
output, and the full suite held at 606 with `encounters_sim.py` still
100% (119 stmts) on a coverage replay. #106 also broke the two-wave
pattern of orphaned claim files by deleting its own claim in its flip
commit — this card's slice does the same. One process note from this
slice: back-to-back carded merges make telemetry/model-usage.jsonl an
append-conflict hotspot (this branch needed a manual merge over #106's
row); the file is append-only so the resolution is mechanical, but it
is the same shared-append shape the claims README warns about.
