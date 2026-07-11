# 2026-07-10 — ORDER 001: unify seat + fix pytest collection scope

> **Status:** `complete`

📊 Model: Claude Opus · 2026-07-10T23:55:47Z · one-shot seat-unification + CI collection-scope fix

## Scope
Execute ORDER 001 (P0): the CI test job silently collected only `tests/` (73 of 121
pure-domain tests) — the 48 `games/exploration/tests/` were invisible to the gate. Fix the
real workflow (`.github/workflows/tests.yml`, not the stale ORDER text pointing at
substrate-gate.yml) so every suite is collected and add a hard count-floor so a dropped or
renamed suite fails loudly. Alongside: land the gen-1 → single-seat reality — mark the
two-lane split as GEN-1 HISTORY on the lane files, fix the recorded kit-version drift
(v1.2.0 → v1.7.1) in the two archived status files, rewrite the root README to the
single-seat world-games seat, and convert `control/status.md` from its gen-1 pointer stub
into the real unified status. No kit re-adoption (tree is already on v1.7.1).

## 💡 Session idea
Make the `tests` workflow a **required status check** on `main`. Today the 121-count floor
lives in the job, but nothing forces the job to run/pass before merge — a control-lane
short-circuit or a missing required-context lets a coverage regression merge green. Marking
`tests` required (with the existing control fast-lane still reporting green so heartbeat PRs
don't jam) turns the count-floor from advice into an actual merge gate: "enforce, don't
exhort", the move this fleet already believes in.

## ⟲ Previous-session review
This is a previous-session review of the two gen-1 close-out cards
(`2026-07-09-exploration-p1-quest-engine` and `2026-07-09-exploration-wakeup`). Both were
honest and disciplined — born-red cards, early PRs, claim-first shared-code, a sim-pinned
engine whose numbers re-derive. The durable miss they both circled but never closed is
exactly this order's target: the CI gate ran `pytest tests/ -q`, so the 48 exploration
tests the P1 session shipped were never actually gated — a green check that proved 73 of
121 suites. The wakeup card's own "enforce, don't exhort" instinct (its lanes-manifest
idea) applies here verbatim; this session pays that debt down with a collected-count floor
instead of trusting the path list to stay complete.

## What shipped
1. **CI collection-scope fix + count floor (ORDER 001 P0)** — `.github/workflows/tests.yml`
   now collects `tests/` **and** `games/exploration/tests/` and guards a 121-count floor
   (73 + 48); a dropped/renamed suite trips `::error::` instead of silently shrinking
   coverage. Before this the gate ran `pytest tests/ -q` and saw only 73 of 121.
2. **GEN-1 HISTORY banners** on the five lane files (`docs/lanes.md`,
   `control/inbox-mining.md`, `control/inbox-exploration.md`, `control/status-mining.md`,
   `control/status-exploration.md`) — the two-lane split is archived, not live.
3. **Kit-drift fix** — the two archived status files recorded `substrate-kit v1.2.0`; the
   tree is on v1.7.1, corrected in place.
4. **Single-seat reality** — root `README.md` rewritten to one seat owning `games/**` and
   the unified `control/` bus (Q-0267 theme-readiness), and `control/status.md` converted
   from the gen-1 pointer stub into the real unified status.

Local test evidence: `python3 -m pytest tests/ games/exploration/tests/ -q` → **121 passed
in 3.54s**; the count-floor pipeline printed `collected tests: 121` (floor passed).

