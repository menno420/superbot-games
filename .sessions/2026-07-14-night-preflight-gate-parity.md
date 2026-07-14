# 2026-07-14 · night build — ci: gate-parity preflight — one command, registry-derived test paths

> **Status:** in-progress
>
> 📊 Model: Fable · 2026-07-14T03:36:56Z · night-preflight-gate-parity

Build slice from `.sessions/2026-07-14-night-coverage-mining-items.md` +
`.sessions/2026-07-14-night-ci-include-services-tests.md`'s card ideas
(both verified unimplemented: no `tools/preflight.py`, no `--print-suites`
flag, and `.github/workflows/tests.yml:51` still hardcodes
`tests/ games/exploration/tests/ services/tests/` — duplicating
`tests/EXPECTED_SUITES.txt`, the drift class that caused the #107 gap).
Plan: (a) `tests/check_suite_floors.py --print-suites` emitting the
top-level pytest path roots derived from the suite registry; (b)
`tools/preflight.py` running floor guard → pytest over the derived paths →
`gen_balance.py --check` with step banners, exiting non-zero on the first
failure — the ONE command a session runs before any flip; (c) tests.yml
invokes the preflight instead of the three hand-synced steps. Unit tests
for the derivation + a preflight smoke test in `tests/tools/`.
