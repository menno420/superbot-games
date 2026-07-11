# 2026-07-11 — substrate-kit upgrade v1.10.0 → v1.10.1

> **Status:** `in-progress`

📊 Model: fable-5 · high · kit-upgrade

## What is about to happen

Distribution-wave upgrade of the vendored substrate-kit from v1.10.0 to
v1.10.1 (kit-owned files only — owner directive Q-0261.3; no lane content,
no control/inbox.md or control/status.md edits, no domain work,
`.github/workflows/tests.yml` untouched).

Payload: the gate's added/modified-card grading loses its `tail -1`
single-card picker — under v1.10.1 **every** session card in the diff is
graded per-card (any added in-progress card holds the whole step; modified
siblings get an advisory alongside an add) — plus the emphasis-blind
`_MODEL_DOCTRINE_PHRASE` match. No breaking changes, no state migration.

Canonical pinned-asset path: v1.10.1 release asset (sha256
`fbe83ce35d1fb3b544ac58fc60ee2609eaa6c69c13d77883e9fdc5da6bbad158`,
three-way verified upstream) staged as `bootstrap.py.new` + `release.json`,
then `python3 bootstrap.py.new upgrade`. This card opens the PR born red by
design (the live v1.10.0 gate already holds added in-progress cards);
auto-merge is deliberately NOT armed — this repo is where the #40
card-only premature merge happened; landing path is a squash merge after
green, as the very last step.
