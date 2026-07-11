# 2026-07-11 — substrate-kit upgrade v1.9.0 → v1.10.0

> **Status:** `complete`

📊 Model: fable-5 · high · kit-upgrade

## What happened

Distribution-wave upgrade of the vendored substrate-kit from v1.9.0 to
v1.10.0 (kit-owned files only — owner directive Q-0261.3; no lane content,
no control/inbox.md or control/status.md edits, no domain work). PR #42.

- **Vendored dist:** `bootstrap.py` replaced with the v1.10.0 release asset,
  sha256 `ba69fc5cf21619cc85e4c733ebe3d9eda8803e678f810fcc39b94d60c2f3b5a4`,
  verified against `release.json` before running (canonical path:
  `bootstrap.py.new` + `release.json` staged in the root, then
  `python3 bootstrap.py.new upgrade`; the upgrade self-verified sha256 +
  version and self-cleaned both inputs). Release facts three-way verified
  upstream: tag `v1.10.0` @ `1b5db16f66…`, release run 29142780212.
  Outgoing v1.9.0 dist banked at `.substrate/backup/bootstrap-1.9.0.py`
  (byte-equal to the pre-upgrade vendored copy, sha256 `55181082…`); the
  four pre-existing banks `bootstrap-1.2.0.py` (`258ab02a…`),
  `bootstrap-1.7.0.py` (`00f4f4cd…`), `bootstrap-1.7.1.py` (`2aa4fedd…`)
  and `bootstrap-1.8.0.py` (`28c5dcb6…`) are byte-untouched
  (hash-verified before/after). Exactly one new backup.
- **Live gate regenerated** kit-owned from the v1.10.0 template, byte-equal
  to staged `.substrate/ci/substrate-gate.yml`. **This closes the card-only
  born-red loophole discovered on this repo (#40):** the added-card lane now
  runs `check --strict --session-log .sessions/__born-red-card-added__.md
  --added-card "$card"` under an engine where an ADDED in-progress/drafted
  card returns a locked-door `session-card-hold` (never allowlistable) —
  a card-only born-red PR no longer rides the advisory lane green.
  Gate-touching PRs additionally run `--simulate-added-card` so the lane's
  would-be verdict stays observable. Zero `pytest` references in the
  regenerated gate; `.github/workflows/tests.yml` untouched (not in the
  diff; sha256 identical before/after).
- **First exercise of the fix on this repo:** this PR's card-only first
  commit (8855422) ran under the OLD v1.9.0 gate and went green one last
  time (run 29143746393 — the #40 loophole demonstrated pre-fix; safe
  because auto-merge was deliberately NOT armed while card-only). The
  payload commit (daf9a65) ran the NEW gate (run 29143818799): locked-door
  red with the designed HOLD banner, and the in-run simulation printed
  "check: simulate-added-card … — the added-card lane would HOLD (born-red:
  the card declares an in-progress/drafted Status; the gate would stay red
  until it flips complete)." — i.e. under the new gate even a card-only
  diff with this in-progress card is HELD. Local `check
  --simulate-added-card` reproduced the same verdict verbatim.
- **Retroactive doctrine append:** `.sessions/README.md` gained the
  model-attribution doctrine (ORDER 012) via the new append-only path —
  the pre-existing host content is byte-preserved as an exact prefix
  (+481 bytes appended under the provenance marker
  `<!-- substrate-kit: model-attribution doctrine … -->`). The v1.9.0-wave
  lane-owed "doctrine adoption" item is hereby closed by the kit itself.
- **Carve-out report:** `.substrate/upgrade-report.md` § Carve-out scan:
  "carve-out scan: .github/workflows/substrate-gate.yml — ran, 0 found".
  Docs pass: consumer-edited: 7 · unchanged: 14 · diverged: 0 · missing: 0.
- **Verify:** `python3 -m pytest tests/ games/exploration/tests/ -q` →
  257 passed (tests.yml count floor 257 exactly met); gate YAML parses;
  `python3 bootstrap.py check --strict` → exit 1 **only** on this card's
  in-progress badge with the designed notice ("check: HOLD (by design):
  session card … declares an in-progress Status — the born-red session
  gate holds the merge red until the card flips complete."), all other
  checks clean. Tests run 29143818800 green on the payload commit.

## 💡 Session idea

The gate's added-card HOLD message tells the agent to "flip the card
complete" but not the *other* half of the #40 lesson — when it is safe to
arm auto-merge. Kit-side candidate: the HOLD banner (and the
simulate-added-card verdict line) could append one clause — "auto-merge may
be armed now; this hold keeps the PR red until the flip" — turning the gate
itself into the arming-timing documentation, so the next agent doesn't need
wave-memory to know pre-arming is now safe on held PRs (and remains unsafe
nowhere).

## ⟲ Previous-session review

The v1.9.0 upgrade session (#40/#41) turned its own failure into this wave's
guardrails: its card recorded the 24-second card-only auto-merge with the
exact mechanism (advisory lane + pre-armed auto-merge) and the mergeable_
state:"dirty" zero-CI anomaly, and both transferred directly — this session
never armed auto-merge while card-only and hit neither failure. What it
could have done better: it framed the loophole only as an arming-timing
lesson; the durable fix (gate-side hold) came from the kit lane a wave
later. Improvement to the system: when a session discovers a gate-semantics
failure, its card should record both the behavioral workaround AND a named
kit-side fix candidate in the same entry — the #40 card's "Session idea" did
exactly this, and it landed as v1.10.0's headline fix within two waves;
that loop (failure → idea → shipped fix → first-exercise verification on
the discovering repo) is the workflow working as designed and worth naming
as the template.
