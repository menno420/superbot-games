# 2026-07-10 — substrate-kit upgrade v1.2.0 → v1.7.0

> **Status:** `complete`

📊 Model: Claude Fable 5 (claude-fable-5)

## What happened

Distribution-wave upgrade of the vendored substrate-kit from v1.2.0 to v1.7.0
(kit-owned files only — owner directive Q-0261.3; no lane content, no control/
edits, no domain work).

- **Vendored dist:** `bootstrap.py` replaced with the v1.7.0 release asset,
  sha256 `00f4f4cd39351b17389b9abab3be88fcb0c9f4dee9ad8f1639ad1fc67fdb5238`
  verified against `release.json` before running. Old dist archived at
  `.substrate/backup/bootstrap-1.2.0.py`; `substrate.config.json`
  `kit_version` → `1.7.0` (plus the new `heartbeat_files` default).
- **`upgrade --apply-docs`:** re-rendered the two consumer-untouched planted
  docs (`CONSTITUTION.md`, `docs/collaboration-model.md`). New plant:
  `docs/CAPABILITIES.md`, wired into `docs/AGENT_ORIENTATION.md` by
  hand-applying the exact v1.7.0 template delta from the upgrade report
  (fixes the strict `reachable` orphan finding the plant introduced).
- **Live gate refreshed** from the staged v1.7.0 template
  (`cp .substrate/ci/substrate-gate.yml .github/workflows/substrate-gate.yml`
  — kit-owned per kit PR #130): no-card sentinel, born-red ADDED-card
  advisory, MODIFIED-card locked door, `--status-only` control fast lane.
- **Host carve-out preserved:** the pure-domain pytest step (repo PR #16)
  would have been silently dropped by the gate refresh — relocated verbatim
  to `.github/workflows/tests.yml` (the kit-prescribed separate-file home for
  host carve-outs). 73/73 tests pass locally.
- **Verify:** `python3 bootstrap.py check --strict` green on the final tree
  (only this card's own in-progress badge held it red before the flip);
  CI-shape command (`--session-log` sentinel) exit 0.
- Evidence: `.substrate/upgrade-report.md` (committed, quoted in the PR body).

## Lane-owed follow-ups (flagged, not done — scope fence)

1. Each lane updates its own heartbeat `kit:` line to
   `kit: v1.7.0 · check: green · engaged: yes` on its next status overwrite
   (both `control/status-*.md` still say v1.2.0; the kit's adopters-registry
   currency checker will show DRIFT until then).
2. Register the per-lane status files in `substrate.config.json`
   `heartbeat_files` (v1.4.0 multi-lane convention; the upgrade seeded only
   the default `control/status.md`) — or run `adopt --lane <name>`.
3. Hand-merge the diverged `control/README.md` template delta (order-claiming
   ritual + OWNER-ACTION six-field format) from the upgrade report if wanted.
4. New live conventions now in force: inbox pure-append discipline,
   `claimed-by:` order claiming (advisory), six-field OWNER-ACTION asks
   (advisory), born-red ADDED-card advisory / MODIFIED-card locked-door gate.
5. Consider making the relocated `tests` workflow a required check — the gate
   context stays `substrate-gate`; `tests` is new and unrequired, so
   auto-merge does not wait on it.

## 💡 Session idea

The v1.7.0 gate template still doesn't wire `check --inbox-base`, so the
"inbox append-only is CI-gated" convention is latent here too (same finding as
the fleet-manager upgrade). When the kit ships a wired template, this repo
gets it free at the next upgrade — but a lane could add the flag to the gate's
check invocation via a kit-side proposal now; route to substrate-kit as a KI
candidate rather than hand-editing the kit-owned workflow.

## ⟲ Previous-session review

Previous-session review: the ORDER 002 session (#21, self-arm wake routine)
landed cleanly with a control-only diff riding the fast lane — good use of the
lane. What it (and every session since adoption) could not have caught: the
repo's only test CI lived as a hand edit inside the kit-owned gate workflow,
one upgrade away from silent deletion. Improvement shipped this session: the
carve-out now lives in its own workflow file where upgrades can't touch it.
