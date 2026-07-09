# Project review — game-exploration lane (2026-07-09, wake-up pass)

> **Status:** `retro-report` — owner-ordered full self-review + wake-up pass, exploration lane.
> Written by the wake-up session; every state claim below verified against the repo/GitHub
> at write time, not from memory. Companion answers file:
> [self-review-exploration-2026-07-09.md](self-review-exploration-2026-07-09.md).

## (a) What this Project is + TRUE current state

**What it is.** The game-exploration Project: one of two autonomous Projects cohabiting
`menno420/superbot-games` (contract: `docs/lanes.md`). Its mission
(`docs/founding-plan-exploration.md`): the federated-world exploration domain for
superbot — a deterministic quest/encounter engine, the survival overlay, and the D&D
story game under the Q-0040 bounded-menu posture — built as pure plugin code for
superbot-next's future host contract. The sibling mining Project ports the mining domain;
lanes never cross.

**True current state, verified against the repo (main @ `7099fda`) and the GitHub PR
list at 2026-07-09:**

- **Merged to main:** PRs #1, #2, #6, #7 (manager: seed, buildability maps, ORDER 003,
  retro protocol) and **#3** (exploration P1 — merged 2026-07-09T16:42Z: substrate-kit
  v1.2.0 adoption, quest/encounter engine `games/exploration/quest/` with 48 tests incl.
  the balance-pin sim, shared encounter seam `games/shared/encounter/`, D&D plan, survival
  D1 re-baseline, D-0002…D-0006).
- **Open:** mining's draft PRs **#4** (kit adoption — loses per ORDER 003 arbitration,
  rebase pending) and **#5** (pure mining domain port, stacked on #4). Mining-lane
  property; untouched by this pass. This pass's own PR **#8** (this branch).
- **Roadmap position:** exploration P0–P1 **done and merged**; P2 (survival sim harness)
  not started; P3 design partially pre-paid (the D&D plan + catalog exist); P4 blocked on
  superbot-next's plugin contract (external).
- **Enforcement:** until this PR, main had NO CI at all and `bootstrap.py check --strict`
  showed 3 findings (lanes.md badge, D-0043 double-stamp, enforcement-unwired). This PR
  fixes all three and installs the staged `substrate-gate.yml` — first CI on the repo.
- **Flags:** the four parked ⚑ needs-owner items are now dispositioned (section (e));
  decision ledger extended with D-0007…D-0009.

## (b) Agent audit — every session/agent that worked this Project

