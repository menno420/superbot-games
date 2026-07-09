# Succession — exploration lane, gen-1 → gen-2

> **Status:** `owner-guidance` — written 2026-07-09 by the gen-1 wind-down session
> (📊 claude-fable-5) for the FIRST gen-2 exploration session. Chat context does not
> survive the transition; this file is what does. Companion whole-life retro:
> [retro/project-review-wind-down-2026-07-09-exploration.md](retro/project-review-wind-down-2026-07-09-exploration.md).

## 1. The first 10 minutes — read these, in this order

Before that: land on main (`git checkout main && git pull --ff-only`) — an inherited
clone may be parked on a dead branch with a dirty tree (documented wall §3 below).

1. **`control/inbox-exploration.md`** — your orders. NEVER edit any inbox; ack new
   orders in your status file before other work (ORDER 005 was a timed test of this).
2. **`docs/lanes.md`** — the binding cohabitation contract. You own
   `games/exploration/**` + your status file; `games/shared/**` is claim-first;
   never touch the mining lane.
3. **`control/status-exploration.md`** — the lane's last true state + queued next
   work. You overwrite it LAST every session (one writer per file).
4. **`docs/founding-plan-exploration.md`** — mission, binding rails (Q-numbers are
   law), and the P0–P5 roadmap you are somewhere inside.
5. **`docs/decisions.md`** — the D-ledger (D-0001…D-0009 at handoff). Append-only;
   D-0007 (bounded-authority posture) and D-0004 (survival D1 option (a)) shape all
   remaining work.
6. **`docs/research/buildability-map-exploration.md`** — reference, verify against
   sources; its "Q-0087 bands" pitfall is already triaged (D-0008).
7. **This file** — walls (§3) so you never probe a documented wall twice; then the
   wind-down retro linked above for the whole-life arc.
8. **`docs/current-state.md`** + **`.sessions/`** (newest first) — repo-wide ledger
   and per-session cards; card conventions in `.sessions/README.md` (born-red first
   commit, flip-to-complete last, Model line mandatory).

## 2. Walking-skeleton check — prove the merge path BEFORE real work

Prove branch → PR → CI → merge end-to-end with a ~zero-content change, in minutes:

1. Branch; add one heartbeat line to `control/status-exploration.md` (updated:
   timestamp) — a **control/-only diff rides substrate-gate's fast lane** (green in
   ~40s, no session card needed).
2. Open the PR **READY** (never draft).
3. Try `enable_pr_auto_merge`. Expect it to possibly fail BOTH ways on a fast repo
   (exact texts in §3) — if it can't arm, wait for green and **squash-merge yourself**
   (standing order: merge on green; this session's precedent: PRs #8, #12).
4. Verify the merge landed on main. Total cost ≈ 5 min; PR #12 is the worked example.

If any step fails in a new way: record the exact error text in your status file and
route it to the manager — that's new wall data, not your bug.

For a *real* (non-control) PR, additionally: session card in the first commit with
`> **Status:** `in-progress`` (holds the gate red on purpose), close-out markers +
flip to `complete` as the deliberate last push. Local CI mirror:
`python3 bootstrap.py check --strict --require-session-log --session-log .sessions/<card>`.

## 3. Known walls — exact error text (never probe a documented wall twice)

1. **Tag push / release creation / branch deletion → HTTP 403** (both git and API;
   sibling-project verified 2026-07-09). Branch pushes, PR create/merge, reads work.
   Branch deletion is an owner click; queue it, don't retry.
2. **Self-merge may be refused inconsistently.** The P1 child session
   (claude-opus-4-8[1m]) was told it was "not permitted to self-merge my own PR
   without review" → ~1.5h owner wait; the same day, two claude-fable-5 worker
   sessions merged their own PRs (#8, #12) freely. If refused: leave the PR READY +
   green, record the refusal text verbatim, flag the owner click — done-when for you
   is then "PR open, READY, green", not the merge.
3. **Inherited workspace residue.** A persistent scratchpad clone may sit on a dead
   branch: `git pull` → "Your configuration specifies to merge with the ref
   'refs/heads/<old-branch>' from the remote, but no such ref was fetched." and a
   blind re-clone → "fatal: destination path 'superbot-games' already exists and is
   not an empty directory." Fix: `git checkout main && git pull --ff-only`. Also
   expect uncommitted `.substrate/guard-fires.jsonl` churn — the kit's `check`
   appends run records to a tracked file; prior sessions did NOT commit these
   run-record appends (revert unless you have a reason).
4. **Auto-merge arming race** (GitHub MCP `enable_pr_auto_merge`): too early →
   "The pull request is in unstable status (required checks are failing). Fix the
   failing checks before enabling auto-merge." (pending reads as failing); too late →
   "The pull request is already in clean status (all checks passed). Auto-merge only
   applies when checks are pending — you can merge directly." On this repo's fast CI
   the armable window can be zero: fall back to direct squash-merge on green.
5. **Coordinator-side platform quirks** (verbatim, coordinator, claude-fable-5):
   Agent tool — "Agent type 'general-purpose' not found. Available agents: worker"
   (pass explicit `subagent_type=worker`); `run_in_background: false` may be ignored
   (agent launches async anyway); `start_project_session` instruction cap is 4096
   bytes; webhooks never deliver CI-success / new-push / merge-conflict events —
   only failures, comments, and merges arrive (poll for green, don't wait on events).
6. **Silent-wrong upstream references.** ORDER 002's "Q-0087-band caps" named
   constants that don't exist anywhere (no error fires — verified at source, D-0008).
   When an order cites an artifact, read it at its source before building against it.

## 4. State you inherit (queue)

Done: P0+P1 merged (#3), wake-up audit + first CI (#8), ORDERs 001–005 done.
**Next queued work: P2 survival sim harness** on the D-0004 option-(a) baseline —
full spec in `docs/design/survival-d1-rebaseline.md`; it also produces the pinned
bands that retire the D-0008 placeholder caps in `games/exploration/quest/catalog.py`.
Then P3 (D&D thread-pilot design); P4 gates on superbot-next's plugin contract.
Between orders: groom the roadmap, never idle. Environment setup:
`environment/setup-exploration.sh` (tested; always exits 0).
