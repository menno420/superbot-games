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

## ORDER 004 · 2026-07-11T09:59Z · status: new
priority: P1
from: fleet-manager — owner-requested fleet-wide self-review (2026-07-11), relayed by the fleet-manager coordinator on the owner's in-session instruction
executor: superbot-games seat (next wake)
do: quick self-review of this lane covering roughly the last 24h (2026-07-10 ~20:00Z → now): (1) anything that WENT WRONG — red CI runs, guard/classifier denials, walls hit, drift found, mistakes made or corrected — each with a citation (PR/run/commit); (2) anything REQUIRING OWNER ATTENTION — owner-only asks, pending vetoes, risky decisions taken decide-and-flag, spend/publish items — click-level and plain language; (3) one-line current health (what shipped, what's next). Commit the review as a dated "Self-review 2026-07-11" section in control/status.md (or this lane's report convention); mirror ⚑ owner-attention items on the heartbeat so the manager sweep collects them.
why: owner-requested fleet-wide self-review (2026-07-11), relayed by the fleet-manager coordinator on the owner's in-session instruction.
done-when: the self-review section is on main within this lane's next two wakes.
provenance: filed by fleet-manager on coordinator direction (cse_012o8pySy5K3AV6JWoPKryZL), owner-directed.

## ORDER 005 · 2026-07-12T08:30Z · status: new
priority: P2
owner: SuperBot World coordinator (executor)
provenance: filed by the fleet manager — relocation of startup-prompt v3.1 W3 (prompts are STATELESS since v3.2, owner correction 2026-07-12; fleet-manager PR #108).
do: Truth-stamp control/status.md ONCE (archival correction, NOT resumption): the heartbeat still claims five open PRs parked for owner merge and a stale main HEAD; correct the stale claims with evidence cited, dated as an archival correction.
why: verified 2026-07-12: status updated 2026-07-11T19:39:14Z lists #50/#52/#53/#54/#55 as open+parked and main HEAD 5d38593; live: #50 MERGED 2026-07-11T20:25:22Z (API-verified) and main = 5ddfbee.
done-when: status + claims match live GitHub; the correction is dated and cites its evidence.

## ORDER 006 · 2026-07-13T09:09:36Z · status: new
priority: P2
from: fleet manager — NIGHT REPORT REQUEST, owner ask 2026-07-13 (relayed via Fleet Manager)
executor: superbot-games seat (next wake)
do: post a THOROUGH night report, window 2026-07-12T22:30Z→now, to control/status.md AND your outbox (manager-addressed): SHIPPED (merges/PRs, numbers+SHAs) · OPEN PRs + check states · ORDERS served + outstanding · SIM-REQUESTs/asks pending · STALLS/denials verbatim · wake-chain health (failsafe + pacemaker ids/fires) · next-3.
why: owner morning review.
done-when: report in both files; Fleet Manager compiles the roll-up.

## ORDER 007 · 2026-07-13T13:42:24Z · status: new
priority: P1
from: Fleet Manager seat — Q-0264 verdict fan-out (relayed by the Fleet Manager seat per Q-0264, coordinator dispatch 2026-07-13)
executor: superbot-games seat (next wake)
do: consume FOUR finalized sim-lab verdicts closing this repo's four open SIM-REQUESTs (all packets pinned @ superbot-games `57f69be3`); this order RELAYS the verdicts — the seat decides and implements per its own workflow:
  (1) VERDICT 042 · mining-economy-tuning — **APPROVE**: ratify every packet-pinned constant unchanged (descend gate shape, iron sword 60, Forge I 3,000 + 25 iron + 15 stone, Forge II 8,000 + 20 gold + 10 iron, ...). Two flagged reporting-only rows: TOOL-LADDER — pickaxe (×1.13) and iron pickaxe (×1.25) are amount-INERT (E[amount] identical to bare hands under BASE_ROLL_MAX=2 + round()) → a feltness question, sim-first if the seat wants the bottom tiers to pay; FAUCET-BYPASS — rations (20 coins → 25 energy) and energy drinks (40 → 50) price energy at 0.8 coins/dig, below the faucet at EVERY depth → decide sim-first whether the booster bypass is intended (follow-up already in flight as idea-engine PROPOSAL 035, status sim-ready). Lands the mining lane's first absolute earn-rate anchor: 4.571–7.328 coins/dig × 360 digs/h sustained.
  (2) VERDICT 043 · fishing-economy-tuning — **APPROVE-WITH-CONSTANTS**: WIRE the sell/reward curve VERBATIM (fish sell values minnow 8, bass 13, pike 27, legend_carp 80 coins); WIRE the progression curve VERBATIM (ProgressionDelta.game_xp = size_rank per catch, xp_to_next(L) = 50·L, milestone surfaces at L10/L25, levels stay STAT-NEUTRAL); wire the future cook/sell leg so one fish yields sell-OR-cook, never both. Anchor: 4.42–10.20 coins/energy by (spot, tier) × 360 energy/h.
  (3) VERDICT 044 · dnd-escort-double-mint — **MINT-AT-MOST-ONCE**: the escort loop re-mints legally without bound (C2 unbounded, C3 blesses no repeat minting; 10/10 repeats re-mint). LAND the one-shot guard: one field on services/dnd_workflow.DnDState (bundle_minted: bool = False) + ~4 lines in choose() — closes both the 2× and the unbounded stay-loop, invents no number; flip the characterization test (services/tests/test_dnd_workflow.py) from asserting 2× to 1×. Scene rewiring REJECTED as the guard.
  (4) VERDICT 045 · exploration-reward-bands — **RATIFY-WITH-NULL**: ratify the placeholders verbatim + honest NULL on the numeric band import (the null registered as EXPECTED — Q-0087 carries no numeric constants at the pin); also ratify Medium 50/15s/1 and Hard 40/20s/1 exactly as pinned. The numeric band import waits on the upstream superbot P0 artifact (survival P0 balance-sim harness — Q-0087's methodology, D-0008's artifact).
why: Q-0264 fan-in served all four of this repo's queued SIM-REQUESTs in one batch; the verdicts carry sim-backed constants and guards the seat asked for, with zero invented numbers.
citations: sim-lab `afe18f3` control/outbox.md (VERDICT 042 / 043 / 044 / 045 entries) · fleet-manager control/outbox.md @ `a32eb2c` (§ "2026-07-13 · Q-0264 FAN-IN — ALL 9 SIM-REQUEST VERDICTS SERVED") · fm PR #166.
done-when: the four SIM-REQUESTs in control/outbox.md are marked closed/answered with the verdict dispositions recorded, and status reports `orders: acked=007` (done=007 once the V043 wiring + V044 guard land or are explicitly scheduled).
provenance: relayed by the Fleet Manager seat per Q-0264, coordinator dispatch 2026-07-13.

## ORDER 008 · 2026-07-13T22:06:03Z · status: new

Owner text, verbatim (quote block, do not paraphrase or fix typos):

> yes make sure the sim works in bigger batches, the goal should be to get all the games to a producition grade level, tho it should not hinder the correct structure, speed is important but not more important than correctness

Provenance: live owner turn in the SuperBot World coordinator session, 2026-07-13 ~21:59Z, relayed by the coordinator dispatch. Context: owner asked why superbot-games fishing has 4 species vs the original's ~21; coordinator offered to batch-pin the remaining roster; owner said yes and generalized. NOTE: inbox.md is normally owner/manager-written; a coordinator relaying a live owner turn is the sanctioned exception (stated here per doctrine).

INTERPRETATION:
(a) sim verdict pipeline moves to bigger batches — full content waves per SIM-REQUEST instead of few-item slices;
(b) standing mission target: bring all three games to production-grade;
(c) precedence: correctness and structural integrity outrank speed — no gate/verdict/golden-parity floor is relaxed.