Enumeration limits, stated honestly: the `webagent list_project_sessions` tool is **not
available in this session** (verified via tool search), so the fleet-level list below
merges (1) coordinator-relayed facts — attributed, verbatim where quoted — with (2) what
this session verified directly (repo artifacts; `claude-code-remote list_events` on the
child session's transcript).

| # | Agent/session | Model | Tasked with | Delivered | Stalls/notes |
|---|---|---|---|---|---|
| 1 | Coordinator session (project front door) | `claude-fable-5[1m]`, fallback `claude-opus-4-8[1m]` (coordinator-stated) | Routing/aggregation | Dispatched the exploration session (2026-07-09 14:40Z); independently verified PR #3 state; relayed flags to owner | None blocking. Two platform quirks (coordinator verbatim, class (b) platform): (1) "its Agent tool rejected the default agent type (\"Agent type 'general-purpose' not found\"), needed explicit subagent_type=worker"; (2) "a run_in_background:false request still launched async" |
| 2 | Exploration child session `cse_01Fsfc2hZ6gjmRmq6ojBSeq4` | **`claude-opus-4-8[1m]`** — verified from inside: its transcript's final result event (`list_events`) reports `modelUsage: claude-opus-4-8[1m]`; its own session card says "Claude Opus". (The coordinator could not determine this; the transcript could.) | ORDER 001/002 (kit adoption, engine-before-dice, D&D plan, survival re-baseline) | PR #3 (67 files), merged | Could NOT self-merge its own PR ("not permitted to self-merge without review" — coordinator-relayed) → waited ~1.5h on the owner's merge click. Classified **(a)/(b)**: a session-permission/repo rule, not the work |
| 3 | Background verification subagent (coordinator-spawned, ~30s, read-only) | `claude-fable-5` (inherited coordinator model per platform default — coordinator-stated) | Verify PR #3 open/ready/clean at `2274f20` | Verification report | No stalls |
| 4 | This wake-up session (worker) | **`claude-fable-5`** — per this session's own environment/system info | Owner's self-review + wake-up pass (this document, ORDER 004, flag disposition, PR #8) | See PR #8 | See (d); merge attempt result recorded in the PR/status |

Also touching the repo but **not** this Project's agents: the manager-fleet session
(`session_019PgczP9p17N6SCB5bwS5fE` per PR bodies of #1/#2/#6/#7) and the mining lane
session(s) (`session_01GGLZMqeTgWmkiuH66DuofS` per PR #4; PRs #4/#5). Listed for
completeness; auditing them belongs to their own lanes.

**Known platform limits** (observed on sibling projects 2026-07-09, relayed by the
coordinator): agent sessions get 403 on tag pushes, GitHub release creation, and branch
deletion via both git and API; branch pushes, PR create/merge, and reads work.

## (c) Retro questions

All 24 IDs (A1–A4, B1–B4, C1–C4, D1–D5, E1–E4, F1–F4, G1–G3) answered in
[docs/retro/self-review-exploration-2026-07-09.md](self-review-exploration-2026-07-09.md)
(ORDER 004). Honesty note: the P1 session's inner experience is reconstructed from
artifacts by the wake-up session; "cannot determine" is used where reconstruction fails
(e.g. unrecorded in-session errors, exact time splits).

## (d) Honest efficiency verdict

**Where the time went.** The lane's elapsed wall time from dispatch (14:40Z) to P1 merged
(16:42Z) was ~2h, of which **~1.5h was waiting for a human merge click** on a repo with
zero CI — the single biggest inefficiency, and entirely a permissions/rule artifact, not
work. The work itself (engine + kit + docs, 67 files, 48 tests) fit in roughly the first
~35 minutes plus close-out — genuinely fast. The wake-up pass (this session) spent
~40% re-verifying state from sources — necessary once (it caught the phantom flag,
D-0008), and now durable so the next session shouldn't pay it again.

**What I'd redo, in order** (full reasoning: self-review C4/F2):
1. **Split PR #3**: land kit adoption + status as a tiny PR in the first 20 minutes, then
   the engine as a second PR. Kills the kit-adoption collision window (mining adopted the
   same kit 7 minutes later; ORDER 003 arbitration + mining's rebase were the cost) and
   un-bundles a 67-file all-or-nothing merge.
2. **Read Q-0087 at its source before designing caps** — the "Q-0087-band caps" the
   orders referenced don't exist as numbers (verified this pass; D-0008); an early source
   check would have saved the hunt and one mis-aimed owner flag.
3. **Adopt recommendations instead of parking them** — two of the four ⚑ flags carried
   their own APPROVE recommendation; decide-and-flag would have shipped them same-session
   (done now as D-0007, D-0004-confirmed).
   Estimated redo speedup: ~25–30% of session time, and ~100% of the wait time under the
   self-merge rule now in force for this repo (no CI checks → merge your own READY PR).

## (e) ⚑ OWNER ACTIONS — genuinely owner-only items

After the self-unblock pass, **no owner action is required to unblock the exploration
lane.** All four previously-parked flags were dispositioned under decide-and-flag:
D-0007 (Q-0040 posture adopted — veto window open until the P3→P4 ship gate), D-0004
confirmed (survival D1 option (a)), D-0008 (Q-0087 caps wait on superbot's future sim
bands, not on you), D-0009 (CI gate installed; revert = veto). **Veto = react to what you
see; silence = consent.**

Remaining genuinely-owner-only items (none blocking):

1. **Optional housekeeping — delete merged branches** (agents get 403 on branch deletion,
   verified platform limit). Unblocks: nothing functional; repo hygiene only.
   Click-by-click: github.com/menno420/superbot-games → **Branches** (link under the
   branch dropdown on the Code tab) → in "Your branches"/"All branches", click the 🗑
   trash icon next to each of: `seed/main`, `manager/research-maps`,
   `manager/order-003-arbitration`, `claude/fleet-retro-2026-07-09`,
   `claude/exploration-p1-quest-engine`, and — after PR #8 merges —
   `claude/exploration-wakeup-2026-07-09`. Do NOT delete `mining/adopt-substrate-kit` or
   `mining/port-pure-domain` (live draft PRs #4/#5).
2. **Only if PR #8's self-merge failed** (the PR conversation + `control/status-exploration.md`
   will say so with the exact error text; if they don't, skip this): open
   github.com/menno420/superbot-games/pull/8 → scroll to the merge box → dropdown →
   **Squash and merge** → **Confirm squash and merge**. Unblocks: this entire review +
   retro + flag disposition landing on main.
3. **P5 live playtest, later** (not now): when P4 host integration exists, the live
   playtest by design needs you in Discord. Nothing to click today.

## (f) CONTINUATION — what the lane does next without the owner

Per the founding-plan roadmap, next is **P2 — the survival sim harness** (build before any
tuning ships), on the D-0004 option-(a) baseline in `docs/design/survival-d1-rebaseline.md`:
simulate casual/regular/grinder profiles across Easy/Medium/Hard over the shipped
per-game energy bars, output the three Q-0087 curves (casual progress/day, grinder
surplus/hour, capability-gap), and pin them as tests — which is *also* the artifact that
retires the D-0008 placeholder caps (the harness produces the very bands `catalog.py`
awaits). Alongside it, small P3 pre-work is already banked (catalog + D&D plan). Status:
**queued** — recorded as the lane's next order-free default in
`control/status-exploration.md` (notes section) by this pass; not started this session.
The lane's between-orders default (self-review F4): groom the founding-plan roadmap, never
idle.
