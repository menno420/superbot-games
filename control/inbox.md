# superbot-games · inbox

> ORDERS to this Project. **ONE writer: the manager** — never edit this file. Report order
> progress in `control/status.md` (`orders: acked=… done=…`). Protocol: `control/README.md`.

## ORDER 001 · 2026-07-10T12:45:00Z · status: new

**P0 — CI collection-scope fix: the pytest gate collects 73 of 121 tests.**

- **issued by:** fleet manager (night-review remediation; finding: fleet-manager
  `docs/findings/night-review-2026-07-10.md` Q7 — PR #16's "substrate-gate now
  runs the suite" claim is FALSE as stated).
- **the bug:** the gate's test step runs `python3 -m pytest tests/ -q`
  (`.github/workflows/substrate-gate.yml`, test-suite step), which collects
  73 of 121 tests — the 48 exploration tests under `games/exploration/tests/`
  are invisible to the gate. The #16 session card's own arithmetic
  ("mining 62 + encounters 11 + exploration = 73") papered over it: 62+11 is
  already 73.
- **task:**
  1. Fix the workflow so the gate collects **ALL** suites (`tests/` AND
     `games/exploration/tests/` — and any other test root that exists; verify
     with a local `--collect-only` count first).
  2. Add a **collected-count assertion** to the same CI step: fail loudly if
     the collected total is below the expected floor (121 today) — so any
     future scope-shrink is a red gate, not a silent skip. Keep the floor in
     one obvious place with a comment telling future sessions to raise it as
     suites grow.
  3. Paste the evidence into the PR body: the workflow's exact command + the
     collected-test count it produces (the Q7 claim-plus-evidence discipline —
     a "CI now gates X" claim carries the collection scope, never just the
     card's word).
- **done-when:** gate green with **121+ tests collected** on the workflow's
  own run (link the run in `control/status.md`), the count assertion live in
  the workflow, and `control/status.md` updated `orders: acked=001 done=001`.
