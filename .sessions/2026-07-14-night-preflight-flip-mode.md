# 2026-07-14 · night build — ci: preflight --flip — one command to flip-readiness

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-14T04:12:45Z · night-preflight-flip-mode

Build slice from #128's card idea, verified fresh at branch base `2b55e43`:
`tools/preflight.py` covered the three tests-workflow gates but a flip
needs a FOURTH local check the script didn't run — the substrate gate's
strict session-card grading. Shipped `--flip` (argparse, default
unchanged): step 4 = `python3 bootstrap.py check --strict`, banners
renumber to `1/4…4/4` only under the flag, a distinct
"flip-ready" green line, and the first red step's exit code propagates
as before. **Default 3-step mode is byte-compatible** — same `1/3…3/3`
banners, same green line, `tests.yml` untouched (it passes no args; no
trivially safe improvement found there worth the churn).

**4 tests** appended to `tests/tools/test_preflight.py`: default mode runs
exactly the three gates and never invokes bootstrap (byte-compat banner
pin), `--flip` appends exactly `[python, bootstrap.py, check, --strict]`
as step 4 with the `/4` banners, a red step 4 propagates its exit code
(SystemExit 7 pinned), and the strict semantics step 4 leans on — the
born-red HOLD — pinned via a REAL subprocess run of
`bootstrap.py check --strict --session-log <synthetic in-progress card>`
(exit 1, "badge still says in-progress", "designed hold"). Honesty note,
as specced: a full `--flip` GREEN end-to-end is deliberately not a unit
test — it would nest the entire suite + strict inside pytest, and
mid-slice the repo's newest card is in-progress BY DESIGN, so bare strict
is red on exactly the tree the test runs on. The wiring + invocation +
propagation are pinned in-process instead, the HOLD is pinned for real via
`--session-log`, and the real `--flip` green run happened post-flip on
this very branch (see below). Read-first evidence: strict's card selection
is `latest_session_log` (newest `*.md` by mtime) and the in-progress
detection is `status_in_progress` over the `> **Status:**` badge
(`bootstrap.py` ~1939–2035, HOLD message ~2050).

Floor `tests/tools` 27 → **31** (floor==collected); `docs/balance.md`
regenerated BEFORE flip; suite **784 → 788 passed** locally; preflight
green; post-flip this card's own deliverable was dogfooded:
`python3 tools/preflight.py --flip` GREEN (all four gates) — the first
one-command flip-readiness run. Claim
`control/claims/night-preflight-flip-mode.md` self-released here.

## 💡 Session idea

`--flip`'s step 4 inherits strict's card SELECTION rule: bare
`check --strict` grades the newest session card **by mtime**
(`latest_session_log`, bootstrap.py ~1939). That is the wrong card
exactly when it matters: touch any old card (a groom, a merge conflict
resolution, even a fresh checkout equalizing mtimes) and flip-readiness
silently grades a bystander while your branch's own card goes unexamined —
a green `--flip` that isn't flip-ready. Add **card-selection parity**:
preflight `--flip` derives the session card from the branch's own diff
(`git diff --name-only origin/main...HEAD -- .sessions/`, the same card
the substrate gate's added-card lane will grade) and passes it via the
existing `--session-log` flag, falling back to mtime only when the diff
carries no card. Plus a test: two cards, the older one in the branch diff,
the newer one a bystander with fresher mtime — parity mode must grade the
branch's card. Dedupe check against all 2026-07-14 cards' 💡 lines: #128's
idea was ADDING step 4 (this slice built it); the truth-stamp,
telemetry-backfill, registry-to-README, driver-parity (this run's slice
1), and quest-completability ideas are elsewhere entirely; no card touches
strict's mtime-based card selection.

## ⟲ Previous-session review

The previous slice is this run's own #130
(`claude/night-scripted-driver-seam`, born-red `369d118`, implementation
`59f37c4`, flip `1d555c5`, squash-merged to main as `2b55e43` — this
branch's base — by github-actions[bot] at 2026-07-14T04:08:53Z).
Same-session review, discount accordingly; external evidence: at the flip
SHA, tests run `29305224156` and substrate-gate run `29305224149` both
success; born-red `369d118`'s substrate-gate failure (run `29304868953`)
was the designed HOLD; CI green on first post-implementation push. Its
central claim (byte-identity) was mechanically strong — 10 fixed-seed
transcripts covering both closing paths, capture double-run to prove
determinism BEFORE trusting it, all SHA-256-identical — and this slice's
own base preflight re-ran the adopting suites green on top of the merge.
Two honest dings: (1) the capture script lives in the session scratchpad,
not the repo, so the SHA table on PR #130 is not re-runnable by a reviewer
from the repo alone — the 11 seam tests pin the loop contract but not the
transcripts themselves; a committed capture harness would have made the
evidence durable. (2) the 5-way adoption pin's tail assertion is weak
(`len(result.lines) > 0`) — the recorder proves the routing, but that
content assertion adds nearly nothing; the byte-identity table carries the
real content weight, which loops straight back into ding (1).
