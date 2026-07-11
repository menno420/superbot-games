# 2026-07-11 — substrate-kit upgrade v1.9.0 → v1.10.0

> **Status:** `in-progress`

📊 Model: fable-5 · high · kit-upgrade

## What is about to happen

Distribution-wave upgrade of the vendored substrate-kit from v1.9.0 to
v1.10.0 (kit-owned files only — owner directive Q-0261.3; no lane content,
no control/inbox.md or control/status.md edits, no domain work). Canonical
path: stage the sha256-verified release asset
(`ba69fc5cf21619cc85e4c733ebe3d9eda8803e678f810fcc39b94d60c2f3b5a4`) as
`bootstrap.py.new` + `release.json` in the repo root, run
`python3 bootstrap.py.new upgrade`, verify the payload, run
`check --strict` + the pytest suite, then flip this card complete as the
deliberate last step.

v1.10.0 headline for THIS repo: it closes the card-only born-red loophole
discovered here (#40 — a PR-added in-progress card on a card-only diff rode
the advisory lane green and pre-armed auto-merge merged it in 24s). The new
gate returns a locked-door `session-card-hold` (never allowlistable) for an
ADDED in-progress card even on card-only diffs. First-exercise verification
of that hold on this repo is part of this session's close-out. Per the #40
lesson, auto-merge is NOT armed while this PR is card-only.
