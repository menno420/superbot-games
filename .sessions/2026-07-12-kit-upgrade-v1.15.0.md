# 2026-07-12 — substrate-kit upgrade v1.14.0 → v1.15.0

> **Status:** `complete`

- **📊 Model:** fable-5 · kit-upgrade distribution wave

## What happened

Distribution-wave upgrade of the vendored substrate-kit from v1.14.0 to
v1.15.0 (kit-owned files only — no lane content, no `control/inbox.md`,
no `control/status*.md` edits; the multi-lane heartbeat `kit:` lines are
lane-owed and were not bumped). PR #64.

- **Vendored dist:** `bootstrap.py` replaced with the v1.15.0 release
  asset, sha256
  `25d22af9d9d81b2a7dc6d8d500234b6aa0f3f1c6a0400284ce2381baaeac650e`
  (828,825 bytes), three-way verified before running: release asset =
  `release.json` sha256 field = kit repo `eaf4f23:dist/bootstrap.py`
  (tag v1.15.0 = annotated `0b26d41` → `eaf4f23`). Canonical two-command
  flow (`python3 bootstrap.py.new upgrade`, then `python3 bootstrap.py
  upgrade --apply-docs`); the tool self-cleaned both inputs. Outgoing
  v1.14.0 dist banked at `.substrate/backup/bootstrap-1.14.0.py`
  (`47c1b8b9…`, byte-equal to the pre-upgrade vendored copy at
  `bdc4cd1:bootstrap.py`); pre-existing banks untouched.
- **Docs report:** consumer-edited: 4 · diverged: 3 · template-improved:
  2 · unchanged: 14. New plants: `docs/ROUTINES.md` (routines/wake-chain
  doctrine) + `docs/seat-digest.md` (derived render, "already current —
  nothing to refresh"). `--apply-docs` applied CONSTITUTION.md +
  docs/SKILLS.md. Capability-seed: no refresh line — CAPABILITIES.md
  classed `unchanged`. Carve-out scan: `substrate-gate.yml — ran, 0
  found` (kept, already current); `tests.yml` untouched.
- **Manual merge (minimal wiring only):** `docs/AGENT_ORIENTATION.md`
  diverged → the expected `[reachable] ROUTINES.md` orphan fired (same
  class as the v1.13.0 SKILLS.md orphan); hand-merged only the one-line
  read-path addition (`docs/ROUTINES.md ·`), clearing it. The remaining
  template delta (git-preflight boot section + ROUTINES routing
  paragraph) stays lane-owed.
- **Lane-owed, recorded verbatim in the PR body (not failures):** the 4
  consumer-edited docs (docs/decisions.md, docs/current-state.md,
  docs/ideas/README.md, control/inbox.md); the `control/README.md` +
  `control/status.md` diverged deltas (kit-token-PLAIN grammar warning +
  version-truth-defers-to-generated-registry note — `control/`
  one-writer discipline keeps them out of a distribution PR; full diffs
  preserved in `.substrate/upgrade-report.md`); the pre-existing
  `owner-action-risk-class` advisory on `control/status.md`.
- **Verify:** `python3 -m pytest -q` → 310 passed. `python3 bootstrap.py
  check --strict` → red only on this card's designed in-progress hold
  (9 allowlist-suppressed findings pre-existing). Auto-merge never
  armed; landing is a squash merge on green (#62/#63 precedent).

## 💡 Session idea

The upgrade report classes `docs/seat-digest.md` as "already current —
nothing to refresh" even when the file did not exist before the wave and
was planted fresh seconds earlier by the same run — the plant and the
refresh report read as contradictory unless you check `git status`. A
one-word class distinction in the seat-digest report line ("planted
fresh" vs "refreshed" vs "already current") would let distribution
workers record the outcome mechanically instead of re-deriving it from
the working tree — the same legibility gap the v1.14.0 card flagged for
diverged-doc ownership hints.

## ⟲ Previous-session review

The v1.14.0 wave card was the right template for this wave: its explicit
"no orphan fired → no manual merge needed" note made this wave's inverse
case (orphan fired → minimal wiring hunk) a mechanical decision, and its
choice to verify only the *new* bank (dropping the O(n) all-banks ritual
the v1.13.0 card flagged) was adopted here unchanged. One improvement it
surfaces: it recorded the carve-out classes but not the report's *count
line* verbatim ("consumer-edited: 6 · diverged: 1 · …"); this card and
PR body quote the count line directly so future waves can diff carve-out
drift across versions at a glance — a habit, not a workflow change.
