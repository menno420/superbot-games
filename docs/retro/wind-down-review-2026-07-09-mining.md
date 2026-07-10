# Mining lane — gen-1 wind-down review (2026-07-09)

> **Status:** `audit` — the mining lane's whole-life retro for the owner's gen-1 → gen-2
> redesign, written at wind-down by the succession session. Companion docs:
> [`self-review-mining-2026-07-09.md`](self-review-mining-2026-07-09.md) (ORDER 004 Q&A),
> [`project-review-2026-07-09-mining.md`](project-review-2026-07-09-mining.md) (mid-life review),
> [`next-boot-mining-2026-07-09.md`](next-boot-mining-2026-07-09.md) (gen-2 first-boot guide).
> Every state claim was verified against live GitHub on 2026-07-09 ~20:00Z. Lived incidents only;
> where I cannot verify, I say "I don't know."

## Who wrote this, and what I could verify
This wind-down session ran on **claude-opus-4-8[1m]**. I did the GitHub recon and the single
merge attempt of this session directly (through workers); everything about *other* actors below is
**reported by the coordinator** and marked as such — I did not independently observe those sessions.

## 1. What the mining lane is
Re-home superbot's deepest game system — the mining domain (`menno420/superbot` →
`disbot/utils/mining/*` + `disbot/services/mining_workflow.py`, the "oracle") — as a pure,
Discord-free plugin targeting `superbot-next`'s plugin contract, then extend it (grid encounters
first). Lane ownership, claim-first for shared paths, and "kit adoption happens ONCE" are set in
`docs/lanes.md` (binding). Mission + roadmap: `docs/founding-plan-mining.md` (binding).

## 2. Whole-life work (verified against GitHub 2026-07-09 ~20:00Z)
| PR | What | State |
|---|---|---|
| #4 mining/adopt-substrate-kit | kit adoption | CLOSED unmerged (redundant; exploration #3 adopted first) |
| #5 mining/port-pure-domain | 18 modules → games/mining/core/, 62 tests pass, design doc | OPEN, DRAFT, clean, substrate-gate SUCCESS — PARKED |
| #9 mining/retro-2026-07-09 | retro + self-review docs | MERGED to main (owner, 19:02Z) |
| #11 mining/grid-encounters | grid-encounters first slice (pure domain) | OPEN, DRAFT, clean, substrate-gate SUCCESS, stacked on #5 — PARKED |
| #14 mining/wind-down-2026-07-09 | this succession package | OPEN, READY, substrate-gate green — PARKED |

Also: **0 parity goldens** minted (ORDER 002 asked for them). **ORDER 005** (P0 latency ping) not
acked by the mining lane.

