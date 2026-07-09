# Project review — game-mining lane (2026-07-09)

> **Status:** `audit` — mining-lane wake-up + retro review for the owner's gen-2 redesign.
> Companion to the question-by-question answers in
> [`self-review-mining-2026-07-09.md`](self-review-mining-2026-07-09.md) (ORDER 004).
> Every state claim below was verified against the live repo / GitHub on 2026-07-09.

---

## A. What this Project is + current TRUE state

**The Project.** game-mining is one of two cohabiting game Projects in the shared repo
`menno420/superbot-games` (the other is game-exploration). Its job: re-home superbot's most
mature subsystem — the mining domain (`menno420/superbot` → `disbot/utils/mining/*` +
`disbot/services/mining_workflow.py`, the "oracle") — as a **pure, Discord-free plugin**
targeting `superbot-next`'s plugin contract. Lane ownership, the claim-first rule for shared
paths, and "kit adoption happens ONCE" are set in `docs/lanes.md` (binding). Founding brief:
`docs/founding-plan-mining.md`; research reference: `docs/research/buildability-map-mining.md`.

**Verified true state (2026-07-09):**

| Fact | Verified how | State |
|---|---|---|
| substrate-kit **v1.2.0** engaged on `main` | present on `main` after PR #3 merge | ✅ live |
| Mining **pure domain** ported — 18 modules in `games/mining/core/` | `ls` on `mining/port-pure-domain` | ✅ exists, **draft PR #5 only** |
| Mining **62 unit tests** pass | `python3 -m pytest tests/mining/` → 62 passed | ✅ green |
| Design doc `docs/design/mining-plugin-layout.md` | file present on #5 branch | ✅ exists |
| **PR #4** (kit adoption) | GitHub API | 🟥 **OPEN, DRAFT, `mergeable_state: dirty`** (conflicts main), CI `substrate-gate` green |
| **PR #5** (pure port, stacked on #4) | GitHub API | 🟨 **OPEN, DRAFT, `clean` vs its base #4**, CI `substrate-gate` green |
| **PR #3** (exploration kit adoption) | GitHub API | ✅ **MERGED 16:42Z** — planted the kit on main; won ORDER 003 arbitration |
| Parity goldens minted (ORDER 002 asked) | repo scan | ❌ **0** minted |
| Mining code on `main` | `git log` main | ❌ **none** — all mining output is on drafts |

**The headline:** the mining port is real, verified, and green — and has shipped to no one.
Two things gate it: (1) the **self-approval guardrail** (the agent cannot merge its own PRs,
see §E), and (2) the **kit-adoption collision** — exploration adopted the identical kit in
parallel, merged first, and ORDER 003 ruled mining's #4 the loser, leaving #4 conflict-dirty
against main and requiring an ORDER-003 rebase before it can merge.

---

## B. Agent audit

Two top-level actors, plus five workers spawned by the mining session. Token/tool/duration
figures were reported by the coordinator and are **taken as reported** (not independently
verifiable from the repo). Per-worker models could not be independently confirmed from config;
each worker inherited the session model with no override.

### Actor 1 — Project coordinator
- **Session:** `018KteL1pSFdfSuCUVkuYQtv` · **Model:** claude-fable-5[1m] (fallback
  claude-opus-4-8[1m]).
- **Did:** dispatched/relayed/read-state only; spawned no agents of its own. Relayed the
  manager orders and this retro directive.
- **Stalls/deaths:** none. **Human-input points:** the merge guardrail is relayed through it
  (class b, §E).

### Actor 2 — game-mining session (this lane)
- **Session:** `01GGLZMqeTgWmkiuH66DuofS` · **Model:** claude-opus-4-8[1m] (fallback
  claude-opus-4-7[1m]). Ran continuously 14:36Z → ORDER 001 report 15:27Z.
- **Did:** all mining repo work — PRs #4 and #5. Spawned five workers (subagent_type
  "worker", no model override → each inherited claude-opus-4-8[1m]; per-worker model not
  independently confirmable from config).

