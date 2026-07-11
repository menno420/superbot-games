# 2026-07-11 — substrate-kit upgrade v1.10.0 → v1.10.1

> **Status:** `complete`

📊 Model: fable-5 · high · kit-upgrade

## What happened

Distribution-wave upgrade of the vendored substrate-kit from v1.10.0 to
v1.10.1 (kit-owned files only — owner directive Q-0261.3; no lane content,
no control/inbox.md or control/status.md edits, no domain work,
`.github/workflows/tests.yml` untouched). PR #43.

- **Vendored dist:** `bootstrap.py` replaced with the v1.10.1 release asset,
  sha256 `fbe83ce35d1fb3b544ac58fc60ee2609eaa6c69c13d77883e9fdc5da6bbad158`,
  verified against `release.json` before running (canonical path:
  `bootstrap.py.new` + `release.json` staged in the root, then
  `python3 bootstrap.py.new upgrade`; the upgrade self-verified sha256 +
  version and self-cleaned both inputs). Outgoing v1.10.0 dist banked at
  `.substrate/backup/bootstrap-1.10.0.py` (sha256 `ba69fc5c…`, byte-equal
  to the pre-upgrade vendored copy); the five pre-existing banks
  `bootstrap-1.2.0.py` (`258ab02a…`), `bootstrap-1.7.0.py` (`00f4f4cd…`),
  `bootstrap-1.7.1.py` (`2aa4fedd…`), `bootstrap-1.8.0.py` (`28c5dcb6…`)
  and `bootstrap-1.9.0.py` (`55181082…`) are byte-untouched
  (hash-verified before/after). Exactly one new backup;
  `last-upgrade.json` from 1.10.0 → to 1.10.1.
- **Live gate regenerated** kit-owned from the v1.10.1 template, byte-equal
  to staged `.substrate/ci/substrate-gate.yml`. **This closes the tail-1
  multi-card shadowing loophole (venture-lab #33 class, partially
  reopening this repo's #40 class):** the old `tail -1` picker graded only
  the last-sorting card in a multi-card diff, so an added in-progress card
  could be shadowed by a later-sorting sibling. Now `while IFS= read -r
  card` loops grade EVERY card in the diff — ANY added card holding holds
  the whole step; siblings modified alongside an add are advisory-only
  (logged, never grade-affecting); a modify-only diff keeps the full
  locked-door gate on each modified card. Gate-touching PRs keep the full
  locked door on added cards + run `--simulate-added-card`. Also in
  v1.10.1: the `_MODEL_DOCTRINE_PHRASE` check is emphasis-blind. Zero
  `pytest` references in the regenerated gate; `tests.yml` not in the diff.
- **Doctrine idempotence:** `.sessions/README.md` byte-identical
  before/after (sha256 `2abe859a…` unchanged — the v1.10.0 doctrine append
  was not duplicated). This repo's unique `.substrate/check-exceptions.yml`
  survives untouched (sha256 `28599970…` unchanged).
- **Carve-out report:** `.substrate/upgrade-report.md` § Carve-out scan:
  "carve-out scan: .github/workflows/substrate-gate.yml — ran, 0 found".
- **CI proof:** born-red card commit c3c1cc9 → old-gate HOLD red (run
  29147191016; the #40 card-only loophole stays closed pre-upgrade),
  tests green (29147191017). Payload commit c6acaaf → NEW gate locked-door
  HOLD red (run 29147228334) with the designed banner and the in-run
  simulate verdict ("the added-card lane would HOLD (born-red …)"), tests
  green (29147228329). Auto-merge never armed (this repo is where the #40
  24-second card-only merge happened); landing is a squash merge after the
  flip goes green.
- **Verify:** `python3 bootstrap.py check --strict` → exit 1 pre-flip
  **only** on this card's in-progress badge with the designed notice
  ("check: HOLD (by design) … nothing to investigate."), all other checks
  clean (9 allowlist-suppressed findings, reason-carrying);
  `check --simulate-added-card` on this card → advisory HOLD verdict,
  exit 0.

## 💡 Session idea

The upgrade's multi-card loop distinguishes added vs. modified cards via
two `git diff --diff-filter` calls whose output feeds `<<<` heredocs — a
card path containing a newline or unusual characters would silently
mis-split. Kit-side candidate: have the gate (or `check`) assert the
`.sessions/*.md` filename grammar (`YYYY-MM-DD-slug.md`, no spaces) and
red loudly on a nonconforming card filename, turning an unrepresentable
edge case into an enforced convention — cheap, and it protects every
per-card loop shipped in v1.10.1 at once.

## ⟲ Previous-session review

The v1.10.0 upgrade session (#42) set the template this session executed
almost verbatim: its card recorded the exact asset-staging path, the
per-bank hash discipline, and the arming-timing lesson, and all three
transferred with zero friction — this session's only divergences were the
new payload facts. What it could have done better: its card documented the
added-card HOLD but not the *multi-card* diff shape, and the tail-1
shadowing loophole v1.10.1 fixes lived exactly in that undocumented gap —
one sentence probing "what if the diff has TWO cards?" might have caught
it a wave earlier. Improvement to the system: upgrade cards should end
with a one-line "shapes NOT exercised by this PR" note (multi-card diffs,
rename-only diffs, …) so the next wave inherits the untested surface as an
explicit checklist instead of rediscovering it via a live loophole.