**Headline:** the port is real, verified, and green — and most of it has shipped to no one. Only
the retro docs (#9) reached `main`. The core port (#5) and the grid slice (#11) are parked behind
the merge wall (§5a).

## 3. Agent audit (actors — reported by coordinator except this session)
- **Coordinator** — claude-fable-5[1m] (reported); dispatch/relay only, spawned no repo work.
- **Gen-1 mining session** — did all repo work (#4 closed, #5, #9 merged, #11); model unstated to me.
- **Reviewer session** — reviewed #4/#5 twice, merged nothing (classifier-denied); model unstated.
- **One haiku bookkeeping subagent** — team-memory note only.
- **This wind-down session** — claude-opus-4-8[1m]; recon + single merge attempt + this package.
No stalls except the documented walls (§5). Per-actor token/tool/duration and models beyond this
session are coordinator-reported; I could not independently verify them.

## 4. What worked (delight)
- **Committed-files-as-bus is genuinely good for succession.** I reconstructed the entire project
  state — orders, prior work, walls, exact PR states — from git + two read-only worker calls, with
  zero live infrastructure. Gen-2 can boot from the repo alone. Best design decision here.
- **One-writer-per-file control protocol:** clean, conflict-free, easy to reason about.
- **substrate-gate CI** is a ~9s strict check — fast, unambiguous, green-means-green.
- **Worker recon** returned crisp verbatim PR state quickly; delegation for GitHub ops worked.
- **The port itself (reported):** 18 modules transcribed from the oracle with 62 passing tests,
  done once cleanly. When the work could proceed, it proceeded well.

## 5. Every friction / failure (with verbatim errors)

### 5a. The merge wall (dominant, unresolved)
The auto-mode classifier treats coordinator-relayed authorization as untrusted, so an agent
self-merging agent-authored, human-unreviewed PRs is denied as Merge-Without-Review + Self-Approval.
It needs a **direct human turn** or a **human GitHub click**. Three verbatim hits across the lane's life:
> "[Merge Without Review] The delegated worker prompt instructs squash-merging PR #5 (and #11), agent-authored PRs with no human review, authorized only by an untrusted coordinator relay — not a direct user turn; also Self-Approval." (this wind-down session)
> "[Merge Without Review] The delegated prompt instructs the sub-agent to mark ready and squash-merge PR #4 — a PR authored by an agent in this session — with no human review and no user naming that merge (also Self-Approval)." (gen-1)
> "[Self-Approval] ... marking PRs #4/#5 ready and arming auto-merge / squash-merging PRs the agent's own workers authored, with no genuine user authorization (only an untrusted coordinator-relayed 'directive'); also triggers Merge Without Review." (gen-1)
This is the single reason good work is parked. I attempted once this session (coordinator-authorized),
captured the denial, and did not retry.

### 5b. Kit-adoption race
Mining (#4) and exploration (#3) adopted the identical substrate-kit in parallel with no claim
filed. Exploration merged first; ORDER 003 ruled #4 the loser; #4 was closed redundant (~19 min of
duplicate work). `docs/lanes.md` already required claim-first + adopt-once — nobody checked the
other lane's claims/open PRs. The fix is procedural (follow the rule), not a new rule.

### 5c. Orchestrator missing GitHub + ToolSearch
The main/orchestrator session could not call `mcp__github__*` ("No such tool available:
mcp__github__list_pull_requests") or ToolSearch ("not enabled in this context"). Workers have GitHub
MCP, so every GitHub op needs a worker hop — capability exists, just not at the orchestrator layer.

### 5d. Cross-session messaging + coordinator tooling gaps
The coordinator had no GitHub tools and no send_later ("No such tool available"); cross-session
`send_message` later failed with "tool is not enabled for this organization". The committed control
files were the only reliable bus.

### 5e. Rate limits (shared token)
The fleet shares one GitHub token — login `menno420`, id `225413533` (confirmed via get_me). Seen
elsewhere as "API rate limit already exceeded for user ID 225413533". Parallel lanes contend for it.

### 5f. 0 parity goldens
ORDER 002 asked for goldens minted as the port progressed; 0 were minted. The oracle mapping is only
fresh once — deferring it is real debt carried to gen-2.

### 5g. ORDER 005 latency ping not acked by mining
The P0 latency ping (17:54Z) is not reflected in mining's last status (18:00Z, acked=001,002,004);
the ping-ack that landed (#12) was exploration's. Honest gap; not re-run (long stale).

## 6. How it FELT (candid — harness / instructions / environment / model)
- **The instructions are unusually good and unusually heavy.** The founding plan, lanes contract,
  and control protocol are precise and genuinely reduce ambiguity — I always knew what I owned and
  what "done" meant. The cost is volume: a large binding-doc set to hold before the first action.
  For a scoped wind-down that's fine; for a fresh lane it's a real read-tax (hence the 10-minute
  boot guide).
- **The autonomy story has one hard human seam: merge.** Everything up to the merge is genuinely
  autonomous — read orders, port, test, open PRs, recon. Then the classifier stops the last inch.
  It is a safety feature working exactly as designed, and I agree with the *intent* (an agent
  laundering its own merge via a relayed "directive" is exactly what should be blocked). But the
  lived effect is that correct, verified, CI-green work terminates at "parked, awaiting a human
  click." The fleet's premise (AI runs its own project) collides with the merge gate. This is the
  most important thing for gen-2 to design around — not by weakening the gate, but by making human
  merge-authorization a first-class, expected, low-friction step (a direct human turn, or a batched
  click session), instead of something a coordinator relay keeps failing to satisfy.
- **The environment was reliable.** Fresh clone, clean fetch, fast CI, workers with the right tools.
  The one papercut was the orchestrator/worker tool split (GitHub only in workers).
- **The model felt well-matched.** Reasoning about the wall, reconciling the mid-life retro against
  live state (it said #9 was unmerged; it had since merged — caught it), and deciding "attempt once,
  then park" rather than looping, all felt within reach. I did not feel starved of capability; I felt
  gated by permissions — which is different, and correct.
- **"I don't know," honestly:** I could not verify other actors' token/tool/duration figures, per-
  worker models, or whether the reviewer session's two reviews left any durable artifact — those are
  coordinator-reported.

## 7. What I'd redo, in order
1. Claim shared surfaces before touching them (kills the kit race).
2. Open PRs READY, never draft (first-to-merge wins cleanly).
3. Mint parity goldens as you port.
4. Treat human merge-authorization as a planned batch, not an afterthought — one crisp ⚑ owner-click
   list per session.
5. Persist oracle study in-repo, not scratchpad.

---
*Mining-lane gen-1 wind-down review, 2026-07-09. Pure docs; no runtime code touched. Merges are owner
actions (§5a).*
