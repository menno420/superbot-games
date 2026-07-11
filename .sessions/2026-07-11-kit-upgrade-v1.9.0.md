# 2026-07-11 — substrate-kit upgrade v1.8.0 → v1.9.0

> **Status:** `in-progress`

📊 Model: fable-5 · high · kit-upgrade

## What happened

Distribution-wave upgrade of the vendored substrate-kit from v1.8.0 to v1.9.0
(kit-owned files only — owner directive Q-0261.3; no lane content, no control/
edits beyond the kit-owned claim file, no domain work).

- **Vendored dist:** `bootstrap.py` replaced with the v1.9.0 release asset,
  sha256 `55181082c796657c8e5e14750d248cea2df9e69a9aa896dd8a8c7f1adfb9cc90`,
  verified against `release.json` before running (canonical path:
  `bootstrap.py.new` + `release.json` staged in the root, then
  `python3 bootstrap.py.new upgrade`; the upgrade self-cleaned both inputs).
  Outgoing v1.8.0 dist banked at `.substrate/backup/bootstrap-1.8.0.py`
  (byte-equal to the pre-upgrade vendored copy, sha256 `28c5dcb6…`); the
  pre-existing banks `bootstrap-1.2.0.py` (`258ab02a…`), `bootstrap-1.7.0.py`
  (`00f4f4cd…`) and `bootstrap-1.7.1.py` (`2aa4fedd…`) are byte-untouched
  (hash-verified before/after). Expected backup dir after this run:
  `bootstrap-1.2.0.py`, `bootstrap-1.7.0.py`, `bootstrap-1.7.1.py`,
  `bootstrap-1.8.0.py`, `last-upgrade.json`, `state.json` — nothing else.
- **v1.9.0 plants:** root `.ignore` + `.gitattributes` (search hygiene —
  fresh plants here, no pre-existing host content; the kit only appends).
  The CLAUDE.md "Kit machinery — search hygiene" section landed
  **staged-only** at `.substrate/claude/CLAUDE.md` (this repo has no live
  CLAUDE.md). The `.sessions/README.md` model-attribution doctrine
  (family-level self-report is attribution ground truth) is in the v1.9.0
  template but the host file was `kept` — **doctrine not live here**;
  this repo already carries the equivalent rule via fm ORDER 003 (#39).
  SessionStart handoff push verified live: `bootstrap.py hook sessionstart`
  renders "## Handoff — the previous session's trail (pushed…)" pointing at
  the newest card.
- **Live gate regenerated** kit-owned from the v1.9.0 template, byte-equal to
  staged `.substrate/ci/substrate-gate.yml`. New in v1.9.0: the advisory
  born-red lane now grammar-lints the ADDED card (`check … --added-card`) —
  born-red incompleteness stays exempt, malformed grammar reds. Zero
  `pytest` references in the regenerated gate; `.github/workflows/tests.yml`
  (the pytest carve-out home) untouched by the regen — not in the diff.
- **Carve-out report:** `.substrate/upgrade-report.md` § Carve-out scan:
  "carve-out scan: .github/workflows/substrate-gate.yml — ran, 0 found".
- **Docs pass:** consumer-edited: 7 · unchanged: 14 · diverged: 0 ·
  missing: 0. `control/README.md` reclassified `diverged` (v1.8.0) →
  `consumer-edited` ("template unchanged — consumer-owned, nothing to
  apply") — the v1.8.0-owed manual merge of its template delta is still
  lane-owed, but the v1.9.0 template did not move again. No
  `required_context` validation advisory was emitted by upgrade or check.
- **Verify:** `python3 -m pytest tests/ games/exploration/tests/ -q` →
  257 passed (tests.yml count floor 257 exactly met); gate YAML parses;
  `python3 bootstrap.py check --strict` → exit 1 **only** on this card's
  in-progress badge with the designed notice ("check: HOLD (by design):
  session card … declares an in-progress Status — the born-red session gate
  holds the merge red until the card flips complete."), all other checks
  clean.
- **Session-PR anomaly (recorded for the wave):** the intended born-red
  session PR #40 (card + claim only) auto-merged 24s after
  `enable_pr_auto_merge` armed it — a card-only diff rides the gate's
  added-card **advisory heartbeat lane** (green by design), so pre-arming
  auto-merge on a card-only PR merges it instantly. The upgrade itself
  landed via PR #41 from the same branch; the flip-to-complete commit
  engages the locked-door gate there (card MODIFIED + gate regen in the
  same PR). Lesson for the distribution runbook: **on repos with working
  auto-merge, don't arm it until the PR contains work the gate actually
  holds** — either push card+work before arming, or arm at close-out.

## 💡 Session idea

The added-card advisory lane plus pre-armed auto-merge turns every born-red
heartbeat PR into an instant merge — correct for claims, surprising for
session PRs (this session's #40). Kit-side candidate: `enable auto-merge`
guidance in the gate header, or a gate notice line when the advisory lane
passes a card-only diff ("heartbeat lane: this PR merges green while
born-red — arm auto-merge only if that is intended"), so the arming decision
is informed at the moment it happens.

## ⟲ Previous-session review

Previous-session review: the v1.8.0 upgrade card set the baseline this
session leaned on — its explicit expected-backup-contents list let this
session verify the bank state by simple diff (all three prior banks
byte-identical, exactly one new bank), and its "zero pytest in gate /
tests.yml untouched" checks transferred verbatim. One gap it left: it armed
nothing born-red (auto-merge was enabled on a PR that already carried the
upgrade), so the heartbeat-lane instant-merge failure mode this session hit
was undiscovered — evidence that "worked last wave" for auto-merge was
about the arming *timing*, not the tool. Improvement carried forward:
distribution runbooks should state when to arm, not just whether arming
works.
