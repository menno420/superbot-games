# 2026-07-12 — substrate-kit upgrade v1.13.0 → v1.14.0

> **Status:** `complete`

- **📊 Model:** Fable 5 · kit-upgrade distribution wave

## What happened

Distribution-wave upgrade of the vendored substrate-kit from v1.13.0 to
v1.14.0 (kit-owned files only — no lane content, no control/ heartbeat
edits, `.github/workflows/tests.yml` untouched). PR #63.

- **Vendored dist:** `bootstrap.py` replaced with the v1.14.0 release
  asset, sha256
  `47c1b8b954be2f587d88f7ed5923870883deab88a8fa7fbf2bb755decc2ee581`
  (779,399 bytes), three-way verified before running: release asset =
  `release.json` sha256 field = kit repo `743a1fc:dist/bootstrap.py`
  (canonical path: `bootstrap.py.new` + `release.json` staged in the
  root, `python3 bootstrap.py.new upgrade`; the tool self-verified and
  self-cleaned both inputs). Outgoing v1.13.0 dist banked at
  `.substrate/backup/bootstrap-1.13.0.py` (`982b2667…`, byte-equal to
  the pre-upgrade vendored copy per the previous card's recorded hash).
- **Docs report:** consumer-edited: 6 · diverged: 1 (control/README.md)
  · template-improved: 5 · unchanged: 10. `upgrade --apply-docs`
  (mandatory second step) applied the 5 template-improved,
  consumer-untouched docs: CONSTITUTION.md, docs/collaboration-model.md,
  docs/question-router.md, docs/CAPABILITIES.md, docs/SKILLS.md.
  Capability-seed: CAPABILITIES.md consumer-untouched — whole file
  refreshed via --apply-docs, no fence-only refresh needed. Carve-out
  scan: `substrate-gate.yml — ran, 0 found` (kept, already current).
- **Lane-owed, recorded verbatim in the PR body (not failures):** the 6
  consumer-edited docs; the control/README.md diverged manual merge
  (template delta = OWNER-ACTION `RISK:` line + new "Owner-assist output
  standard" section — control/ one-writer discipline keeps it out of a
  distribution PR; full diff preserved in `.substrate/upgrade-report.md`);
  the v1.14.0 Q-0270-collapse note (venue-scoped capability ledger now
  carries the boot-triad/venue-posture rule — any local prose copy should
  collapse to a pointer); the pre-existing `owner-action-risk-class`
  advisory on control/status.md.
- **Verify:** `python3 -m pytest -q` → 310 passed. `python3 bootstrap.py
  check --strict` → red only on this card's designed in-progress hold
  (9 allowlist-suppressed findings pre-existing; unlike the v1.13.0 wave,
  NO SKILLS.md `[reachable]` orphan fired — SKILLS.md was
  template-improved, not replanted, so no manual orientation wiring was
  needed). Auto-merge never armed; landing is a squash merge on green.

## 💡 Session idea

The upgrade report's "Template deltas for diverged docs" section prints
the full diff but not *who owes the merge*. For repos with one-writer
zones (this repo's `control/`), `bootstrap.py upgrade` could tag each
diverged doc with an ownership hint from `substrate.config.json` (e.g.
`owned-by: lane-heartbeat` for `control/**`) so a distribution worker can
mechanically classify "merge here" vs "record verbatim, lane-owed"
instead of re-deriving the one-writer rule each wave — this exact
classification is re-reasoned manually in every distribution card since
v1.12.x.

## ⟲ Previous-session review

The v1.13.0 wave card (`.sessions/2026-07-12-kit-v1130-upgrade.md`) was
exemplary on integrity bookkeeping (three-way sha, per-bank byte-equal
verification) and its card explicitly explained *why* the
AGENT_ORIENTATION manual merge was required (gate-red causality), which
made this wave's "no orphan fired → no manual merge needed" decision
trivially derivable. One improvement it surfaced: it verified all 9
older banks byte-identical each wave — useful once, but O(n) growing
ritual; a single kit-side `check` finding (bank-hash drift) would make
per-wave re-verification redundant. This wave verified only the new bank
against the pre-upgrade vendored copy accordingly.
