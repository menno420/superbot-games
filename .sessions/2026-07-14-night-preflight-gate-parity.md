# 2026-07-14 · night build — ci: gate-parity preflight — one command, registry-derived test paths

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-14T03:36:56Z · night-preflight-gate-parity

Build slice from `.sessions/2026-07-14-night-coverage-mining-items.md` +
`.sessions/2026-07-14-night-ci-include-services-tests.md`'s card ideas,
both verified unimplemented at branch base `94a396c`: no
`tools/preflight.py`, no `--print-suites` flag, and tests.yml's pytest
line hardcoded `tests/ games/exploration/tests/ services/tests/` — a
second copy of what `tests/EXPECTED_SUITES.txt` already pins, the drift
class behind the #107 collected-but-never-run gap.

Shipped all three legs. (a) `tests/check_suite_floors.py --print-suites`:
pytest execution roots DERIVED from the registry — each entry collapses to
the prefix up to its first `tests` path component (its outermost test
tree), first-seen order, deduped; an entry with no `tests` component fails
loudly rather than guessing. At HEAD that derives exactly the three roots
the workflow used to hardcode. (b) `tools/preflight.py`: floor guard →
pytest over the derived roots → `gen_balance.py --check`, step banners,
exit = first failing step's code — the ONE command a session runs before
any flip. (c) tests.yml's two hand-synced gate steps replaced by
`python3 tools/preflight.py` (fast lane, setup-python, and the pip install
kept; minimal diff otherwise). 6 tests in `tests/tools/test_preflight.py`:
three derivation unit tests (collapse, underivable report, first-seen
order + dedupe, via importlib on the guard script), the derived==known
roots pin, a structural every-registry-entry-under-some-root pin, and the
end-to-end smoke (subprocess, green repo → exit 0, all three banners).
The smoke's `SBG_PREFLIGHT=1` env guard makes the pytest-inside-preflight
nesting bound to ONE level (the inner suite skips the smoke). Floor
`tests/tools` 21 → **27** (floor==collected); `docs/balance.md`
regenerated BEFORE flip, `--check` green; suite **760 → 766 passed**
locally; strict exit 0 post-flip. Since this PR changes CI itself, the
post-flip run was watched to confirm the preflight path actually executed
(run IDs in the PR body). Claim
`control/claims/night-preflight-gate-parity.md` self-released here.

## 💡 Session idea

Preflight now makes the three CI gates one local command, but a flip needs
a FOURTH local check the script doesn't cover: the substrate-gate's strict
session-log pass (`bootstrap.py check --strict --require-session-log
--session-log <card>`), which every card in this wave runs by hand next to
preflight. Add a flip mode: `tools/preflight.py --flip
.sessions/<card>.md` that appends the strict check as step 4/4 after the
three gates — flip-readiness becomes literally one command, and the
session-log argument doubles as a guard against flipping with the WRONG
card path (a typo today just checks nothing). Dedupe check against the
used-idea list: this card's own spec (gate-parity preflight +
registry-derived CI paths) covers CI's three gates only, not the strict
flip check; truth-stamp scaffold generates cards, it doesn't verify them
at flip time; missing-vs-stale split and report-flag wiring pins target
gen_balance internals. No card idea to date folds the strict flip check
into the preflight sequence.

## ⟲ Previous-session review

The previous slice is this run's own #127
(`claude/night-shared-repl-seam`, born-red `97d5b22`, seam `834122f`,
flip `8363a10`, squash-merged to main as `94a396c` — this branch's base —
by github-actions[bot] at 2026-07-14T03:36:05Z). Same-session review, so
discount accordingly; what I could verify from the outside all held:
at the flip SHA both tests (run 29303891358) and substrate-gate (run
29303891387) completed success, and the born-red SHA's substrate-gate
failure (run 29303435276) was exactly the designed pre-flip HOLD.
Re-checked its numbers against this slice's own baseline: the suite at
`94a396c` runs **760 passed** (my pre-slice run here), matching its
"749 → 760"; `games/shared/cli/repl.py` exists at base with all five
mains importing `games.shared.cli`; `services/tests` floor reads 193 with
collection matching. Honest limits, same one #126 noted about #125: the
15 byte-identity transcripts live in the session scratchpad, not the
repo, so the PR-body SHA table is attestation, not a reproducible
artifact (the transcript-golden-corpus idea that would fix this is
already on the used list, not re-claimed); and coverage claims (repl.py
100%, fishing 99%) come from the card's own local run — no CI coverage
gate pins them.
