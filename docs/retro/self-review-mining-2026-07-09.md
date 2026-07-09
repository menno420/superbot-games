# Mining lane — gen-1 self-review (2026-07-09)

> **Status:** `audit` — answers to `docs/retro/QUESTIONS.md`, mining lane. Honest over
> flattering. Each claim is tied to a PR/commit/file where possible. "I don't know" is used
> where I genuinely cannot verify.

Scope of "I" below: the game-mining lane session (model Claude Opus 4.8, session
`01GGLZMqeTgWmkiuH66DuofS`) and the five workers it spawned. Facts about token/tool counts and
worker models were reported by the coordinator and are taken as reported — they are not
independently verifiable from the repo, and that limit is flagged where it matters (A2).

---

## A. Work & correctness

**A1 — Shipped to main vs. only on branches/drafts.**
Nothing from the mining lane reached `main`. Everything mining produced sits on **two open
draft PRs**: PR #4 (`mining/adopt-substrate-kit`, kit adoption) and PR #5
(`mining/port-pure-domain`, the pure-domain port, stacked on #4). The gap has two causes:
(1) both PRs were deliberately left **draft** pending a merge convention that this repo never
stated at seed (see B4/D1); (2) the **kit-adoption collision** — the exploration lane adopted
the same kit in parallel and its PR #3 **merged first** (16:42Z), so the manager's ORDER 003
ruled exploration's adoption the winner and mining's #4 the loser. As of this retro, PR #4 is
`mergeable_state: dirty` (it conflicts with main because #3 already planted the identical
`.substrate/`, `bootstrap.py`, `CONSTITUTION.md`, and overlapping `docs/`). So the honest
answer: **the port (games/mining/core, 18 modules, 62 tests) is real and verified but has
shipped to no one** — it is gated behind a merge the agent is not permitted to perform and a
rebase that ORDER 003 asked for but this session did not execute.

**A2 — Verified against an external oracle vs. only my own tests.**
- *Against an external oracle (the source repo `menno420/superbot`):* the port formulas and
  constants were transcribed **verbatim** from the oracle's `disbot/utils/mining/*` and
  `disbot/utils/equipment.py` and cross-checked against `scratchpad/oracle-study.md`. That is
  oracle-pinned in the sense that the spec is shipped upstream behavior.
- *Only my own tests:* the 62 unit tests in `tests/mining/` are **self-authored** — they
  assert the port matches my *reading* of the oracle, not a recorded golden from a live run of
  the oracle bot. ORDER 002 asked to **mint parity goldens** against the oracle; that was **not
  done** this session (0 parity goldens minted). So "matches the oracle" is verified only to
  the strength of my transcription + my tests, **not** to a byte-for-byte captured oracle run.
- *Not verified by any human or live deploy:* nothing was deployed; there is no Discord host in
  this repo yet (the plugin contract is still in flight in `superbot-next`).
- I **cannot independently verify** the per-worker token/tool/duration figures or the workers'
  models — those were reported to me, not measured by me.

**A3 — Least confident piece + the check that would settle it.**
The **superbot-next plugin contract mapping** in `docs/design/mining-plugin-layout.md`. The
design maps the pure core onto superbot-next's `SubsystemManifest`, but the contract is **in
flight in another repo** and was not opened with certainty this session (recon.md OPEN
QUESTION #1 flags exactly this). Concrete disproof: open `superbot-next`'s actual manifest
schema / plugin entry points / host-write API and diff the design doc's assumed seams against
it. If they diverge, the adapter layer is designed against a guess.

**A4 — Built that was unnecessary / duplicated / already existed.**
The **entire kit-adoption work (PR #4, worker W1, ~19 min)** is now largely redundant: the
exploration lane adopted the same `substrate-kit v1.2.0` in parallel, merged first (#3), and
won the ORDER 003 arbitration. After the ORDER 003 dedup, #4 collapses to a handful of
mining-only deltas (its `control/status-mining.md`, the cross-repo superbot-next decision
stamp allowlist, a
`docs/lanes.md` badge) — the ~11,700-line kit plant it carries is duplicate of what #3 already
landed on main. This is the textbook parallel-agent duplicate-work loss the claim-first rule
in `docs/lanes.md` exists to prevent (see G1). I **did not check `docs/claims/` or open PRs
before adopting**, so I could not have seen exploration's in-flight adoption.

---

## B. Errors & friction

**B1 — Every error hit.**
1. **W3 launch denial (auto-mode classifier).** The first launch of the "design + pure port"
   worker was denied because its prompt included a step to self-merge PR #4. Time lost: one
   worker launch + relaunch cycle. **Preventable by us** (our prompt asked a worker to
   self-merge — a self-approval the classifier always refuses). Class (a) our setup.
2. **Self-merge guardrail on #4/#5 (this session and the retro session).** The classifier
   refused, twice, to let the agent mark-ready / arm / merge its own PRs, ruling a
   coordinator-relayed directive is not genuine user authorization. Class **(b) platform
   limit** compounded by **(a)** (our workflow assumed the agent merges its own PRs). This is
   the single biggest blocker: it is why nothing shipped to main.
3. **`.substrate/guard-fires.jsonl` churn.** The tracked telemetry file is appended on every
   `bootstrap.py check` run, so the tree is perpetually dirty and `git checkout <branch>`
   aborts with "local changes would be overwritten." Cost this retro session several minutes
   and one denied tree-wide-discard attempt. **Preventable by better setup** — recon.md OPEN
   QUESTION #4 already flagged gitignoring it. Class (a).
4. **`.substrate/backup/bootstrap-1.2.0.py` untracked-vs-tracked collision.** #4 gitignored
   the backup dir; #3 committed it. On `git pull` the untracked local copy blocked the merge.
   Minor, class (a).
- No environment, dependency, or API errors hit. No worker died or went silent.

**B2 — Already documented somewhere I didn't find.**
The **merge/auto-merge convention**. superbot's own `.claude/CLAUDE.md` has an elaborate
auto-merge-on-green doctrine, but this repo's seed (`docs/lanes.md`, `control/README.md`)
never restated it, so W1 left #4 draft "awaiting a convention." It should have been in
`docs/lanes.md` (or `CONSTITUTION.md`) at seed — the one place a first session reads before
opening a PR. The manager later supplied it in ORDER 003 ("READY + auto-merge, never draft"),
i.e. *after* the drafts had already stalled.

**B3 — Broke silently (no error, wrong result).**
Worker **W5 verified PR #4 as "mergeable-clean, zero review threads"** at ~15:2xZ. That was
true then and **silently became false** at 16:42Z when exploration's #3 merged the same kit
to main — #4 is now `dirty`. Nothing errored; a point-in-time green verification simply
decayed. Discovered only in this retro by re-reading the live PR state via the GitHub API.
Lesson: "mergeable-clean" is not durable while sibling PRs touching the same shared surface
are open.

**B4 — Ambiguous / contradictory / missing instruction, quoted.**
From PR #4's own notes: *"Left as draft; not arming auto-merge (no repo convention here
directs it — awaiting manager/coordinator)."* The **absence** of a stated merge convention was
the ambiguity — the session correctly sensed a decision it couldn't source and defaulted to
the most conservative (draft), which turned out to be exactly wrong per the later ORDER 003
(*"drafts don't land"*). A one-line convention at seed would have removed the guess.

---

## C. Efficiency

**C1 — Rough % of time, biggest sink.**
Across the lane's worker wall-time (W1 ~19m, W2 ~6m, W4 ~23m, W5 ~1m; W3 denied):
- Orientation/reading (recon + oracle study): **~35%** (W1's read-binding-docs half + all of
  W2).
- Building (kit adoption + port + tests + design doc): **~50%**.
- Verifying (W5 + in-worker checks): **~8%**.
- CI/merge mechanics: **~2%** (CI itself is a 9-second `check --strict`).
- Blocked/waiting: **~5%** (the W3 denial + relaunch).
**Biggest single sink: the kit adoption (W1, ~19m) — most of which A4 shows was duplicate
work.** The most *valuable* time (the port + tests, W4) was also the largest single block, and
that time was well spent.

**C2 — Context rebuilt from scratch that should have been durable.**
The **oracle mining domain map**. W2 spent ~6m reconstructing the mining subsystem's file
inventory, formulas, RNG model, and cut line from `menno420/superbot`. That is now durable in
`scratchpad/oracle-study.md` — but a scratchpad file is session-local; it should live in the
repo (e.g. `docs/design/oracle-mining-reference.md`) so the next porter doesn't re-derive it.
The superbot-next contract (A3) is the *other* context that had to be guessed rather than read.

**C3 — Most / least value per minute.**
- *Most:* `python3 bootstrap.py check --strict` — a 9-second gate that catches doc/stamp/status
  drift and is the single required CI check. High signal, near-zero cost.
- *Least:* the kit adoption itself (A4) — high cost, ~zero net value after arbitration. Not the
  tool's fault; the waste was doing it in parallel with exploration without a claim.

**C4 — Redo speed + biggest ordering change.**
Probably **~40% faster**. Biggest ordering change: **claim the shared kit surface first, then
either adopt or verify-only.** The correct gen-1 order was: one lane adopts the kit (with a
claim visible to the other), the second lane *verifies engagement* rather than re-adopting —
exactly what `docs/lanes.md` "Kit adoption — ONCE" already says. Both lanes adopted anyway
because neither checked the other's claim/PRs first. Secondary change: **open PRs READY, not
draft**, so the first-to-merge wins cleanly instead of two drafts racing.

---

## D. Autonomy & owner input

**D1 — Every stop for owner input / human click.**
1. **Merge PR #4 → PR #5.** Blocked from the agent side by the self-approval guardrail
   (class b). **Truly owner-only under the current platform** — the classifier will not accept
   a coordinator-relayed merge directive as authorization. Unblockable only by the *owner*
   (a click, or an in-chat authorization in the mining session), or by a platform-level grant
   that trusts a named manager.
2. **Merge this retro PR (#9).** Same guardrail, same owner-only status.
3. **The ORDER 003 rebase of #4/#5.** *Not* owner-only — an agent can rebase/forward-merge to
   drop the duplicate kit plant. This session did not do it (scope was the retro); flagged as a
   self-doable continuation item, not an owner action.

**D2 — Routed upward that should have been decide-and-flag.**
The **draft-vs-ready merge decision** (B4). W1 effectively routed it upward by leaving #4
draft "awaiting manager/coordinator." Under decide-and-flag it should have opened READY with a
one-line "merging on green per the fleet convention; veto if wrong" — reversible until merge,
so it did not warrant a stop.

**D3 — Took while unsure I was allowed to.**
Adopting the kit and **removing the vestigial `control/inbox.md`** seed, gitignoring
`.substrate/backup/`, and allowlisting the cross-repo superbot-next decision stamp — all done without explicit
permission. They were correct and contained, but a written *"first adopter may fix kit
first-run rough edges and record them under ⚑"* rule would have made them unambiguous.

**D4 — Smallest standing grants for zero-human end-to-end.**
1. *"A named manager/coordinator's relayed directive to merge a green, lane-clean PR is genuine
   authorization"* — the single grant that would unblock D1.1–D1.2.
2. *"Open lane PRs READY and arm auto-merge on green by default; hold only with a stated
   reason."* — kills the draft-stall.
3. *"The first lane to touch a shared surface files a claim; the second verifies, never
   re-does."* — kills the G1 collision.

**D5 — Did I always know what "done" meant?**
Mostly. ORDER 001's done-when (*"acked=001 with kit check --strict green and the first port PR
merged"*) was clear but **unreachable by the agent** — it requires a *merge* the agent can't
perform, so "done" was defined in terms of an action outside the agent's authority. ORDER 004's
done-when (*"self-review merged"*) has the same defect: it defines done as a merge the
classifier blocks. "Done" should be defined as *"PR open, READY, green"* for an agent whose
merges are owner-gated.

---

## E. Protocol & environment

**E1 — Did the control/ ritual fit?**
Mostly yes, and cheaply. Inbox-first / status-last / never-edit-inbox is light and the
one-writer-per-file rule prevented any control-file collision between lanes. The one cost:
the kit's `check_status_current` **hardcodes `control/status.md`** while this repo uses per-lane
`control/status-mining.md` — the first adopter had to keep an aggregate `control/status.md`
pointer as a workaround (relayed to kit-lab as their ORDER 004). Not skipped anywhere.

**E2 — Environment should have contained at first boot.**
The repos were pre-cloned (`superbot`, `superbot-next`, `substrate-kit`, `superbot-games`
were all present), which was excellent. Missing: nothing environmental blocked work. If
anything, a pre-resolved read of the `superbot-next` plugin contract would have removed the
one guess (A3).

**E3 — Repo should have contained at seed.**
1. A **merge convention** (READY + auto-merge on green) in `docs/lanes.md` — its absence caused
   the draft stall (B2/B4).
2. **`.substrate/` engaged at seed by the manager** (or a claim/lock naming who adopts it), so
   neither lane races to adopt it (G1).
3. **`.substrate/guard-fires.jsonl` gitignored** (or the churn documented) so `git checkout`
   doesn't abort (B1.3).
4. A stated home for **oracle-reference docs** so W2's study is durable, not scratchpad-local
   (C2).

**E4 — What a fresh no-history session would misunderstand first, and the one doc to prevent it.**
It would misunderstand **"is the kit already adopted, and by whom?"** — and might re-adopt,
re-triggering the G1 collision. The single preventing document: a **`docs/lanes.md` "Shared
surface status" line** (or a `docs/claims/` entry) stating *"substrate-kit adopted by
exploration in #3; all lanes verify-only."* Second-most-likely misunderstanding: that the
mining port is on `main` (it is not — it's on draft PR #5).

---

## F. Redesign (the payload)

**F1 — Three rules I'd add to the next Project's founding instructions.**
1. **Claim before you touch any shared surface — including `.substrate/`/the kit.** File a
   one-line claim in `docs/claims/` *and* scan open PRs before adopting or editing anything not
   exclusively in your lane. (Directly prevents G1.)
2. **Open PRs READY and arm auto-merge on green; never draft.** A draft is an abandoned-PR
   risk and loses a first-to-merge race. Hold only with a stated `⚑` reason.
3. **Define "done" as an agent-reachable state** ("PR open, READY, green"), and put every
   merge/human-click the agent can't perform on an explicit **owner-actions list** at PR-open
   time — never as the order's done-when.

**F2 — What the manager should have done differently.**
Orders were well-scoped and correctly prioritized. Two misses: (1) **ORDER 001 required a
merge in its done-when** that the agent could not perform — the merge convention and the
merge-authority reality should have been in the *seed*, not discovered via a mid-stream
arbitration (ORDER 003); (2) **the kit-adoption race was foreseeable** — two lanes booted in
parallel against a repo with no `.substrate/` and a "adopt it once" rule but no claim/lock, so
both adopted. Seeding the kit (or naming the adopter) before dispatching either lane would have
prevented the whole ORDER 003 arbitration.

**F3 — One capability I'd trade almost anything for.**
**Authority to merge a green, lane-clean PR on a trusted manager's relayed directive.** It is
the single thing that stands between this lane's verified work and `main`. Every other friction
was minor; this one nullified the session's output.

**F4 — Ideal seed state (≤10 bullets).**
1. `.substrate/` **already adopted and engaged** by the manager at repo birth (no lane races to
   adopt).
2. `docs/lanes.md` states the **merge convention** (READY + auto-merge on green) and the
   **claim-first rule for every shared surface**, kit included.
3. `.substrate/guard-fires.jsonl` gitignored; `.substrate/backup/` gitignored — no tree churn.
4. A **`docs/design/oracle-*-reference.md`** stub naming where the oracle map lives, so study
   is durable.
5. The **superbot-next plugin contract** either pinned in-repo or a pointer with its exact
   path, so the adapter is designed against fact not a guess.
6. Per-lane `control/status-*.md` supported by the kit checker natively (no aggregate-pointer
   workaround).
7. Done-when clauses phrased as **agent-reachable states**, with merges on an owner-actions
   list.
8. A **`docs/claims/` seeded with the kit-adoption claim already resolved.**
9. A one-page **"read me first, in this order"** router (the kit's `AGENT_ORIENTATION.md`
   already does this — keep it).
10. Parity-golden **fixtures scaffold** (`tests/mining/goldens/`) present and empty, so
    "mint goldens as you port" has an obvious home.

---

## G. Addendum — GAMES

**G1 — The kit-adoption collision, from my side.**
- *What I checked before adopting:* whether `.substrate/` already existed (it did not), and
  `docs/lanes.md`'s "Kit adoption — ONCE" rule (which I read as "I'm first, so I adopt").
- *What I did NOT check:* `docs/claims/` and **open PRs**. Had I looked, exploration's PR #3
  (opened 14:47Z, adopting the same kit) was already in flight when mining's #4 opened
  (14:54Z) — seven minutes earlier. I never filed a claim of my own either. `docs/lanes.md`'s
  claim-first rule is written as scoped to `games/shared/`, so I read it as **not** applying to
  `.substrate/` — that scoping gap is the root cause (ORDER 003 explicitly corrects it:
  *"the claim-first rule applies to ALL shared surfaces incl. `.substrate/`"*).
- *The rule/mechanism that would have prevented it:* **seed-time adoption by the manager** is
  the strongest (nothing to race). Failing that, a **claim file OR a lock file for the kit
  surface**, plus rewording `docs/lanes.md` so claim-first covers every shared surface, not
  just `games/shared/`. A pure "check open PRs first" habit would also have caught it, but a
  mechanism beats a habit.

**G2 — Per-lane control files: does the split work?**
The **inbox/status split works** — one writer per file, zero control-file collisions between
lanes all day. What still collides on shared ground: (1) **`.substrate/`** — the kit is a
single shared surface both lanes tried to own (G1); (2) **`.substrate/guard-fires.jsonl`** and
**`.substrate/state.json`** — appended by every `check` run, so two lanes' runs produce
conflicting diffs; (3) **`control/status.md`** — the aggregate-pointer workaround is a
two-writer file by construction (recon.md OPEN QUESTION #2). The session-journal and per-lane
`.sessions/` cards did *not* collide (per-file convention holds).

**G3 — Shared `games/shared/`: is claim-first workable long-term?**
For *low-frequency* shared edits, yes. For a surface both lanes touch often (the shared
encounter engine — mining implements it, exploration consumes it), claim-first is a soft lock
that depends on discipline and loses races (exactly how G1 happened on `.substrate/`). Long
term it wants something **stronger**: either **CODEOWNERS-style required review** on
`games/shared/` (the owning lane must approve), or **kit-level claim support** (a real lock
file the checker enforces, not a convention). The interface-change-announced-in-both-status-files
rule is good but is a *notification*, not a *lock* — it tells you after the fact, it doesn't
prevent the collision.
