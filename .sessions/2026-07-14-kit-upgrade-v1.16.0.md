# 2026-07-14 — kit upgrade v1.15.0 → v1.16.0

> **Status:** `complete`

- **📊 Model:** fable-5 · medium · mechanical refactor

## What is about to happen

Substrate-kit distribution wave: upgrade this repo's kit pin from v1.15.0 to
v1.16.0 using the canonical two-command recipe (`bootstrap.py.new upgrade`
then `upgrade --apply-docs`), release asset three-way sha256-verified
(bba34e2102cbaf09394f39992f0501ea5cfd542d90301ef67e31a0854ca59170,
980,026 bytes), followed by `check --strict`. Rails per Q-0261.3: kit-owned
files only; no control/, hooks, settings, or product-code edits. Auto-merge
is never armed by this session (the #40 lesson lives here); the resident
live enabler merging on green after the final card flip is the sanctioned
landing path.

## What happened

- Asset three-way sha256 verified (downloaded == release.json == expected
  bba34e21…, 980,026 B). Two-command recipe ran clean; report carries the
  `## Applied (--apply-docs)` section (6 docs applied).
- Banked exactly one new `bootstrap-1.15.0.py` (sha256 25d22af9… == the
  v1.15.0 release asset); all pre-existing banks byte-identical.
- Carve-out: the regen overwrote the host-customized
  `auto-merge-enabler.yml`, dropping the host-added "skip arming while the
  PR's own in-diff card is in-progress" guard (this repo's #40 defense).
  Restored byte-identical to origin/main (sha256 71045852…); pre-regen
  copy banked at `.substrate/backup/auto-merge-enabler.pre-regen-71045852.yml`.
- New v1.16.0 plant `docs/reading-path.md`: strict-red on arrival
  ([reachable] orphan + [unrendered-banner]). Cured by answering the three
  fleet slots (`fleet_dark_repos`, `fleet_status_command`,
  `fleet_siblings`) + `render --live`, and a minimal wiring hunk into the
  diverged `docs/AGENT_ORIENTATION.md`. Rest of the orientation template
  delta stays lane-owed (preserved in `.substrate/upgrade-report.md`).
- Verify: `python3 -m pytest` 810 passed; `check --strict` clean except
  the designed born-red HOLD, which this flip commit clears.

## Lane-owed (flagged, untouched per Q-0261.3)

- `control/status.md` still carries NO `kit:` heartbeat line (chronic).
- `docs/AGENT_ORIENTATION.md` diverged — manual merge of the remaining
  template delta.
- Advisory `[automerge-branch-drift]`: the host-edited enabler arms many
  branch prefixes but `automerge.branch_patterns` would regenerate only
  `{claude/*}` — pin the real list in `substrate.config.json` so the next
  regen doesn't narrow it.
- Advisory `[owner-action-fields]` on `control/status.md` (pre-existing).
- 20 `model-line` advisories on the 2026-07-14 night-wave sibling cards
  (effort/task-class segments not in the PL-004 taxonomy) — sibling cards
  untouched per the tail-1/shadowing doctrine.

💡 Session idea: the enabler regen silently drops host arm-guards that
exist precisely to protect kit mechanics (the in-progress-card skip is the
#40 defense) — the kit's carve-out scanner could classify guard-shaped
enabler steps as "kit-alignable" and offer to fold them into the template
instead of exiling them to a sibling workflow.

⟲ Previous-session review: the v1.15.0 upgrade (#64) left the upgrade
report's AGENT_ORIENTATION delta lane-owed and it was still unmerged when
this wave re-diverged it — confirming the report-overwrite-drops-deltas
class; workflow improvement: an outstanding-deltas ledger carried forward
across upgrades (already filed kit-side) would have preserved it without
relying on PR-body prose.