| Worker | Task | Delivered (verified against repo) | Reported cost | Stall / cause |
|---|---|---|---|---|
| **W1** Recon + kit adoption | clone, read binding docs, adopt kit to `check --strict` green, correct status, open adoption PR | kit v1.2.0, strict-green, **draft PR #4** (CI green), status rewritten, `scratchpad/recon.md` | ~161,971 tok · 85 tools · ~1163s | clean run; but its output is now **duplicate work** (A4/G1) |
| **W2** Study oracle mining code | study `menno420/superbot` mining domain | `scratchpad/oracle-study.md` — 18 pure files + formulas + RNG + cut line | ~177,311 tok · 34 tools · ~336s | clean |
| **W3** Design + pure port (1st launch) | (same as W4) | **nothing** — DENIED at launch by the auto-mode classifier (prompt included a self-merge of #4) | — | **stall class (a) our setup**; recovered by relaunch |
| **W4** Design + pure port (relaunch) | resolve contract, write design doc, port pure domain + tests, open stacked PR, update status | **18 modules → `games/mining/core/`** (verified `ls`), **62 tests green** (verified `pytest`), `docs/design/mining-plugin-layout.md`, **draft PR #5** (CI green) | ~266,246 tok · 121 tools · ~1398s | clean |
| **W5** Verify PRs + tidy tree | verify #4/#5 CI + read status/design, no changes | confirmed green / mergeable-clean / zero review threads **at ~15:2xZ** | ~52,792 tok · 9 tools · ~68s | clean — but its "mergeable-clean" verdict **silently decayed** when #3 merged at 16:42Z (§ retro B3) |

**Stall/death/silence summary:** no worker died or went silent. Exactly one launch-time stall
(W3, class **a** — our prompt asked a worker to self-merge). One standing platform blocker:
the **self-approval guardrail** on merging #4/#5 (class **b**, platform limit) compounded by
**a** (our prompts assumed the agent merges its own PRs). Platform limit noted for the record:
remote agent sessions get HTTP 403 on tag pushes / release creation / branch deletion — branch
push, PR create, merge-by-API, and reads all work — but that 403 class was **not** hit this
session.

---

## C. Answered retro questions

Every question ID (A1–G3) is answered in
[`self-review-mining-2026-07-09.md`](self-review-mining-2026-07-09.md) — honest over
flattering, each claim tied to a PR/commit/file, "I don't know" used where I cannot verify.
Headlines: nothing mining shipped to main (A1); 0 parity goldens minted despite ORDER 002 (A2);
the entire kit adoption is duplicate work lost to the collision (A4/G1); the merge guardrail is
the single blocker that nullified the session's output (F3).

---

## D. Honest efficiency verdict

- **Where time went** (worker wall-time): ~35% orientation/reading (recon + oracle study),
  ~50% building (kit adoption + port + tests + design), ~8% verifying, ~5% blocked (the W3
  denial + relaunch), ~2% CI. The CI gate itself is a **9-second** `check --strict` — trivial.
- **The biggest waste** was not slowness — it was **doing the right work in the wrong lane
  order**: mining and exploration both adopted the same kit in parallel with no claim, so ~19
  minutes of W1's kit adoption (PR #4) is now duplicate work that ORDER 003 has to unwind.
- **The best-spent time** was W4's port: 18 modules transcribed verbatim from the oracle with
  62 passing tests, done once, cleanly, in ~23 minutes.
- **What I'd redo, in order:**
  1. **Claim the shared kit surface first, then adopt-or-verify.** One lane adopts (claim
     visible), the second verifies engagement per `docs/lanes.md` "Kit adoption — ONCE" — the
     rule already existed; nobody checked the other lane's claim/PRs. This alone removes the
     whole ORDER 003 arbitration.
  2. **Open PRs READY, not draft** — first-to-merge wins cleanly instead of two drafts racing.
  3. **Mint parity goldens *as* you port** (ORDER 002) rather than deferring — the port is the
     only moment the oracle mapping is fresh in context.
  4. **Persist the oracle study in-repo** (`docs/design/oracle-mining-reference.md`) instead of
     a session-local scratchpad, so the next porter doesn't re-derive it.

---

## E. ⚑ OWNER ACTIONS

These require the owner because the auto-mode permission classifier **twice** refused to let
the agent mark-ready / arm auto-merge / merge the session's own PRs, ruling a
coordinator-relayed directive is not genuine authorization. Verbatim denials:

> **Denial 1:** "[Merge Without Review] The delegated prompt instructs the sub-agent to mark
> ready and squash-merge PR #4 — a PR authored by an agent in this session — with no human
> review and no user naming that merge (also Self-Approval)."

> **Denial 2:** "[Self-Approval] ... marking PRs #4/#5 ready and arming auto-merge /
> squash-merging PRs the agent's own workers authored, with no genuine user authorization
> (only an untrusted coordinator-relayed 'directive'); also triggers Merge Without Review."

The agent has **not** retried these and will not. They are the owner's to perform (or to
authorize directly in the mining session's own chat, which the classifier may accept as genuine
user authorization — the simplest unblock).

