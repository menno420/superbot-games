# 2026-07-11 — substrate-kit upgrade v1.7.1 → v1.8.0

> **Status:** `in-progress`

📊 Model: Claude Fable 5 (claude-fable-5)

## What is about to happen

Distribution-wave upgrade of the vendored substrate-kit from v1.7.1 to v1.8.0
(kit-owned files only — owner directive Q-0261.3; no lane content, no control/
edits, no domain work). Canonical path per the v1.7.1 card: stage the
sha256-verified release asset as `bootstrap.py.new` + `release.json` in the
root, run `python3 bootstrap.py.new upgrade`, verify plants/backups/report,
`check --strict`, flip this card, merge on green.
