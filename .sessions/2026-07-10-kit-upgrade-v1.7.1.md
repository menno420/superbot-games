# 2026-07-10 — substrate-kit upgrade v1.7.0 → v1.7.1

> **Status:** `complete`

📊 Model: Claude Fable 5 (claude-fable-5)

## What happened

Distribution-wave upgrade of the vendored substrate-kit from v1.7.0 to v1.7.1
(kit-owned files only — owner directive Q-0261.3; no lane content, no control/
edits, no domain work).

- **Vendored dist:** `bootstrap.py` replaced with the v1.7.1 release asset,
  sha256 `2aa4feddf7de7e20b00f46866826985ca8fd11f40bc51ebe261bbdef3118486d`
  verified against `release.json` before running (canonical path:
  `bootstrap.py.new` + `release.json` staged in the root, then
  `python3 bootstrap.py.new upgrade`; the upgrade self-cleaned both inputs).
  Old v1.7.0 dist banked at `.substrate/backup/bootstrap-1.7.0.py`
  (byte-equal to the pre-upgrade vendored copy, sha256 `00f4f4cd…`; the
  upgrade reported it "already banked" — PR #22 had committed that copy);
  `substrate.config.json` `kit_version` → `1.7.1`.
- **Live gate regenerated** kit-owned from the v1.7.1 template, byte-equal to
  the staged `.substrate/ci/substrate-gate.yml`. New in v1.7.1: the
  **inbox append-only gate** step (`check --strict --status-only --inbox-base`)
  — `control/inbox.md` pure-append + ORDER grammar is now CI-enforced (the
  latent-convention gap flagged in the v1.7.0 session idea is closed upstream).
- **Host carve-out protection verified (kit #137 live exercise):**
  `.github/workflows/tests.yml` (the pytest carve-out relocated out of the
  gate in PR #22) is untouched by the regen — not in the diff; the
  regenerated gate carries **no host jobs** (zero `pytest` references); the
  upgrade report has **no carve-out section** = zero carve-outs detected
  (the pre-upgrade gate was byte-identical to the v1.7.0 template).
- **Docs pass:** consumer-edited: 7 · unchanged: 12 · zero
  diverged/template-improved — no doc applies needed this release.
- **Verify:** `python3 -m pytest tests/ -q` → 73 passed (tests.yml command);
  `python3 bootstrap.py check --strict` → exit 0 on the final tree (only this
  card's own in-progress badge held it red before the flip); gate YAML parses.

## 💡 Session idea

The upgrade's "already banked" path silently accepts a pre-existing
`.substrate/backup/bootstrap-<old>.py` as the rollback anchor without
re-verifying it is byte-equal to the vendored copy being replaced. Here it
was (verified by hand, sha256 match), but a corrupted or hand-edited banked
copy would poison `upgrade --rollback`. Kit-side candidate: the upgrade
should hash-compare an "already banked" backup against the live vendored
dist and refuse (or re-bank) on mismatch — route to substrate-kit as a KI
proposal, not a hand edit.

## ⟲ Previous-session review

Previous-session review: the v1.7.0 upgrade session (#22) did the hard thing
right — it spotted that the repo's only test CI lived inside the kit-owned
gate and relocated it to `tests.yml` before the regen could delete it, which
is exactly what made this session's regen safe to take blind. One gap: it
banked `bootstrap-1.7.0.py` (a copy of the then-NEW dist) without noting why
in the card, which cost this session a provenance chase before the upgrade
tool explained it ("already banked"). Improvement: a kit-upgrade card should
list the exact expected backup-dir contents after its run, so the next
upgrade can diff against a stated baseline instead of reverse-engineering.
