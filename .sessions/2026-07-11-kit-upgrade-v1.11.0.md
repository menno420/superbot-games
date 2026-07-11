# 2026-07-11 — substrate-kit upgrade v1.10.1 → v1.11.0

> **Status:** `in-progress`

📊 Model: fable-5 · high · kit-upgrade

## What is about to happen

Distribution-wave upgrade of the vendored substrate-kit from v1.10.1 to
v1.11.0 (kit-owned files only — owner directive Q-0261.3; no lane content,
no control/inbox.md or control/status.md edits, no domain work,
`.github/workflows/tests.yml` untouched). Canonical path: stage the
sha256-verified release asset as `bootstrap.py.new` + `release.json`,
run `python3 bootstrap.py.new upgrade`, verify the MINOR payload
(HANDOFF.md composer, planted CLAUDE.md read-first rider, gate action-pin
bumps to checkout@v5 / setup-python@v6, guard-fires dedupe, exactly one
new `.substrate/backup/bootstrap-1.10.1.py`), then
`python3 bootstrap.py check --strict` → flip this card → squash-merge on
green.
