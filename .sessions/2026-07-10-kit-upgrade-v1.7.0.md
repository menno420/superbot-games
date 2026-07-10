# 2026-07-10 — substrate-kit upgrade v1.2.0 → v1.7.0

> **Status:** `in-progress`

## What is about to happen

Distribution-wave upgrade of the vendored substrate-kit from v1.2.0 to v1.7.0
(release-asset path, sha256-verified against `release.json`), regeneration of
kit-owned `.substrate/**` artifacts, and a manual refresh of the live gate
(`cp .substrate/ci/substrate-gate.yml .github/workflows/substrate-gate.yml` —
kit-owned per kit PR #130). Scope is kit-owned files only: no lane content,
no control/ edits, no domain work (owner directive Q-0261.3).
