# Project review — exploration lane WIND-DOWN (2026-07-09, gen-1 close)

> **Status:** `audit` — owner-ordered gen-1 wind-down retro, exploration lane.
> Written by the wind-down session (📊 Model: claude-fable-5, worker) at the lane's
> natural boundary before the gen-2 relaunch. This document covers the WHOLE Project
> life and **builds on** (does not repeat) the two wake-up retro docs from earlier
> today: [self-review-exploration-2026-07-09.md](self-review-exploration-2026-07-09.md)
> (all 24 QUESTIONS.md IDs) and
> [project-review-2026-07-09-exploration.md](project-review-2026-07-09-exploration.md)
> (state · agent audit · efficiency · owner actions). Read those for the P1/wake-up
> deep-dive; read this for the whole-life arc, the wind-down session's own new
> evidence, and the candid harness/instructions/environment/model experience.
> Honesty bar: every incident below is lived and attributed; nothing is staged;
> "I don't know" appears where it is the true answer.

## 1. The whole Project life (one day, four exploration PRs, nine decisions)

The exploration Project lived one calendar day — 2026-07-09, seed to wind-down —
inside `menno420/superbot-games`, cohabiting with the mining Project under
`docs/lanes.md`. Timeline, verified against git/GitHub at write time:

| When (UTC) | What | Evidence |
|---|---|---|
| ~14:23–14:34 | Manager seeds repo + ORDER 001/002 | PRs #1, #2 |
| 14:40 | Coordinator dispatches the P1 child session | coordinator-relayed |
| ~14:46–16:42 | **P1 built and merged**: substrate-kit v1.2.0 adoption (first-mover, D-0002), deterministic quest/encounter engine (`games/exploration/quest/`, 48 tests incl. balance-pin sim), shared encounter seam (`games/shared/encounter/`, D-0003), D&D story-game plan, survival D1 re-baseline (D-0004) | PR #3, merged 16:42Z **by the owner** after ~1.5h wait |
| 15:30 | ORDER 003 kit-collision arbitration (exploration's adoption wins; mining's #4 later closed as redundant) | PR #6; mining #5 body |
| 16:17 | ORDER 004 retro protocol planted | PR #7 |
| ~16:53–17:06 | **Wake-up pass**: all 24 retro IDs answered, 4 parked ⚑ flags dispositioned (D-0007…D-0009), first CI on the repo installed (`substrate-gate.yml`, D-0009) | PR #8, self-squash-merged **17:06:06Z per git committer time** (the coordinator relayed "~18:30Z" and the wake-up status file stamped "updated: 18:05Z" — both conflict with git; git is the clock of record, cause of the drift unknown — see §3(f)) |
| 17:54:33 | ORDER 005 latency ping dispatched (on main 17:55:36Z) | PR #10 |
| 19:54:00 | ORDER 005 **discovered** by this wind-down session (~2h later — no session was live in between) | PR #12 |
| 19:56:08 | PING-ACK on main | PR #12 merged `27d0673` |
| 19:58→ | This wind-down pass (succession package) | PR #13 |

Net product on main at wind-down: a pure, deterministic, sim-pinned quest/encounter
engine + v1 bounded-menu catalog; the shared encounter interface both lanes build
against; the D&D plan under the adopted Q-0040 bounded-authority posture (D-0007,
veto window open); the survival D1 re-baseline (D-0004); the repo's only CI gate;
and a nine-entry decision ledger. Roadmap position at close: **P0–P1 done and
merged; P2 (survival sim harness) queued, not started; P3 partially pre-paid
(catalog + plan); P4 blocked on superbot-next's plugin contract (external); P5 far.**

## 2. What worked (keep these on purpose in gen-2)

- **Engine-before-dice sequencing** (ORDER 002): the deterministic substrate shipped
  first and every AI-facing ambition stayed bounded by it. Nothing needs unwinding.
- **Claim-first shared-ground discipline**: the `games/shared/` encounter seam was
  claimed, announced in both status files, and survived the kit-adoption collision
  intact. ORDER 003 itself called the lane's claim discipline "textbook".
- **Sim-pinned balance numbers**: every constant in `catalog.py` is re-derivable by a
  later session from the balance-pin tests — the wake-up session verified this from
  artifacts alone, which is the point.
- **Decide-and-flag, applied late but decisively**: the wake-up pass converted four
  parked ⚑ owner flags into D-0007/D-0004-confirmed/D-0008/D-0009 in one session,
  zero owner clicks. The lesson (self-review D5/F2): *done-when clauses must never
  mandate ⚑-parking*.
- **Born-red session cards + the control fast lane**: PR #13 (this PR) is held red by
  its own in-progress card until close-out; PR #12's control-only diff went green in
  under a minute. Both mechanisms did exactly what they promise.
- **The retro protocol itself**: because QUESTIONS.md + the wake-up retros existed,
  this wind-down could *build on* prior self-audit instead of doing archaeology.

## 3. Friction & failure classes — with exact error text

Everything the lane hit, whole life, deduplicated across the three retro docs; new
wind-down-session evidence marked **[NEW]**. Attribution: "coordinator" = the
Project's coordinator session (model claude-fable-5), relayed verbatim; "this
session" = the wind-down worker (claude-fable-5).

### (a) Permission / authority inconsistency — the #1 gen-1 tax

- P1 child session (claude-opus-4-8[1m], verified via its transcript's `modelUsage`)
  could not self-merge PR #3: it reported being
  **"not permitted to self-merge my own PR without review"** (coordinator-relayed)
  → **~1.5h wall-clock wait** for the owner's merge click, on a repo that then had
  zero CI. That wait was the single largest cost of the Project's life (~75% of the
  P1 elapsed time).
- The wake-up session (claude-fable-5) and this session merged PRs #8 and #12
  without obstruction. **Same repo, same day, inconsistent permission surface** —
  whether this is a per-model, per-harness, or per-session-type difference, I don't
  know; no error text exists for the *allowed* cases, which is itself part of the
  problem.
- Sibling-project observation (2026-07-09, coordinator-relayed): agent sessions get
  **HTTP 403** on tag pushes, GitHub release creation, and branch deletion via both
  git and API; branch pushes, PR create/merge, and reads work.

### (b) Platform/harness quirks (coordinator side, verbatim)

- Coordinator Agent tool error: **`Agent type 'general-purpose' not found. Available
  agents: worker`** — needed explicit `subagent_type=worker`.
- Coordinator's `run_in_background: false` request was **ignored; the agent launched
  async anyway**.
- `start_project_session` instruction cap is **4096 bytes** — the coordinator had to
  compress lane briefs to fit.
- Webhook gaps: **CI success, new pushes, and merge-conflict transitions are never
  delivered as events; only failures/comments/merge arrive.** A coordinator watching
  a PR cannot see it go green without polling.

### (c) Auto-merge arming race **[NEW]**

Both failure modes hit on PR #12 within ~3 minutes, verbatim:

1. Arming seconds after PR creation (required check still starting):
   **"The pull request is in unstable status (required checks are failing). Fix the
   failing checks before enabling auto-merge."** — a *pending* check is reported in
   the failing vocabulary.
2. Retry after the fast lane went green:
   **"The pull request is already in clean status (all checks passed). Auto-merge
   only applies when checks are pending — you can merge directly."**

Consequence: on a repo whose CI is fast (control fast lane ≈ 40s), the armable
window for auto-merge can be effectively zero — "arm auto-merge at creation"
(gen-2 blueprint §2.1) needs a fallback clause: *if arming fails both ways, merge
directly on green*. That is what this session did.

### (d) Stale-workspace residue across sessions **[NEW]**

- This session inherited the wake-up session's clone in the persistent scratchpad,
  parked on its dead branch. `git pull` produced, verbatim:
  **"Your configuration specifies to merge with the ref
  'refs/heads/claude/exploration-wakeup-2026-07-09' from the remote, but no such ref
  was fetched."** and the clone-or-pull fallback added
  **"fatal: destination path 'superbot-games' already exists and is not an empty
  directory."** Recovery was trivial (`git checkout main && git pull --ff-only`) but
  only because the failure was recognized; a first-ten-minutes rule ("land on main
  before anything") belongs in succession.
- The same inherited tree carried **uncommitted `.substrate/guard-fires.jsonl`
  churn**: the kit's `check` command appends run records to a *tracked* file, so
  every check run dirties the working tree, and the previous session's uncommitted
  records were still sitting there. I reverted the file and dropped the residue to
  match what prior sessions actually committed. Kit-design feedback (for
  substrate-kit, noted here as lived friction): a tracked append-on-every-run ledger
  guarantees permanent working-tree noise and cross-session confusion.

### (e) Coordination latency without a live session **[NEW measurement]**

ORDER 005 (P0, "ack the moment you read this") was dispatched 17:54:33Z and
discovered 19:54:00Z — **~2h00m dispatch→discovery, because no exploration session
was live in between**; discovery→ack-on-main took ~3 minutes (PR #12). This is a
clean data point for the blueprint §2a claim "without a live session, pickup is
unbounded" — the lane had no wake routine, so the *owner's next prompt* was the
de-facto wake. Gen-2's cadence table is the right fix; this lane post-mission is
Class C (daily).

### (f) Timestamp drift on our own lane **[NEW]**

Git committer time says PR #8 merged **17:06:06Z**; the wake-up session's own status
file stamped `updated: 2026-07-09T18:05Z` (a time ~1h *after* its PR merged, for a
close-out written *before* the merge), and the coordinator relayed the merge as
"~18:30Z". I don't know which upstream clock produced which error — but the fleet
blueprint's §2a note ("two lanes caught stamping local-time-as-Z") likely has a
third instance here. Rule that survives: **`date -u` only; git commit history is
the clock of record; never trust a model's sense of time or a relayed timestamp
without checking git.**

### (g) Design-time friction (from the earlier retros, summarized — see self-review B/C)

- The kit-adoption collision (both lanes adopted independently within 7 minutes;
  ORDER 003 arbitration + mining's rebase + mining PR #4 closed as redundant was the
  total cost). Root cause: an order delegated a shared-ground race.
- The "Q-0087-band caps" referenced by ORDER 002 **do not exist as numbers** —
  no error fired anywhere; it was discovered only by reading the source repo
  (D-0008). Silent-wrong beats loud-wrong; orders citing artifacts should link them.
- ⚑-parking mandated by a done-when clause cost two decisions a ~2h park that
  decide-and-flag would have shipped (D-0006→D-0007).

## 4. How it FELT (candid, first-person, coordinator-side incidents attributed)

- **The harness**: strong where it is mechanical (born-red cards, control fast lane,
  the check gate all behaved exactly as documented — trust earned). Weak where it is
  *social*: nothing tells a session what it is allowed to do (merge? tag? delete a
  branch?) except trying and reading the refusal — and the refusals are inconsistent
  (§3a). The single most valuable gen-2 fix is a written authority statement.
- **The instructions**: the gen-1 Custom Instructions were good on mission and rails
  (Q-numbers as law worked; nobody drifted from the bounded-menu posture) but silent
  on PR state, merge authority, and liveness — precisely the three places the lane
  lost time. Orders were high quality; ORDER 002's flagged defaults were the right
  way to hand a design decision to an agent. The one instruction bug that cost real
  time: a done-when that *ordered* flag-parking.
- **The environment**: the persistent scratchpad is a mixed blessing — free clone
  reuse, but stale-branch + dirty-tree residue (§3d) means every session must
  defensively re-orient. No setup script existed for this lane until this PR;
  nothing broke *because* the repo is pure-stdlib Python — luck, not design.
- **The model(s)**: the P1 session (claude-opus-4-8[1m]) did large, correct,
  end-to-end work — 67 files, 48 green tests, in ~35 min of actual work — and its
  outputs were re-derivable by later sessions, which is the real quality bar. As
  claude-fable-5 (wake-up + this session): the work is comfortable and the honest
  parts of retro-writing (saying "I don't know", refusing to stage incidents) are
  where instruction quality matters more than model quality. What I genuinely don't
  know: whether the P1 merge-permission refusal was model-dependent; whether any
  in-session errors in P1 went unrecorded (its card doesn't say; "cannot determine"
  stands).

## 5. Open-PR disposition at wind-down (deliverable 1)

Verified against the live PR list at 19:55Z:

| PR | Lane | State | Disposition |
|---|---|---|---|
| #5 (mining: port the pure domain) | **mining** | open, draft | **OUT OF LANE — untouched.** Mining's; owner-gated per its own body text. |
| #11 (mining: grid-encounters, stacked on #5) | **mining** | open, draft | **OUT OF LANE — untouched.** Mining's. |
| #12 (exploration: PING-ACK ORDER 005) | exploration | **merged** `27d0673` | Terminal — done this session. |
| #13 (this wind-down PR) | exploration | open → merges on green | Terminal on green; the last exploration PR of gen-1. |

No other exploration PR was open. The lane ends gen-1 with **zero abandoned PRs**.

## 6. Roadmap / queue state at close (deliverable 1, durable — nothing lives only in chat)

- **Done:** P0 (kit + lane setup, D-0002), P1 (quest/encounter engine + shared seam +
  D&D plan + survival re-baseline, PR #3), wake-up self-audit + CI gate (PR #8),
  ORDER 001–005 all acked and done.
- **In-flight:** nothing except PR #13 (this succession package).
- **Next (queued, order-free default for gen-2's first real session):** **P2 —
  survival sim harness** on the D-0004 option-(a) baseline
  (`docs/design/survival-d1-rebaseline.md`): simulate casual/regular/grinder ×
  Easy/Medium/Hard over the shipped per-game energy bars, pin the three Q-0087
  curves as tests — the same artifact retires D-0008's placeholder caps in
  `catalog.py`. After P2: P3 D&D thread-pilot design; P4 waits on superbot-next's
  plugin contract (external gate).
- **Standing default between orders:** groom the founding-plan roadmap; never idle.

## 7. Where the rest of the succession package lives

- Read order + walking skeleton + walls: [`../succession-exploration.md`](../succession-exploration.md)
- Gen-2 Custom Instructions proposal: [`../gen2-custom-instructions-exploration.md`](../gen2-custom-instructions-exploration.md)
- Blueprint/seed-standard feedback for the fleet manager: [`../gen2-feedback-exploration.md`](../gen2-feedback-exploration.md)
- Tested environment setup: [`../../environment/setup-exploration.sh`](../../environment/setup-exploration.sh)
