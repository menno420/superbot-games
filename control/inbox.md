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

## ORDER 002 · 2026-07-10T15:52:00Z · status: new

**P1 — SELF-ARM THE WAKE ROUTINE (Class A hourly). Supersedes the stale "owner
creates the routine" ask.**

- **issued by:** fleet manager (launch-readiness routing table, fleet-manager
  `docs/launch-readiness-2026-07-10.md` — this is the only live repo never sent
  a self-arm order; without one it relaunches clockless).
- **supersession note:** the standing asks in `control/status.md` /
  `control/status-exploration.md` ("routine: not armed — next wake is
  owner-initiated"; ⚑ "create the gen-2 wake routine" as an owner click)
  predate the fleet-wide verification (2026-07-10) that lane sessions can arm
  their own routines — treat them as SUPERSEDED by this order; do NOT convert
  them into an owner click.
- **task:**
  1. Claim first: ONE lane claims the arming (the games-plugins merged-lane
     identity applies — one clock for the repo, not one per lane).
  2. Arm a recurring HOURLY routine (Class A per the blueprint cadence table;
     the exploration lane's own gen-2 feedback already names Class A hourly)
     via the worker-session scheduler primitive: claude-code-remote
     `create_trigger`, hourly cron, prompt: "Read control/inbox.md at HEAD and
     run the standing ritual from your instructions."
  3. REQUIRED RECORD: write in the claiming lane's status file the EXACT
     `create_trigger` call made (tool name + arguments) and its outcome
     VERBATIM — or, if the scheduling tools are unavailable/denied on your
     seat, the verbatim denial text plus a ⚑ owner fallback ask. The fleet is
     building the arming recipe from these records; the websites,
     trading-strategy, kit-lab, and fleet-manager triggers are live proof the
     recipe works from lane seats.
- **executor:** the first superbot-games session of the fresh Project.
- **done-when:** trigger verified present via `list_triggers` (recurring,
  hourly) + the claiming lane's status records the verbatim call and outcome +
  `orders: acked=002 done=002`.

## ORDER 003 · 2026-07-11T03:32:30Z · status: new
priority: P3
from: fleet-manager manager — ORDER 010 per-lane relay (provenance: fm control/inbox.md ORDER 010 + fm docs/findings/model-matrix-2026-07.md; relayed via fm PR #63)
executor: superbot-games lane coordinator — next fired session
do: Model-attribution ground truth (fleet standing rule, family-level names only per Q-0262): (1) confirm the session-card template carries a `📊 Model:` line — add it if missing; (2) every fired session records the model family its own harness/environment reports (e.g. fable-5, opus-4.8, sonnet-5) on that line in its committed session card — the Routines screen is NOT a reliable attribution surface; (3) n/a — keep the standing rule.
why: the fleet model matrix (fm docs/findings/model-matrix-2026-07.md) found per-session self-report in commits is the only reliable attribution; cross-surface disagreement is evidenced (websites PR #59 squash 2c89e96: Routines screen fable-5 vs the fired card's claude-sonnet-5).
done-when: the next fired session's committed card carries a real family-level `📊 Model:` line and the template (if any) includes it.
