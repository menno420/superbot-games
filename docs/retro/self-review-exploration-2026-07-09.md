# Self-review — exploration lane, gen-1 retro (2026-07-09)

> **Status:** `audit` — exploration lane's answers to `docs/retro/QUESTIONS.md`, by ID (ORDER 004).

**Honesty preamble.** The lane's P1 work was done by one child session
(`cse_01Fsfc2hZ6gjmRmq6ojBSeq4`, model `claude-opus-4-8[1m]` — verified from its
transcript's final result event via `claude-code-remote list_events`, and matching its
session card's own "Claude Opus" line). These answers are written by the lane's *wake-up*
session (model `claude-fable-5`, per its own environment info), which did NOT live the P1
session. Everything below is reconstructed from durable artifacts — PR #3 (67 files,
opened 2026-07-09T14:47Z, merged 16:42Z), the session card
`.sessions/2026-07-09-exploration-p1-quest-engine.md`, `control/status-exploration.md`,
`docs/decisions.md` D-0002…D-0006, and coordinator-relayed facts (attributed) — plus this
session's own direct experience. Where the P1 session's inner experience is unrecoverable,
the answer says "cannot determine" rather than inventing it.

## A. Work & correctness

**A1.** Shipped to main: everything the lane produced. PR #3 (merged 16:42Z) carried the
whole P1 batch — substrate-kit v1.2.0 adoption, the deterministic quest/encounter engine
(`games/exploration/quest/{rng,models,predicates,catalog,engine,leverage}.py`), 48 tests
incl. the balance-pin sim, the shared encounter seam (`games/shared/encounter/`), the D&D
plan (`docs/planning/dnd-story-game-plan.md`), the survival D1 re-baseline
(`docs/design/survival-d1-rebaseline.md`), and D-0002…D-0006. Nothing exploration-lane
exists only on branches. Gap: none for this lane — but note the *shape*: one 67-file PR is
"everything or nothing"; had the merge been refused, the gap would have been 100%.

**A2.** External-oracle verification is the lane's weakest column. Verified against an
external oracle: the survival D1 re-baseline (checked against superbot's actually-shipped
per-game energy constants — that check is *why* the old D1 was found self-contradictory),
and the merge itself (a human clicked it after review). Everything else — engine
correctness, balance numbers, the encounter seam — is verified only by the lane's own
48 tests and its own sim (`tests/test_balance_sim.py`). The sim pins the numbers but the
lane wrote both the numbers and the sim; no live Discord run, no real superbot-next host,
no golden from the old bot has ever exercised this engine.