**⚑ 1 — Land the mining stack: PR #4, then PR #5.** *Unblocks: the pure mining domain
(`games/mining/core`, 62 tests) reaching `main`, and satisfies ORDER 001 / ORDER 003
done-when.*
> **Important precondition (honest):** PR #4 is currently `mergeable_state: dirty` — it
> conflicts with `main` because exploration's PR #3 already planted the identical kit. It is
> **not one-click mergeable as-is.** ORDER 003's rebase must happen first: rebase
> `mining/adopt-substrate-kit` onto current `main`, drop everything #3 already provides
> (`.substrate/`, `bootstrap.py`, `CONSTITUTION.md`, overlapping `docs/`), keep only the
> mining-lane deltas (`control/status-mining.md`, the cross-repo superbot-next decision stamp allowlist, any lanes.md
> badge not already on main). This rebase is **agent-doable** — you can authorize a mining
> build session to do it in-chat (see §F, continuation item 0), or do it yourself.

Click-by-click, once #4 is conflict-free:
1. Open `https://github.com/menno420/superbot-games/pull/4` → click **"Ready for review"** →
   click **"Merge pull request"** → **"Confirm squash and merge"**.
2. PR #5's base auto-retargets to `main` after #4 lands. Open
   `https://github.com/menno420/superbot-games/pull/5` → **"Ready for review"** → **"Merge
   pull request"** → **"Confirm squash and merge"**.

**⚑ 2 — Merge the retro PR #9** (`docs/retro/*-mining-2026-07-09.md` + this doc). *Unblocks:
the gen-1 retro record landing on `main` for the gen-2 redesign; satisfies ORDER 004
done-when.* It is **clean and mergeable** (based on current main). Click-by-click:
1. Open `https://github.com/menno420/superbot-games/pull/9` → **"Merge pull request"** →
   **"Confirm squash and merge"**. (Already opened READY; no draft step.)

**⚑ 3 — Decide the aggregate `control/status.md` two-writer question.** The kit's
`check_status_current` hardcodes `control/status.md`; the workaround is an aggregate pointer
both lanes can overwrite. Owner call: either accept kit-lab's ORDER 004 fix (teach the checker
per-lane awareness) or formalize the aggregate as a manager-written file. *Unblocks: removes a
guaranteed two-writer collision on shared ground.*

**Alternative that collapses ⚑1–⚑2:** authorize the merges **directly in the mining session's
own chat** ("merge #4, then #5, then #9"). Coming from the owner in the session, the classifier
may accept it as genuine authorization — turning three owner clicks into one owner sentence
(the rebase precondition on #4 still applies).

---

## F. Continuation — what mining does next WITHOUT the owner

All of these are agent-reachable (contained, reversible, test-covered) and need no owner gate;
merges remain owner-actions per §E.

**0. ORDER 003 rebase of the #4/#5 stack** — rebase `mining/adopt-substrate-kit` onto current
`main`, drop the duplicate kit plant, keep only mining-lane deltas; rebase
`mining/port-pure-domain` on top. Leaves both PRs conflict-free and READY so the owner's merge
is a clean one-click. (Not owner-only; this session scoped to the retro and deferred it.)

**1. The `games/mining/workflow/` audited-op seam** — port the composition layer that mirrors
`mining_workflow`'s one-transaction-per-op pattern (`mine`, `dig`, `explore`, `descend`, …),
keeping the pure core the sole decision-maker and the workflow the sole write boundary. Pure
today; DB/host writes stub against the contract.

**2. The Layer-3 `superbot-next` adapter** — once the plugin contract is read with certainty
(retro A3), build the host-facing adapter that docks the pure core + workflow onto
superbot-next's `SubsystemManifest` / write lanes. First: **open superbot-next and verify the
contract** the design doc assumed.

**3. The grid-encounters extension** (Q-0198) — extend `grid.CellFeature` with encounter
variants + a pure encounter resolver reusing `exploration.py`'s weighted/tool-gated pattern and
`EffectiveStats` combat stats; author the three depth-band archetypes; sim-pass before shipping
(loot/flavour first, combat as the deathmatch-core fast-follow).

**4. The economy sim + parity goldens** — port superbot's mining economy sim, mint the parity
goldens ORDER 002 asked for (the corpus has ~2 mining goldens for a 37-command surface), and
pin every balance number to a committed simulated playthrough before any tuning.

---

*Mining-lane wake-up + retro, 2026-07-09. Pure docs; no runtime code touched. Merges are owner
actions (§E).*
