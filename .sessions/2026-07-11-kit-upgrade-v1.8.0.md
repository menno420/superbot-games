# 2026-07-11 — substrate-kit upgrade v1.7.1 → v1.8.0

> **Status:** `complete`

📊 Model: Claude Fable 5 (claude-fable-5)

## What happened

Distribution-wave upgrade of the vendored substrate-kit from v1.7.1 to v1.8.0
(kit-owned files only — owner directive Q-0261.3; no lane content, no control/
edits, no domain work).

- **Vendored dist:** `bootstrap.py` replaced with the v1.8.0 release asset
  (tag 63c6b39), 625,066 bytes, sha256
  `28c5dcb64b713dde8d64a513a9a1aa860b4a07bf17d832686f0009932dc89b9b`
  verified against `release.json` before running (canonical path:
  `bootstrap.py.new` + `release.json` staged in the root, then
  `python3 bootstrap.py.new upgrade`; the upgrade self-cleaned both inputs).
  Outgoing v1.7.1 dist banked at `.substrate/backup/bootstrap-1.7.1.py`
  (byte-equal to the pre-upgrade vendored copy, sha256 `2aa4fedd…`); the
  pre-existing banks `bootstrap-1.7.0.py` (`00f4f4cd…`) and
  `bootstrap-1.2.0.py` (`258ab02a…`) are byte-untouched (hash-verified
  before/after — the exact expected-backup-contents baseline the v1.7.1
  card's review asked for). Expected backup dir after this run:
  `bootstrap-1.2.0.py`, `bootstrap-1.7.0.py`, `bootstrap-1.7.1.py`,
  `last-upgrade.json`, `state.json` — nothing else.
- **v1.8.0 plants:** `control/claims/README.md` (unified work-claim
  convention, one file per claim) and `scripts/env-setup.sh` (setup-script
  contract; `scripts/` did not exist here, so this was a fresh plant — the
  skip-if-exists guard had nothing to skip). Auto-merge enabler is now
  kit-owned and landed **staged-only** at `.substrate/ci/auto-merge-enabler.yml`
  — correct for this repo, where it has never been live
  (`.github/workflows/` still holds exactly `substrate-gate.yml` + `tests.yml`).
- **Live gate regenerated** kit-owned from the v1.8.0 template, byte-equal to
  the staged `.substrate/ci/substrate-gate.yml`. New in v1.8.0 (kit #156):
  the session-gate **hold-tightening** — a PR that regenerates the gate
  itself keeps the full locked door even on a newly-ADDED card, so this very
  PR stays red until this card flips `complete`. Zero `pytest` references in
  the regenerated gate; `.github/workflows/tests.yml` (the pytest carve-out
  home) untouched by the regen — not in the diff.
- **Carve-out report (kit #156):** the upgrade report now carries an explicit
  `## Carve-out scan` section even at zero:
  "carve-out scan: .github/workflows/substrate-gate.yml — ran, 0 found" —
  correct, the pytest carve-out lives in `tests.yml`, outside the gate.
- **Docs pass:** consumer-edited: 6 · diverged: 1 · missing: 2 (the two new
  plants) · unchanged: 12. The one diverged doc is `control/README.md`
  ("both the template and the doc moved — manual merge"): the v1.8.0
  template adds a "Claiming work" section + grammar-source-of-truth notes;
  the upgrade correctly did NOT touch the consumer-owned file and recorded
  the delta in `.substrate/upgrade-report.md` § "Template deltas" for a
  lane-local manual merge (left for the repo's own lane — out of Q-0261.3
  kit-upgrade scope).
- **Verify:** `python3 -m pytest tests/ games/exploration/tests/ -q` → 204
  passed (tests.yml count floor exactly met); `python3 bootstrap.py check
  --strict` → exit 0 on the final tree (only this card's own in-progress
  badge held it red before the flip); gate YAML parses.

## 💡 Session idea

The v1.8.0 upgrade classifies `control/README.md` as diverged and records a
clean template delta, but nothing downstream *tracks* that a manual merge is
owed — a diverged doc's delta sits in the upgrade report until someone
rereads it. Kit-side candidate: `check` could carry an advisory
"unapplied template delta from vN" nag keyed on the upgrade report's
diverged entries, so owed manual merges surface every session instead of
silently aging out with the next upgrade's report rewrite.

## ⟲ Previous-session review

Previous-session review: the v1.7.1 upgrade card (#23) set the standard this
session leaned on — its explicit sha256 of the pre-upgrade vendored dist
(`2aa4fedd…`) is exactly what let this session verify the new
`bootstrap-1.7.1.py` bank byte-matches the dist it replaced, and its review
asked for a stated expected-backup-contents baseline, which this card now
provides. One gap: it verified "no carve-out section = zero carve-outs" by
inference; v1.8.0's explicit zero-carve-out section (kit #156a) closes
precisely that ambiguity upstream — evidence the session-review → kit-fix
loop is working end-to-end. Improvement carried forward: keep stating the
expected backup-dir contents in every upgrade card so the next upgrade diffs
against a baseline instead of reverse-engineering provenance.
