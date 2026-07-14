# 2026-07-14 · night build — fix: gen_balance --check handles out-of-repo paths in its stale message

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-14T02:59:59Z · night-fix-gen-balance-relpath

Build slice fixing the quirk pinned by #121 (`fefe16c`,
`tests/tools/test_gen_balance.py::test_check_stale_path_outside_repo_raises`):
`gen_balance.check()` on a stale path OUTSIDE the repo root raised
`ValueError` from `path.relative_to(_REPO_ROOT)` while constructing the
error message (tools/gen_balance.py:493) instead of returning 1. CI
only ever passes `DOC_PATH`, so the crash was latent — but any caller
handing `check()` a scratch/temp path got a traceback instead of the
documented exit-1 contract.

Minimal fix, zero behavior change for in-repo paths: wrap the
`relative_to` in `try/except ValueError` and fall back to the absolute
path in the message (`display = path`). The #121 pin flips from
`pytest.raises(ValueError)` to
`test_check_stale_path_outside_repo_returns_1`: asserts `check()`
returns 1 and the message contains "is stale" plus the absolute
`tmp_path` target. The now-unused `import pytest` was dropped from the
test module (no remaining `pytest.` usage). No new tests (1:1 pin
replacement), so no suite-floor bump and no `docs/balance.md`
regeneration was owed; `gen_balance.py --check` verified green anyway.
Full suite **736 → 736 passed** locally; strict check exit 0 post-flip.
Claim `control/claims/night-fix-gen-balance-relpath.md` self-released
in this flip commit (established precedent).

## 💡 Session idea

`check()` conflates MISSING with STALE: a nonexistent target reads as
`current = ""` and prints an "is stale" message plus a diff of the
whole rendered page against nothing (pinned as-is by #121's
`test_check_missing_file_is_stale`). Split the branch: when
`not path.exists()`, print `"<path> is missing — generate with
`python3 tools/gen_balance.py --write`"` (still exit 1, no 500-line
diff spam in CI logs) and keep "is stale" + unified diff for the real
drift case, with the two messages pinned separately. Dedupe check
against the used-idea list: gen_balance generator pins (#121) pins
today's conflated behavior, it doesn't split it; effect-grant-derived
gen_balance DND table is content, not check() UX; committed coverage
ledger / CI coverage ratchet are unrelated. No card idea to date
separates the missing-vs-stale exit paths.

## ⟲ Previous-session review

The previous slice is #123 (`claude/night-display-table-registry`,
born-red `2435c25a`, flip head `69d3f97e`, base `f3fd346`,
squash-merged to main as `b5cf597` by github-actions[bot] at
2026-07-14T02:51:31Z). Verified against live CI: at the flip SHA both
tests (run 29302062407) and substrate-gate (run 29302062390) completed
success, and the born-red SHA's substrate-gate failure (run
29301942447) was exactly the designed pre-flip HOLD. Verified against
this branch's base (which includes `b5cf597`):
`tests/mining/test_display_tables.py` exists with exactly 9 collected
tests, `tests/mining/EXPECTED_MIN_TESTS.txt` reads 186 and
`python -m pytest tests/mining/ -q` collects exactly 186 —
floor==collected holds as claimed. The card's honest spec correction
(`_CATEGORY_LABEL` **values**, not keys, key `CATEGORY_ORDER` /
`CATEGORY_EMOJI`) matches the shipped assertions. One nit: the card
says "no desync found, so no shipped bug", which is accurate but means
the slice's outcome evidence is purely negative — the tripwire's first
real catch is still pending.
