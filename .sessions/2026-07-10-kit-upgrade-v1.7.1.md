# 2026-07-10 — substrate-kit upgrade v1.7.0 → v1.7.1

> **Status:** `in-progress`

📊 Model: Claude Fable 5 (claude-fable-5)

## What is about to happen

Distribution-wave upgrade of the vendored substrate-kit from v1.7.0 to v1.7.1
(kit-owned files only — owner directive Q-0261.3; no lane content, no control/
edits, no domain work). Canonical path: sha256-verified v1.7.1 release asset
staged as `bootstrap.py.new` + `release.json`, then `python3 bootstrap.py.new
upgrade`. Must verify: `tests.yml` (the relocated pytest carve-out from PR #22)
untouched; regenerated gate carries no host jobs; carve-out detector clean;
exactly one new banked backup (`bootstrap-1.7.0.py`).
