# 2026-07-11 — substrate-kit upgrade v1.12.0 → v1.12.1

> **Status:** `complete`

📊 Model: fable-5 · high · kit-upgrade

## What happened

Distribution-wave upgrade of the vendored substrate-kit from v1.12.0 to
v1.12.1 (kit-owned files only — no lane content, no control/ edits of any
kind on this multi-lane repo, no domain work,
`.github/workflows/tests.yml` untouched). PR #58.

- **Vendored dist:** `bootstrap.py` replaced with the v1.12.1 release asset,
  sha256 `1055ca2cfd32a83e3dab7a978b05fbec2a82932a3375de0b1034f2519c16e4aa`
  (704108 bytes), verified against `release.json` (449 bytes) before running
  (canonical path: `bootstrap.py.new` + `release.json` staged in the root,
  then `python3 bootstrap.py.new upgrade`; the upgrade self-verified sha256 +
  version and self-cleaned both inputs). Outgoing v1.12.0 dist banked at
  `.substrate/backup/bootstrap-1.12.0.py` (sha256 `77c00b81…`, byte-equal to
  the pre-upgrade vendored copy per the previous card's recorded hash).
  Exactly one new bootstrap bank; the eight older banks and the historical
  `substrate-gate.pre-regen-4f50eb4d.yml` bank are untouched;
  `last-upgrade.json` from 1.12.0 → to 1.12.1.
- **Gate workflow (the release payload):** v1.12.1 carries the
  substrate-gate false-green fix — `substrate-gate.yml` regenerated in place
  with the kit review #226 fixes: (G-1) a PR that adds one good card can no
  longer silently bypass the gate on a modified sibling card (sibling
  verdicts now ADD red, never substitute), and (G-2) session-card deletions
  are now a hard red (session memory is append-only; the old
  `--diff-filter=d` lists silently excluded deletions). Carve-out scan:
  `ran, 0 found` — live gate matched the previous kit template
  byte-for-byte, NO pre-regen bank created (normal case).
- **Planted docs:** consumer-edited: 7 · unchanged: 14 — zero
  template-improved, zero diverged; nothing to apply, nothing overwritten.
  Note: `docs/AGENT_ORIENTATION.md` now classifies plain **consumer-edited**
  (template unchanged v1.12.0 → v1.12.1), so the v1.12.0 orientation-trim
  manual merge flagged by the previous card is still outstanding and still
  lane-owed.
- **Verify:** `python3 bootstrap.py check --strict` → exit 1 pre-flip
  **only** on this card's in-progress badge with the designed notice
  ("check: HOLD (by design) … nothing to investigate."); 9
  allowlist-suppressed findings (reason-carrying, pre-existing). Repo suite:
  `python3 -m pytest -q` → 310 passed. Auto-merge never armed while born-red
  (the #40 lesson — a card-only diff merged in 24s here once); landing is a
  squash merge after the flip goes green.

## 💡 Session idea

The upgrade-report's docs table says "consumer-edited — template unchanged,
nothing to apply" for `docs/AGENT_ORIENTATION.md`, which is technically true
per-release but hides that a previous release's template delta was never
taken (the v1.12.0 diverged classification). Kit-side candidate: carry an
`outstanding` marker across upgrades — when a doc classified diverged /
template-improved in release N is still unapplied at release N+1, the N+1
report should keep flagging it (e.g. `consumer-edited · outstanding template
delta from v1.12.0`) instead of letting the pending merge fall out of the
only report an upgrade session reads.

## ⟲ Previous-session review

The v1.12.0 upgrade session (#51) left an unusually good trail: its
"Next session should know" list was directly load-bearing here (the banked
v1.12.0 sha it recorded let this session verify the new bank byte-matches
the outgoing dist without re-deriving anything, and its heads-up on the
missing `kit:` heartbeat line / missing live CLAUDE.md saved re-triage).
Its card-structure was mirrored verbatim by this card. One gap: it recorded
the AGENT_ORIENTATION.md diverged delta as "lane-owed" but created no
durable lane-visible artifact beyond the card and upgrade-report — and this
session watched that report get rewritten by the next upgrade, silently
dropping the flag (hence this session's idea above). Improvement adopted
here: state explicitly in the card when a previously-flagged item is STILL
outstanding, so the chain of custody survives report rewrites.

## Next session should know

- Kit now v1.12.1; rollback anchor `.substrate/backup/bootstrap-1.12.0.py`
  (sha256 `77c00b81…`) or `python3 bootstrap.py upgrade --rollback`.
- `docs/AGENT_ORIENTATION.md` still carries the unapplied v1.12.0
  orientation-trim template delta — lane-owed manual merge, no longer
  visible in the current `.substrate/upgrade-report.md` (rewritten by this
  upgrade); the delta text lives in the v1.12.0-era report in git history
  (PR #51).
- No live root CLAUDE.md yet (staged `.substrate/claude/CLAUDE.md` only) —
  still lane-owed.
- `kit:` heartbeat lines are stale at v1.7.1 in `control/status-mining.md`
  and `control/status-exploration.md` (`control/status.md` has none) —
  lane-owed (one-writer rule), do not update from a distribution session.
