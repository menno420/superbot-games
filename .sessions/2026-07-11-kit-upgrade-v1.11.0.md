# 2026-07-11 — substrate-kit upgrade v1.10.1 → v1.11.0

> **Status:** `complete`

📊 Model: fable-5 · high · kit-upgrade

## What happened

Distribution-wave upgrade of the vendored substrate-kit from v1.10.1 to
v1.11.0 (kit-owned files only — owner directive Q-0261.3; no lane content,
no control/inbox.md or control/status.md edits, no domain work,
`.github/workflows/tests.yml` untouched). PR #45.

- **Vendored dist:** `bootstrap.py` replaced with the v1.11.0 release asset,
  sha256 `c339bd6a2eb3a139dd0106d5fd3873eb2d067f79723fccb5781d4e72a74a8d29`,
  verified against `release.json` before running (canonical path:
  `bootstrap.py.new` + `release.json` staged in the root, then
  `python3 bootstrap.py.new upgrade`; the upgrade self-verified sha256 +
  version and self-cleaned both inputs). Kit release: tag v1.11.0 →
  `640f8a1` (bump PR menno420/substrate-kit#205), release run 29152928040.
  Outgoing v1.10.1 dist banked at `.substrate/backup/bootstrap-1.10.1.py`
  (sha256 `fbe83ce3…`, byte-equal to the pre-upgrade vendored copy); the six
  pre-existing banks (`1.2.0` `258ab02a…`, `1.7.0` `00f4f4cd…`, `1.7.1`
  `2aa4fedd…`, `1.8.0` `28c5dcb6…`, `1.9.0` `55181082…`, `1.10.0`
  `ba69fc5c…`) are byte-untouched (hash-verified before/after). Exactly one
  new bootstrap bank; `last-upgrade.json` from 1.10.1 → to 1.11.0.
- **Known false-positive carve-out (this wave's class, fleet-manager #72
  precedent):** the carve-out scanner flagged the kit's own OUTGOING action
  pins (`actions/checkout@v4`, `actions/setup-python@v5`) in the live gate
  as "host-added steps" and banked
  `.substrate/backup/substrate-gate.pre-regen-4f50eb4d.yml`. Verified the
  banked copy is **byte-identical** to the old kit-owned staged template
  (`diff` vs `HEAD:.substrate/ci/substrate-gate.yml` — clean): nothing
  host-owned was lost, no `host-ci.yml` needed. The bank is committed as an
  audit artifact.
- **Live gate regenerated** kit-owned from the v1.11.0 template, byte-equal
  to staged `.substrate/ci/substrate-gate.yml`. Action pins bumped off the
  Node 20 deprecation: `actions/checkout@v4` → `@v5` (line 21),
  `actions/setup-python@v5` → `@v6` (line 80). Zero `pytest` references in
  the regenerated gate; `tests.yml` not in the diff (sha256 `574ae4e9…`
  unchanged before/after).
- **v1.11.0 MINOR payload verified in the dist:** HANDOFF.md composer
  present (`handoff_lines` / `render HANDOFF.md body`, bootstrap.py ~4885–
  4954); guard-fires 10-minute dedupe present
  (`GUARD_FIRES_DEDUPE_WINDOW_S = 600`, bootstrap.py:4502) and **observed
  live**: a second `check --strict` within the window appended only the 9
  verdict-carrying allowlist records (always-append by design) and skipped
  the duplicate verdict-less session-log fire (delta 9, not 10). Planted
  CLAUDE.md read-first rider (HANDOFF.md at orientation slot 2) landed in
  the **staged** `.substrate/claude/CLAUDE.md:16` — this repo has **no live
  CLAUDE.md at root**, so the run-6 delivery-gap rider stays invisible to
  worker sessions here until the lane adopts a live CLAUDE.md (chronic
  class, lane-owed; same as fleet-manager pre-#72).
- **Verify:** `python3 bootstrap.py check --strict` → exit 1 pre-flip
  **only** on this card's in-progress badge with the designed notice
  ("check: HOLD (by design) … nothing to investigate."), all other checks
  clean (9 allowlist-suppressed findings, reason-carrying). Repo test suite
  green locally: `python3 -m pytest tests/ games/exploration/tests/ -q` →
  257 passed. Auto-merge never armed (this repo is where the #40 24-second
  card-only merge happened); landing is a squash merge after the flip goes
  green.

## 💡 Session idea

The carve-out scanner's false-positive on the kit's own outgoing action
pins fired on every v1.11.0 adopter this wave (fleet-manager #72, here) —
the scanner compares the live gate against the NEW template, so every
kit-side edit to the gate template reads as "host-added" in the old live
copy. Kit-side candidate: scan against the OLD staged template
(`.substrate/ci/substrate-gate.yml` at HEAD, which the kit already owns and
ships) instead of the new one — a live gate byte-identical to the old
staged copy is definitionally carve-out-free, killing this whole
false-positive class for one `filecmp` call, while real host additions
still diff against both.

## ⟲ Previous-session review

The v1.10.1 upgrade session (#43) left exactly the checklist this session
needed: per-bank hash discipline, the never-arm-automerge-here lesson, and
the "shapes NOT exercised" idea its own review proposed — and this wave
promptly hit an unexercised shape (the carve-out scanner meeting a
kit-side pin bump for the first time), proving that review's point. What
#43 could have done better: it verified the carve-out report said "0
found" but did not record WHY zero was the expected value (live gate
byte-identical to staged template) — this session had to re-derive that
invariant to prove the false-positive harmless. Improvement to the system:
upgrade cards should record the live-gate-vs-staged-template hash equality
as a standing pre-upgrade invariant line, so any future carve-out bank can
be triaged against it in one diff.