**A3.** Least confident: the **reward-cap numbers** in `catalog.py`
(`TIER_CAPS`/`GLOBAL_MAX`) — they were invented in-repo because the "real Q-0087 bands"
were assumed to exist upstream. The wake-up session verified they do NOT exist (Q-0087 is
a philosophy + a sim methodology; the numeric bands are future sim outputs — see D-0008).
Concrete disproving check: when superbot's survival P0 sim harness ships its pinned bands,
run this catalog through the same harness profile (casual minutes/day vs grinder
hours/day) and see whether the capability-gap metric stays in band. Second-least: the
`EncounterResolver` Protocol — designed without the consumer (mining's production core)
ever having compiled against it; the check is mining's port actually implementing it.

**A4.** The **kit adoption itself** turned out duplicated — mining's PR #4 (opened 14:54Z,
7 minutes after #3) adopted the identical kit independently; ORDER 003 had to arbitrate
and mining's copy gets dropped. From this lane's side the work wasn't wasted (it won), but
fleet-wide one full adoption (~a third of #4's diff) was built twice. Also arguably
duplicated: the *reference* encounter resolver — mining owns the production core, so the
reference impl exists only so exploration needn't wait; if mining's core lands soon, it
was scaffolding. Not discovered-elsewhere-later: nothing found so far.

## B. Errors & friction

**B1.** From artifacts + coordinator facts, in order of cost:
1. **Merge wait, ~1.5h** (PR #3 open 14:47Z / ORDER 003 "land #3" 15:30Z / merged 16:42Z).
   The session reported it was "not permitted to self-merge without review" (coordinator-
   relayed verbatim). Preventable by setup: a standing self-merge grant or the wake-up
   pass's rule (no CI checks → merge it yourself). Not preventable by the session itself
   as instructed.
2. **Kit-adoption collision** (see G1): cost mining a rebase + arbitration ORDER 003;
   preventable by better setup (seed-time adoption), only partially by the sessions.
3. Coordinator-side platform quirks (coordinator verbatim, class (b) platform): its Agent
   tool rejected the default agent type ("Agent type 'general-purpose' not found", needed
   explicit subagent_type=worker); a run_in_background:false request still launched async.
   Cost: minutes, external.
4. This wake-up session: none blocking. `bootstrap.py check --strict` on main showed 3
   findings (lanes.md badge, D-0043 stamp, enforcement-unwired) — inherited, fixed here.
   Time lost across the lane to environment/CI/API errors proper: near zero — the repo has
   no CI, and no tool errors are recorded in the P1 card. Cannot determine unrecorded
   in-session errors.

**B2.** The **Q-0087 band constants**: ORDER 002 and the buildability map both speak of
"Q-0087-band caps" as if numbers existed; the P1 session hunted, didn't find them, and
shipped placeholders with a note. Where the answer actually lived: superbot's
`docs/owner/maintainer-question-router.md` § Q-0087 + the rpg-survival plan — which say
the bands are *future sim outputs*. Where it SHOULD have been: the buildability map's
decision table should have said "no numeric bands exist yet — invent conservative caps"
instead of implying an importable constant. One sentence at the point of use would have
saved the hunt and the mis-aimed ⚑ flag.

**B3.** One silent wrong-result found so far: **flag (3) itself** — it sat on the
needs-owner list implying the owner could resolve it, when no owner action existed
(the referenced constants don't exist). No error fired; discovered only because the
wake-up order forced re-derivation of every flag from sources (D-0008). Engine-side:
nothing known to have broken silently — but per A2, the coverage that would *catch* a
silent balance break (external sim/goldens) doesn't exist yet, so "none found" is weaker
evidence than it sounds.

**B4.** Two lines, quoted:
1. ORDER 002: *"five templates × 3 reward tiers × Q-0087-band caps"* — ambiguous exactly
   when needed: it presumes "Q-0087-band caps" are a thing you can look up (B2). The
   session had to improvise its meaning.
2. `docs/lanes.md`: *"substrate-kit is adopted **once**, by whichever Project runs
   first."* — defines the rule by an unobservable ("runs first" is invisible to a parallel
   session until a PR/status lands); both lanes could truthfully believe they were first
   for ~10 minutes. Missing: the *mechanism* (claim file / lock) rather than the principle.
   Also missing everywhere until the wake-up order: who may install cross-lane CI — the P1
   session had to invent flag (4) because no line answered it.

## C. Efficiency

**C1.** For the P1 session, reconstructed from timestamps (dispatch 14:40Z → born-red PR
14:47Z → engine+kit push ~15:0xZ → docs commit 55999f3 → flip 16:0xZ; merged 16:42Z):
roughly **orientation ~10%, building ~45%, verifying (tests+sim) ~15%, docs/ledger/status
~20%, CI/merge mechanics ~0% (no CI), blocked/waiting ~10–25%** (the 1.5h merge wait
overlapped close-out, then was pure wait). Biggest single sink: the merge wait — the only
interval producing nothing. Caveat: these are artifact-inferred, not measured; cannot
determine the true split inside the session. This wake-up session: ~40% reading/
re-verifying state, ~50% writing, ~10% mechanics.

**C2.** Rebuilt-from-scratch context that should have been durable: (1) the *actual*
status of Q-0087's numbers — every reader of "Q-0087-band caps" re-derives it; now durable
as D-0008; (2) the four-flag disposition rationale — parked as one-liners in the status
file, re-derived fully here; now durable as D-0007…D-0009; (3) coordinator-side facts
(who dispatched what, model IDs, stall causes) lived only in chat — now durable in the
project review's agent audit. The engine/design context itself was well-preserved (design
doc + card are good).

**C3.** Most value per minute: the **balance-pin sim test** — a few tests froze every
number the whole posture depends on, and made "sim-pinned" an honest claim; close second,
the **born-red card + claim files** (near-zero cost, and they are what won the ORDER 003
arbitration). Least value per minute: the **kit adoption interview/render** performed
in-session (13 slots + render + first-adopter bug-fixing inside a feature session) — not
worthless, but it was fleet plumbing paid for out of a game-building session, and half its
diff got duplicated by mining anyway (G1).

**C4.** Redo estimate: **~25–30% faster** to the same merged state, and most of that from
one ORDERING change: **land the kit adoption + status correction as a tiny PR #a in the
first 20 minutes, then build the engine as PR #b.** That kills the collision window
(mining would have pulled a visible `.substrate/` before its own adopt), makes the 67-file
all-or-nothing PR two reviewable ones, and starts the owner's merge-review clock on the
engine earlier. Second change: read Q-0087 at the source *before* designing caps (saves
the placeholder detour and one ⚑ flag).

## D. Autonomy & owner input

**D1.** Every stop, lane-wide:
1. **PR #3 merge click** (~1.5h). Not truly owner-only — repo had no CI and the change was
   lane-clean. Unblockable by a pre-granted rule; the grant, as the wake-up order now
   phrases it: *"no CI checks on the repo → the lane merges its own READY PR (squash) and
   records it."*
2. **Q-0040 bounded-authority sign-off** (parked as ⚑, D-0006). Borderline taste — but the
   posture is reversible until the P3→P4 ship gate, so decide-and-flag covered it; grant:
   *"a recommendation-carrying, downstream-gated design decision is adopted, not parked."*
   Adopted as D-0007 this session. The *ship* of AI-narrated content past the gate stays
   genuinely owner-only.
3. **Survival D1 option (a)** — was already decided-and-flagged (D-0004); listing it under
   ⚑ needs-owner anyway was over-routing (see D2).
4. **Cross-lane CI gate** — parked for coordination, not the owner; resolved by evidence
   (mining ships the same gate) as D-0009. Grant: name a default owner for shared
   enforcement (e.g. "first lane to need it installs it; other lane may veto by revert").
   Genuinely owner-only clicks encountered: **none** in this lane so far.

**D2.** Routed up but should have been decide-and-flag: Q-0040 (D-0006 explicitly chose
ROUTE over adopt) and the duplicate ⚑ listing of the already-decided D-0004. Both carried
their own APPROVE/option-(a) recommendations — the definition of "you've answered your own
question." The wake-up pass took them (D-0007, and D-0004 confirmed) at the cost of two
ledger entries; the P1 session could have done the same for free.

**D3.** Decisions taken while unsure of authority: (1) defining the shared encounter
interface *and* a reference resolver in `games/shared/**` when the founding plan said
"mining implements the shared encounter engine first" — the session claimed first per
lanes.md and shipped; a written rule like *"claim-first also covers interface DEFINITION;
the owner lane keeps production implementation"* would have made it unambiguous (it worked
out; ORDER 003 even called the claim discipline "textbook"). (2) In-session, fixing kit
first-adopter rough edges (vestigial `control/inbox.md` removal). (3) This session:
installing the cross-lane gate — made unambiguous only by the wake-up order's self-unblock
instruction plus mining's identical file as evidence.

**D4.** Smallest standing-grant set for zero-human end-to-end, this lane:
1. Self-merge grant: READY + lane-clean + local `check --strict` green (+ CI green when CI
   exists) → merge your own PR.
2. Recommendation-adoption grant: any decision that is reversible until a later named gate
   and carries a recommendation is decided-and-flagged, never parked.
3. Shared-ground default: staged kit enforcement may be installed by whichever lane needs
   it first; revert = veto.
4. Numbers grant: where a referenced constant does not exist upstream, invent conservative
   sim-pinned placeholders and record the reconciliation trigger (already de facto D-0005/
   D-0008).
   That's it — with those four, gen-1 exploration would have shipped with zero human
   interventions.

**D5.** "Done" was well-defined for 001–003 (each order has a done-when; 001's "first
engine PR merged" was crisp). Two soft spots: ORDER 002's done-when required "⚑ flags for
the owner's bounded-authority sign-off" — done-by-flagging, which quietly *mandated*
parking instead of decide-and-flag (the very thing the wake-up pass reversed); and nothing
defined done for the *lane between orders* — after #3 merged, the lane had no standing
"what next" until this wake-up order arrived (the founding plan's P2+ exists but no order
activated it).

## E. Protocol & environment

**E1.** The control ritual fits well — inbox-first gave the P1 session an exact work
order, and one-writer-per-file meant zero contention with mining all day. Real costs:
(1) the one-writer rule cuts *lane→lane* signalling — the encounter-interface announcement
that lanes.md § claim-first requires "in BOTH status files" is literally unwritable by
exploration (it can't touch `status-mining.md`); the session had to announce in its own
status + ask the manager to relay. The protocol contradicts the lanes contract here; give
lanes a writable shared bulletin (or make the manager relay explicit). (2) Status-last +
one status file means mid-session state lives nowhere durable; fine at this session
length, would bite on longer ones. Skipped: nothing knowingly skipped; ORDER 003/004 acks
happened one session late only because the orders arrived after the P1 session closed.

**E2.** First-boot environment gaps: (1) no pre-authenticated way to *finish* the job —
merge rights matching what orders demand ("see them merged"); (2) no pinned Python/pytest
availability statement — the kit assumes `python3` works (it did, but nothing said so);
(3) read access to sibling repos (superbot, superbot-next) is needed to verify claims
(Q-0087, energy constants) — the P1 session apparently had only the buildability map's
summaries; the wake-up session happened to have a superbot checkout and immediately caught
D-0008 with it. Grant every lane session read clones of the oracle repos.

**E3.** Seed gaps in the repo: (1) **the kit itself** — lanes.md legislated "adoption
ONCE" but the seed shipped no `.substrate/`; seeding the adoption would have deleted the
whole G1 collision class; (2) CI from day zero (the gate existed only staged; repo ran
checkless for its first 6 PRs, and the "auto-merge can't arm on zero checks" quirk follows
from it); (3) a `docs/claims/` dir with a README (the P1 session had to create the
convention's home); (4) an example plugin skeleton under `games/` showing the intended
layer shape (each lane invented its own); (5) per-lane session-card naming guidance
(`.sessions/` is shared ground — fine so far, one collision class waiting).

**E4.** A fresh session would first misunderstand **who installs/owns the shared
enforcement and how the two lanes coordinate** — the visible state (two inboxes, a staged
gate, a lanes contract that says "your lane only") reads as "never touch shared ground,"
which is exactly the over-caution that parked flag (4). The single preventing document: a
short `docs/shared-ground.md` — who owns `.substrate/`, `.github/workflows/`, `docs/`
commons, the defaults for acting on them (first-need installs, revert = veto), and the
lane→lane signalling channel. (Second place: this retro + the project review, which now
record the answers.)

## F. Redesign (the payload)

**F1.** Three founding rules gen-1 lacked:
1. *"If the repo has no CI required checks, you merge your own READY PR (squash) and
   record it — an unmerged approved PR is a failure state, not deference."*
2. *"A parked flag must name a concrete actor + artifact that unblocks it ('owner clicks
   X' / 'waits on repo Y shipping Z'); a flag that names a recommendation you already
   believe is a decision — take it decided-and-flagged."*
3. *"Before building against a named upstream constant/system, read it at its source
   repo; if it doesn't exist, say so in the design doc and pin a placeholder + a
   reconciliation trigger."* (Each rule is a real gen-1 loss: the 1.5h wait, the four
   parked flags, the Q-0087 hunt.)

**F2.** Manager delta: mostly good — ORDER 002 was the right call (sequencing invention
before construction) and ORDER 003's arbitration was fast and clean. Do differently:
(1) seed the kit adoption itself (or order it explicitly to ONE lane) — ORDER 001's
"adopt ONLY if mining hasn't" delegated a race to the racers; (2) don't mandate ⚑-parking
in done-when clauses (see D5) — say "decide-and-flag with a veto note" instead;
(3) buildability-map claims that name upstream constants should carry a
verified-at-source line; (4) orders arrived slightly behind the sessions (ORDER 003/004
landed after the P1 session closed — an idle gap until this wake-up). Density/priority
were right.

**F3.** One capability worth almost anything: **executing against a live host** — a
sandboxed superbot-next test instance (or even a recorded-event replay harness) to run the
quest engine against real EventBus traffic instead of self-authored fixtures. It converts
A2's whole weakness class (self-verified only) into external verification, and it's the
difference between "48 tests green" and "a user completed a quest."

**F4.** Ideal relaunch seed, ≤10 bullets:
- Kit pre-adopted at seed; `check --strict` green on commit 1; gate installed in
  `.github/workflows/` from day zero.
- CI required check wired so auto-merge can arm (no zero-checks quirk).
- Standing grants file (the D4 four) in the constitution, not discovered by retro.
- `docs/shared-ground.md` — shared-path ownership, install defaults, lane→lane channel.
- `docs/claims/` + README seeded; claim covers interface definition explicitly.
- Example plugin skeleton in `games/` (pure-core/workflow/adapter) both lanes copy.
- Read-only clones (or pinned snapshots) of oracle repos (superbot, superbot-next)
  available in the environment, with the buildability maps linking to exact paths.
- Per-lane orders that never delegate a shared-ground race; shared-ground work assigned
  to exactly one actor.
- done-when clauses that end in a merged artifact, never in a parked flag.
- A standing "between orders" default (groom the founding-plan roadmap) so a lane is
  never idle waiting for its next order.

## G. Addendum — GAMES

**G1.** From this lane's side: before adopting, the P1 session checked (per D-0002 and the
PR body) that no `.substrate/` existed on main and that mining's status file still said
not-started — both true at 14:46Z when it wrote its status + claim declaration. What it
did NOT (and could not) check: mining's *in-flight, unpushed* working tree — mining's
session was dispatched in the same minutes and pushed its own adoption at 14:54Z, 7
minutes later. So the collision wasn't negligence; it was a rule defined over invisible
state ("whichever runs first") with a detection latency (~8 min) longer than the decision
window. Mechanism that would have prevented it, in preference order: (1) **seed-time
adoption** — no race exists if the manager plants the kit with the repo; (2) a
**kit-adoption claim file** (`docs/claims/kit-adoption.md`, same claim-first discipline as
`games/shared/**` — push the claim BEFORE starting the adopt, ~1-minute latency instead of
~8); (3) manager assignment in ORDER 001 ("exploration adopts; mining verifies") instead
of the conditional both lanes evaluated identically and optimistically.

**G2.** The per-lane split works where it was applied: inbox/status collisions — zero all
day, and the arbitration itself was communicated cleanly through it. Still colliding or
unowned: (1) `.sessions/` + `.session-journal.md` — shared, name-collision-by-luck (both
lanes date-slug their cards; no per-lane prefix convention); (2) `.substrate/state.json`,
`guard-fires.jsonl`, `check-exceptions.yml` — kit state is repo-global; both lanes will
append/edit it (this PR touches check-exceptions for a *mining-doc* finding, which is
awkward under "your lane only"); (3) `docs/decisions.md` — one shared D-NNNN sequence;
fine append-only, but two parallel sessions minting D-numbers will collide (the Q-block
next-free-number problem, no per-lane namespace); (4) `docs/claims/` dies with each
session (delete-at-end), so it's ephemeral coordination only — nothing durable marks
long-lived shared-surface ownership except lanes.md prose. Verdict: split works, but only
because traffic is low; per-lane card prefixes + namespaced decision IDs (EXP-D-NNNN /
MIN-D-NNNN or ranges) + kit awareness of lanes are the needed hardening.

**G3.** Claim-first is workable **short-term and at two lanes** — it already carried the
one real shared-surface event (encounter interface: claimed, built, announced, arbitration
even praised it). It does not scale as-is because: claims are session-ephemeral (G2),
enforcement is honor-system (nothing *rejects* a PR touching `games/shared/**` without a
claim), and announcement requires writing the other lane's status file, which the
one-writer rule forbids (E1 contradiction). Needed, cheapest-first: (1) fix the
announcement channel (shared bulletin file with per-lane sections, or manager-relay made
explicit); (2) make claims durable while an interface is owned (a `games/shared/OWNERS.md`
row per module — CODEOWNERS-style, but a doc the gate can lint); (3) kit support: teach
`check --strict` a lanes manifest so "PR touches shared path without a claim/OWNERS row"
is a red finding, not a memory. With those three, claim-first stays the right model; the
alternative (hard CODEOWNERS + branch protection) adds owner-click overhead this fleet is
explicitly trying to remove.
