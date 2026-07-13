# 2026-07-14 · night CI fix — run services/tests in the tests workflow

> **Status:** `in-progress`
>
> 📊 Model: Fable · 2026-07-13T23:48:43Z · night-ci-include-services-tests

CI-gap slice, verified this session at main `a704e96` before acting
(the lead came from PR #102's text and was treated as unverified):

- `.github/workflows/tests.yml`'s pytest step runs
  `python3 -m pytest tests/ games/exploration/tests/ -q` — it omits
  `services/tests/` (164 tests: the five cross-game workflow suites plus
  the world registry).
- The suite IS registered: `tests/EXPECTED_SUITES.txt` lists
  `services/tests` and `services/tests/EXPECTED_MIN_TESTS.txt` pins a
  floor of 164, so `tests/check_suite_floors.py` collection-checks it on
  every CI run — but the tests are never EXECUTED there. Measured:
  CI invocation collects **442**, the full local suite
  (`pytest tests/ games/exploration/tests/ services/tests/ -q`)
  collects **606**.

Plan: minimal one-line workflow fix adding `services/tests/` to the
pytest invocation, matching the existing style. No test changes, no
gameplay changes.
