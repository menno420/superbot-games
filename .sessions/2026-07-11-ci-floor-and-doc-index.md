# 2026-07-11 — kill cross-PR conflict churn (self-computing floor + doc indexes)

> **Status:** `complete`

- **📊 Model:** Opus 4.8 · Sat Jul 11 01:29:26 UTC 2026 · kill cross-PR conflict churn (self-computing floor + doc indexes)

## Scope

Every feature PR was forced to edit the same three shared lines and so re-conflicted
every other open PR on merge:

1. `.github/workflows/tests.yml` carried ONE hardcoded `-lt 230` count-floor int for
   the whole suite. Any PR that added tests had to bump that single integer, so two
   test-adding PRs always collided on the same line.
2. `docs/current-state.md` funneled EVERY design-doc link through one `**Designs:**`
   bullet, so any PR adding a design doc edited that one line — another shared collision
   point.

This session removes both code-level causes without weakening the ORDER-001 guarantee
(the gate must still fail loudly the moment any suite drops out of collection or shrinks).

## What shipped

- **FIX #1 — per-suite floor.** Each real suite dir gets its own
  `EXPECTED_MIN_TESTS.txt` (single integer = that suite's current collected count), so a
  test-adding PR edits only its OWN suite's file. A committed discovering checker
  `tests/check_suite_floors.py` collects each suite, compares to its floor, and prints a
  LOUD per-suite failure (naming the suite) on any shortfall / collection error / known
  suite collecting zero. The shared hardcoded `-lt 230` is gone from `tests.yml`; the CI
  step now runs the guard then the suite.
- **FIX #1b — suite registry closes the wholesale-removal gap.** Discovery alone had a
  hole: deleting an ENTIRE suite dir *together with* its `EXPECTED_MIN_TESTS.txt` made the
  suite vanish from discovery, so the guard passed green while all of that suite's coverage
  was silently lost (the old single hardcoded total floor would have caught it; per-suite
  discovery could not). A committed registry `tests/EXPECTED_SUITES.txt` now pins the set of
  suite dirs that MUST exist; `check_suite_floors.py` cross-checks discovery against it so a
  registered suite whose dir or floor file has VANISHED fails LOUDLY (naming it), and a
  discovered-but-UNREGISTERED suite also fails LOUDLY (new coverage must be tracked). The
  registry is one shared file touched only when a whole suite is added/removed (rare), so it
  does not reintroduce per-test churn. Net: neither per-suite shrinkage NOR wholesale suite
  removal NOR an untracked suite can pass silently.
- **FIX #2 — per-domain doc indexes.** Per-domain design index files under `docs/design/`
  (one per domain that has design docs), each badged `reference`, list that domain's
  design docs. `current-state.md` links the four indexes ONCE instead of enumerating every
  design doc, so a design-doc-adding PR edits only its domain's index. `bootstrap.py`'s
  reachability check is already transitive (BFS through markdown + backtick refs), so docs
  linked through an index stay reachable — no gate change needed.

## 💡 Session idea

The kit's docs-gate could ship a first-class "index" badge/convention so per-domain index
files are a recognized shape rather than an ad-hoc `reference` doc — the reachability BFS
already supports the pattern; naming it would let `maintain` scaffold a domain index when a
new `docs/<domain>/` tree appears.

## ⟲ Previous-session review

The gate-pytest session (#gen-2 night prep) added the pytest step and its single count
floor in good faith, but baked the floor as ONE shared integer in a line every future
test-adding PR must touch — a conflict magnet it could not have seen without the cross-PR
merge history that only showed up later. This session's previous-session review confirms
the fix belongs at the same file it touched, split per suite so the next test PR never
meets another on that line.
