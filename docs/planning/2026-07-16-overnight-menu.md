# Overnight planning menu — un-filtered proposal set (2026-07-16)

> **Status:** `plan` — an UN-FILTERED idea menu for owner triage, NOT approved
> work. Nothing here is claimed, scheduled, or building. Every proposal is a
> candidate the owner accepts, defers, or vetoes tomorrow; the point is BREADTH,
> not a curated shortlist. Grounded in a fresh read of the repo at the HEAD
> below — citations are to real files/PRs, but sizes/risks are estimates.

- **HEAD:** `197966d` (`slice: shared deterministic-RNG seam — extract mining's
  splitmix64 into games/shared/rng.py (#150)`).
- **Date:** 2026-07-16.
- **Suite baseline:** 821 passed (810 pre-#150 + 11 in `tests/shared/rng/`);
  ~97% coverage of `games/` + `services/` at the #120 groom.
- **How to read this:** ideas are numbered (M1…) and grouped by category. Each
  carries a one-line Pitch, an Effort (S/M/L), a Risk & reversibility line, and
  an Unblocks/enables line. Reference an idea by its number in triage.
- **Deliberately exhaustive:** weak and ambitious ideas are BOTH included on
  purpose. Do not read inclusion as endorsement — the owner filters.

Legend — Effort: **S** ≈ one focused slice · **M** ≈ a few slices / one design
pass · **L** ≈ multi-session or design-gated. Reversibility: ↩️ = easily undone
(docs/tests/additive) · ⚠️ = behaviour change, revert is a real diff · 🔒 =
owner-gated or hard to reverse.

---

## A. Engine / shared code

**A1 — Migrate fishing's RNG onto `games/shared/rng.py`.**
Pitch: `games/fishing/core/rng.py` is a hand-rolled third copy of the mining
splitmix64 family and its own docstring names itself a "promotion candidate";
#150 built the shared seam but scoped itself to mining. Fold `fishing_seed`
onto `shared.rng.mix64`/`cell_seed` (keeping the fishing salt) with byte-identical
outputs pinned. Effort: S. Risk: ⚠️ behaviour-preserving refactor, byte-hash
pin makes regressions loud; trivial revert. Unblocks: retires copy #3, leaves
only exploration's divergent family outside the seam.

**A2 — Cross-family RNG tripwire test.**
Pitch: the two mining `_cell_seed` copies were kept aligned "by comment" only
(no test asserted equality — flagged in #150's session card). Add a
`tests/shared/` grep-pin that any in-repo seam claiming the mining family (the
`0x9E3779B97F4A7C15` + `<<6 … >>2` shape) routes through `shared.rng.mix64`
rather than re-inlining it. Effort: S. Risk: ↩️ test-only, additive. Unblocks:
makes A1 (and any future copy) reds-by-construction if it drifts.

**A3 — Document/label the two splitmix64 families explicitly.**
Pitch: the repo has TWO distinct "splitmix64" algorithms — the mining family
(`shared/rng.py`, `<<6…>>2`) and exploration's canonical `0xBF58476D…`
finaliser (`games/exploration/quest/rng.py`). They share a name and gamma but
are different algorithms; a future migrator could wrongly "unify" them. Add a
short `docs/design/shared-index.md` note + module cross-references pinning that
they are intentionally separate. Effort: S. Risk: ↩️ docs-only. Unblocks:
prevents a determinism-breaking "cleanup" of exploration's RNG.

**A4 — Promote a shared child-RNG derivation helper.**
Pitch: `shared/rng.py` gives `mix64`/`cell_seed` but not the "derive a child
stream from a parent seed" pattern that the grid-encounters slice and the
exploration engine both need. Add a documented `derive(seed, *tags)` on the
shared module so future plugins get the whole determinism kit, not just the mix
step. Effort: S. Risk: ↩️ additive API. Unblocks: one audited source for
child-stream derivation across games.

**A5 — Consolidate the four balance-sim harnesses behind one runner protocol.**
Pitch: `games/*/sim/*_sim.py` + `games/shared/sim/economy_sim.py` each
re-implement `run(**kw) → report` + `format_report`; the smoke registry (#119)
already treats them uniformly by glob. Formalise a tiny `SimHarness` protocol
(like the encounter/inventory seams) so a harness is discovered structurally,
not by naming convention. Effort: M. Risk: ⚠️ refactor across 5 sims, golden
render transcripts pin output. Unblocks: uniform sim tooling, easier to add a
new game's sim.

**A6 — Extract the shared inventory reference into a conformance-tested base.**
Pitch: `games/shared/inventory/` already has interface + reference +
conformance, but fishing carries its own `inventory/adapter.py`. Audit whether
the fishing adapter can consume the shared conformance suite so every game's
inventory is proven against one contract. Effort: M. Risk: ⚠️ touches fishing
inventory behaviour; conformance suite guards it. Unblocks: single inventory
contract ahead of the persistence build.

**A7 — Unify the four `services/*_workflow.py` audited seams on a shared base.**
Pitch: mining/fishing/dnd/exploration each hand-roll the same
`Sink`+`AuditRecord` wiring around their state machine (`services/audit.py` is
shared, the wiring is not). A `WorkflowSeam` base could single-source the audit
plumbing so a new game's seam is a subclass, not a copy. Effort: M. Risk: ⚠️
refactors all four seams; driver-parity + workflow tests pin behaviour.
Unblocks: cheaper 5th game, consistent audit semantics.

**A8 — Kill the `services → games` import-direction ambiguity with a checked rule.**
Pitch: the hub deliberately avoids a `services → games` edge (opener-as-opaque
callable, #72). Nothing enforces it — a future PR could add the edge silently.
Add an import-linter/AST test pinning the dependency direction. Effort: S.
Risk: ↩️ test-only. Unblocks: keeps the plugin-boundary architecture honest.

**A9 — Shared "step function" typing/protocol.**
Pitch: #134 unified the per-game step-closure into `make_step_fn` factories but
each game still types its own. A shared `StepFn` protocol + a single parity
harness would let the driver-parity tests (12 today) derive their game list
instead of enumerating it. Effort: S. Risk: ↩️ typing/test refactor. Unblocks:
new games auto-join driver-parity coverage.

---

## B. Gameplay & content

**B1 — Wire the fishing full-roster economy on sim-verdict receipt.**
Pitch: fishing ships only 4 species (minnow/bass/pike/legend_carp) vs the
original's ~21; the full-roster + cook-leg SIM-REQUEST is routed to sim-lab
(ORDER 008/009). On verdict, wire the 29 species' sell/XP values VERBATIM into
`games/fishing/core/{species,economy}.py`. Effort: M (mechanical once numbers
land). Risk: ⚠️ economy change, but data-only + regenerated balance page pins
it; externally gated (do not invent numbers). Unblocks: the headline
production-grade fishing target (ORDER 008).

**B2 — Wire the fishing cook leg.**
Pitch: sell-OR-cook exclusivity is already structural (#83 haul-debit) but the
cook branch has NO pinned constants (cooked-value + energy-restore await the
`fishing-cook-economy` SIM-REQUEST). On verdict, wire cook alongside sell.
Watch VERDICT 042's FAUCET-BYPASS flag on any energy-restore number. Effort: M.
Risk: ⚠️ new economy path, sim-gated + balance-pinned. Unblocks: fishing's
second economy leg, closes the last standalone-fishing gap.

**B3 — Standalone-CLI save/load for mining + fishing.**
Pitch: "a game you cannot save is thin" (outbox OWNER-QUEUE). State
dataclasses are already cleanly JSON-serializable; the build is mechanical
ONCE the persistence format-governance decision lands (§F/owner). Effort: M.
Risk: 🔒 owner-gated on format-governance + D2; reversible code once decided.
Unblocks: the last standalone-polish item for both CLIs.

**B4 — Land the D&D bounded-authority ship-gate and P4 scaffolding.**
Pitch: `docs/planning/dnd-story-game-plan.md` ends at a ⚑ needs-owner gate
(Story-Actions-only, engine owns amounts). Approval unblocks the `dungeon_master`
profile/toolset over the already-built deterministic engine. Effort: L
(design-gated, then multi-slice). Risk: 🔒 the AI layer is the biggest
invention gap; posture is maximally conservative (worst case = a legal capped
outcome). Unblocks: the one genuinely undesigned pillar (buildability map §8).

**B5 — Import exploration reward bands when the upstream artifact lands.**
Pitch: V045 ratified exploration's reward placeholders with an honest NULL; the
real numeric bands wait on superbot's P0 survival balance-sim artifact
(Q-0087/D-0008). Reopen and import verbatim on arrival. Effort: S. Risk: ⚠️
data-only, externally gated. Unblocks: removes the last invented-placeholder
economy in the fleet.

**B6 — Data-drive the remaining hardcoded player-facing nouns (theme readiness).**
Pitch: the theme-slot-readiness audit (`docs/audit/theme-slot-readiness-2026-07-11.md`)
mapped where nouns live in DATA vs hardcoded in CODE with a remediation
roadmap. Execute the roadmap so a game can be re-themed by editing data, not
code. Effort: M. Risk: ⚠️ moves literals to data; display-completeness registry
(#123) guards coverage. Unblocks: re-skinnable games, cheaper content.

**B7 — Mining tool-ladder feltness pass (VERDICT 042 flag).**
Pitch: VERDICT 042 flagged that pickaxe (×1.13) and iron pickaxe (×1.25) are
amount-INERT under `BASE_ROLL_MAX=2 + round()` — the bottom tiers don't pay.
Decide sim-first whether to make them felt. Effort: S (sim), M (if numbers
change). Risk: ⚠️ economy tuning, sim-gated. Unblocks: closes a known
player-feel dead spot.

**B8 — Mining faucet-bypass pricing decision (VERDICT 042 flag / PROPOSAL 035).**
Pitch: rations (20 coins → 25 energy) and energy drinks (40 → 50) price energy
below the faucet at every depth — a booster bypass. Decide sim-first whether
intended (already in flight as idea-engine PROPOSAL 035). Effort: S–M. Risk: ⚠️
economy, sim-gated. Unblocks: resolves a standing economy-integrity flag.

**B9 — A fifth game over the existing hub + seams.**
Pitch: the hub is a game-neutral world registry (#72) and the WORKFLOW/audit
seams are shared; a new small game (e.g. farming/crafting/trading) would prove
the plugin boundary generalises beyond the current four. Effort: L. Risk: ⚠️
net-new surface, but built on proven seams. Unblocks: validates the
"game-neutral" claim with a real second-order consumer.

**B10 — D&D richer scene graph / content expansion.**
Pitch: dnd is a bounded-menu story engine with a small scene catalog; the
reachability (#126) and effects-liveness (#129) tripwires mean new scenes come
with structural guarantees. Add more authored scenes/branches within the
existing caps. Effort: M. Risk: ↩️ data-additive, tripwires pin correctness.
Unblocks: more playable depth without touching the engine.

**B11 — Exploration survival-sim depth (the queued P2 harness).**
Pitch: the superseded wind-down snapshot names "P2 survival sim harness on the
D-0004 option-(a) baseline" as the exploration next-default. The survival sim
scaffolding exists (`games/exploration/survival/`); grow it toward the P2
target. Effort: M. Risk: ⚠️ sim/balance change, balance-pin sim guards.
Unblocks: exploration's next design pillar.

**B12 — Player-facing "economy readout" parity across all four games.**
Pitch: fishing surfaces a V043 economy readout via CLI `sell` + a generated
`balance.md` section (#87); mining/dnd/exploration don't have the same
player-visible economy surface. Add parity readouts routed through each audited
seam. Effort: M. Risk: ↩️ additive read-only surface. Unblocks: consistent
player economy transparency, easier balance verification.

---

## C. Testing & CI

**C1 — Land the mirror/reconcile-race fix (#149).**
Pitch: the `claude/mirror-reconcile-race-fix` branch exists with a completed
card (`df0eef9`) but isn't on main — the reconcile race it addresses is still
live. Re-verify and land it. Effort: S–M. Risk: ⚠️ CI-plumbing change; verify
against the arm→disarm window semantics. Unblocks: closes a known CI race.

**C2 — Preflight-scripts existence tripwire (#143's own unbuilt 💡).**
Pitch: #143 planted `scripts/preflight.py` so `check --strict` stops silently
skipping its preflight leg, and its OWN session idea — a `tests/tools` pin that
every `preflight_scripts` config token EXISTS as a file — is still unbuilt
(grep confirms empty at HEAD). Build it. Effort: S. Risk: ↩️ test-only.
Unblocks: the silent-skip class #143 named gets a tripwire.

**C3 — Assert `services → games` non-import in CI (pairs with A8).**
Pitch: same rule as A8, expressed as a gate step so the architecture boundary
is enforced on every PR, not just discoverable by reading. Effort: S. Risk: ↩️
test/CI-only. Unblocks: boundary can't regress silently.

**C4 — Coverage floor / ratchet gate for `games/` + `services/`.**
Pitch: coverage is ~97% (measured at #120) but nothing GATES it — a PR can drop
coverage silently. Add a coverage-floor step to the tests workflow with the
floor in one obvious place (mirrors the ORDER 001 collected-count-floor
discipline). Effort: S–M. Risk: ↩️ CI-only, additive. Unblocks: coverage
becomes a red gate, not a groom-time measurement.

**C5 — Property/fuzz sweep for the remaining resolver seams.**
Pitch: the dnd resolver got a DM-clamp property fuzzer (#52) that surfaced the
#115 unhashable-`option_id` bug. The fishing/exploration/mining workflow
resolvers have no equivalent adversarial input sweep. Add one per seam. Effort:
M. Risk: ↩️ test-only, may surface latent bugs (that's the point). Unblocks:
hardening parity across all four seams.

**C6 — Determinism subprocess-check for every RNG seam (not just mining grid).**
Pitch: only the mining grid unit-tests process-independence via a subprocess
check; fishing and exploration RNGs claim the same property but don't pin it
cross-process. Add a shared subprocess determinism test parametrised over every
seam. Effort: S. Risk: ↩️ test-only. Unblocks: the "subprocess-stable" claim is
proven everywhere, not asserted.

**C7 — Balance-doc freshness as a hard cross-check on ALL generated sections.**
Pitch: `docs/balance.md` is generated (`tools/gen_balance.py`) and freshness is
checked, but the check is only as complete as its section list. Add a
completeness pin that every economy source module has a corresponding generated
section (so a new game's economy can't dodge the balance page). Effort: S.
Risk: ↩️ test-only. Unblocks: no silent balance-doc drift when a game is added.

**C8 — Golden-transcript coverage for the hub + every standalone `main()`.**
Pitch: driver-parity (#134) pins scripted-driver stdout byte-for-byte, and the
REPL seam (#127) is shared, but the interactive `main()` banner/quit/EOF paths
are only spot-covered. Extend the fixed-seed transcript set to every entrypoint
pair. Effort: S–M. Risk: ↩️ test-only. Unblocks: player-visible output changes
red loudly.

**C9 — CI matrix across supported Python versions.**
Pitch: the code is stdlib-only and claims "Python ≥ 3.10" but CI runs one
interpreter. A small version matrix (3.10/3.11/3.12/3.13) would catch
stdlib-behaviour drift. Effort: S. Risk: ↩️ CI-only. Unblocks: the ≥3.10 claim
is tested, not asserted.

**C10 — Mutation-testing spot check on the tripwire registries.**
Pitch: the detector-trip registry (#122) already proves each invariant
predicate can return False, but the broader suite has no mutation signal. A
scoped `mutmut`/`cosmic-ray` run on the economy/resolver cores would measure
whether tests actually catch regressions. Effort: M. Risk: ↩️ analysis-only,
no shipped behaviour. Unblocks: evidence for where coverage is shallow.

---

## D. Tooling & infra

**D1 — Sweep the ~85 stale `claude/*` remote branches.**
Pitch: `git ls-remote` shows ~85 merged/abandoned `claude/*` branches
(claim-order-007, dnd-finalization, kit-upgrade-*, night-coverage-*, …), all
long-since squash-merged. They clutter branch pickers and the automerge branch
allowlist scope. Owner deletes by hand OR enables "Automatically delete head
branches" (branch deletion is a verified 403 wall for sessions — CAPABILITIES).
Effort: S (owner click) / M (enumerate + verify merged first). Risk: ⚠️ verify
each is merged before proposing deletion; deletion itself is owner-only.
Unblocks: a clean branch namespace, smaller allowlist surface.

**D2 — Enable "Automatically delete head branches" repo setting.**
Pitch: the root cause of D1's accumulation — merged PR branches are never
reaped because session-side deletion 403s. One repo-settings toggle fixes it
going forward. Effort: S (owner click). Risk: 🔒 owner-gated repo setting, ↩️
reversible toggle. Unblocks: stops the stale-branch pile from re-growing.

**D3 — `stamp_scaffold.py` → full truth-stamp autopilot.**
Pitch: `tools/stamp_scaffold.py` emits "Recently shipped" bullet skeletons from
`git log <anchor>..HEAD` (authoring aid, not a gate). Grow it to also flag the
ledger's KNOWN drift (e.g. it still describes #102 as an open PR though it
merged — noted in the EAP walkthrough handoff). Effort: M. Risk: ↩️ tooling +
docs. Unblocks: cheaper, less-error-prone ledger grooms.

**D4 — Ledger-drift CI check (the advisory KIT-ASK, built locally).**
Pitch: the outbox carries an advisory-only lane→manager KIT-ASK for a
mechanical ledger-drift check comparing `current-state.md`'s highest cited PR
against main's squash subjects. Build it as a local non-blocking tool now.
Effort: S. Risk: ↩️ advisory tooling, never merge-blocking. Unblocks: drift is
surfaced automatically instead of caught by eye.

**D5 — `bootstrap claim` ergonomics / claim-staleness sweep.**
Pitch: claims are one-file-per-claim (measured 0% conflict) but nothing prunes
stale claim files whose branch already merged (e.g. residual claims in
`control/claims/`). A `bootstrap claim --sweep` that lists claims whose branch
is merged would keep the ledger honest. Effort: S. Risk: ↩️ tooling, read-only
suggestion. Unblocks: claim ledger stays a live signal, not a graveyard.

**D6 — Session-card scaffolder that pre-fills the `📊 Model:` line + status.**
Pitch: ORDER 003 requires every card carry a family-level `📊 Model:` line and
the walkthrough notes historical cards nag the `[model-line-*]` check. A
scaffolder that stamps the correct card skeleton (status, model line,
task-class) would stop the recurring hygiene misses. Effort: S–M. Risk: ↩️
tooling. Unblocks: consistent, gate-clean cards by construction.

**D7 — One-command "new game" scaffold.**
Pitch: adding a game today means hand-copying the CLI/`__main__`/core/sim/tests
layout + registering the suite floor + hub entry. A `tools/new_game.py`
scaffold would encode the whole convention. Effort: M. Risk: ↩️ tooling.
Unblocks: cheap 5th/6th game (pairs with B9).

**D8 — Promote `automerge card guard` into a kit knob (the standing KIT-ASK).**
Pitch: the host-owned `automerge-card-guard.yml` reconciler (#142) is a manual
relocation the outbox already asked to become a kit-sanctioned config knob so
future kit regens don't clobber it. Pursue upstream / config-ise it. Effort: M.
Risk: ⚠️ CI-plumbing; touches the merge-safety window. Unblocks: no re-apply
duty on kit upgrades.

**D9 — Pin the kit version + a regen-diff check.**
Pitch: kit upgrades (#141/#144) have twice motivated host-file clobber fixes. A
CI step that regenerates kit-owned files and diffs them against committed (fail
if a host edit crept into a kit-owned file) would catch the clobber class
early. Effort: M. Risk: ↩️ CI-only. Unblocks: kit upgrades stop being a
manual-restore hazard.

---

## E. Docs & records

**E1 — Truth-stamp groom of `current-state.md`.**
Pitch: the ledger's "In flight" still describes #102 as an open PR (it merged
`1c323c1`, 2026-07-14) and predates #150; the EAP walkthrough handoff item 5
explicitly flags this. Re-stamp with `stamp_scaffold.py` from the #135 anchor.
Effort: S. Risk: ↩️ docs-only. Unblocks: the living ledger matches main again.

**E2 — Flip the RNG-seam idea to `shipped` when #150 merges.**
Pitch: `docs/ideas/shared-deterministic-rng-seam-2026-07-10.md` is `promoted`
with null ship fields "until the PR merges — the merge flips them to
`outcome: shipped`". #150 is at HEAD; flip the frontmatter (shipped_pr/repo/
merged_date) per the backlog's convention. Effort: S. Risk: ↩️ docs-only.
Unblocks: the ideas conveyor scores correctly (it's "a conveyor, not a
graveyard").

**E3 — Capture NEW ideas into `docs/ideas/` from this menu.**
Pitch: the ideas backlog has exactly ONE captured idea (the RNG seam, now
shipped). This menu surfaces dozens; the highest-value ones should become
proper captured idea files with frontmatter so they live in the repo, not just
this doc. Effort: M. Risk: ↩️ docs-only. Unblocks: a real, scored backlog
instead of an empty conveyor.

**E4 — Record the EAP-extension acknowledgment (ORDER 010).**
Pitch: ORDER 010 (EAP extended to 2026-07-21) is `done-when: seat acknowledges
on its first rebooted wake`; `control/claims/claude-eap-ack.md` exists but the
status ack should be confirmed present. Close the loop. Effort: S. Risk: ↩️
control-doc only. Unblocks: the dormancy record stops reading as current.

**E5 — Fold the four EAP owner-decision items into a single live decision log.**
Pitch: the OWNER ACTIONS checklist (D2 ratify · rung-3 packaging · persistence
governance · transfer-policy) is spread across outbox + two design docs.
`docs/decisions.md` exists; consolidate the open decisions there with deep
links + recommendations so the owner has ONE queue. Effort: S. Risk: ↩️
docs-only. Unblocks: one place for the owner to clear the backlog.

**E6 — Author `docs/PLATFORM-LIMITS.md` (referenced, missing).**
Pitch: the task brief and orientation reference a platform-limits doc; it does
NOT exist in the repo. The CAPABILITIES walls section (tag-push 403, branch
deletion 403, api.github.com blocked, GraphQL quota) is the raw material. Give
it a home. Effort: S. Risk: ↩️ docs-only. Unblocks: a durable, discoverable
limits reference separate from the capabilities ledger.

**E7 — Append fresh CAPABILITIES findings from the current outage.**
Pitch: `docs/CAPABILITIES.md`'s append log is empty below the kit fence, and
today's GitHub REST 503 outage (git works, MCP PR ops fail) is exactly the kind
of venue-scoped finding the discovery rule wants recorded. Log it. Effort: S.
Risk: ↩️ docs-only. Unblocks: the next session pre-routes around the outage
class instead of rediscovering it.

**E8 — Prune / archive the superseded wind-down snapshot in `current-state.md`.**
Pitch: the ledger still carries a 2026-07-09 wind-down snapshot marked
"superseded" but kept "for provenance" — it's long, stale, and duplicates git
history. Move it to a dated archive doc and leave a one-line pointer. Effort: S.
Risk: ↩️ docs-only, provenance preserved. Unblocks: a shorter, current ledger.

**E9 — A "how to add a game" contributor doc.**
Pitch: the plugin boundary, audited-seam convention, hub registration, and
suite-floor registry are all documented separately; a single walkthrough
(pairs with the D7 scaffold) would encode the path end-to-end. Effort: M. Risk:
↩️ docs-only. Unblocks: onboard a new game (or new seat) faster.

---

## F. Owner-decision unblocks (decide-and-flag queue)

_These are ⚑ needs-owner gates — no session can clear them. Listed so the owner
can clear several in one pass; each already carries a bolded recommendation in
its source doc. Effort here is the OWNER's click; the build effort is in §A–B._

**F1 — Ratify D2 (audit item-grants).**
Pitch: the rung-2 seam audits every state-changing action INCLUDING item grants
(a deliberate divergence from the oracle); the ⚑ ratification is pending in
`control/outbox.md` § DECISION-NOTE D1/D2. Recommendation in-doc: **ratify as
built** (reversal is a one-line toggle). Effort: S (reply "D2 ratified").
Risk: 🔒→↩️ owner-gated, reversible. Unblocks: rung-3 packaging + persistence.

**F2 — Approve rung-3 packaging + hermeticity.**
Pitch: making sbg an installable distribution importing `sb.spec` from
superbot-next is `partially buildable`, gated on a ⚑ packaging/hermeticity
decision (`docs/design/mining-host-adapter.md` § ⚑). In-doc rec: **approve,
sequenced after D2** (the rung-2 op it waited on now exists). Effort: S (reply).
Risk: 🔒 owner-gated. Unblocks: the host-adapter build (rung 3).

**F3 — Decide persistence format-governance.**
Pitch: contract-impl vs flat-local · namespace mapping · load-vs-audit rule
(`control/outbox.md` § OWNER-QUEUE, landed #73). In-doc rec: **contract-impl
per PR #53 · per-game namespaces · load emits no audit rows**. Effort: S (reply
3 picks). Risk: 🔒 owner-gated. Unblocks: save/load (B3) becomes mechanical.

**F4 — Decide transfer-policy source model.**
Pitch: `docs/design/persistence-design.md` §5 item 4 — true source-debit vs
seeded-credit. In-doc rec: **TRUE source-debit** (seeded-credit violates the
doc's own conservation invariant). Effort: S (reply choice). Risk: 🔒
owner-gated. Unblocks: item-transfer persistence.

**F5 — Approve the D&D bounded-authority ship-gate.**
Pitch: the Q-0040 posture at the foot of `dnd-story-game-plan.md` —
"Story Actions are the sole AI-emitted component; the engine owns all amounts
and state; every menu is hard-capped in code." In-doc rec: **APPROVE**
(substrate is built + sim-pinned; worst case = a legal capped outcome).
Effort: S (reply). Risk: 🔒 owner-gated. Unblocks: D&D P3 → P4 (B4).

**F6 — Per-seat routine re-arm go (post-EAP-extension).**
Pitch: ORDER 010 holds routines UN-armed pending the owner's per-project reboot
review (the v3.6 reboot prompt IS the go). Until the owner gives the per-seat
go, the wake routine (ORDER 002) stays un-armed. Effort: S (owner go). Risk: 🔒
owner-gated. Unblocks: autonomous wake cadence resumes.

---

## G. Housekeeping / small wins

**G1 — Delete merged claim files still in `control/claims/`.**
Pitch: `claude-shared-rng-seam.md` rides #150's branch and is deleted at session
close per the README; verify no other merged-work claims linger. Effort: S.
Risk: ↩️ control-doc only. Unblocks: claims dir reflects only live work.

**G2 — Add a PR template.**
Pitch: there is NO `.github/PULL_REQUEST_TEMPLATE` — PR bodies are hand-shaped
each time (evidence/claim-plus-evidence discipline is convention, not
scaffolded). A template encoding the claim/evidence/verify sections would make
the discipline default. Effort: S. Risk: ↩️ additive. Unblocks: consistent,
evidence-carrying PR bodies.

**G3 — Consolidate the two `preflight.py` copies' relationship in a comment.**
Pitch: `scripts/preflight.py` (kit-conventional wrapper) delegates to
`tools/preflight.py` (#143); the split is load-bearing but only explained in the
ledger. A one-line header cross-reference in each file would make the
delegation self-documenting. Effort: S. Risk: ↩️ comment-only. Unblocks:
future sessions don't mistake one for dead code.

**G4 — Retire the `# pragma: no cover` on `services/audit.py`'s protocol stub.**
Pitch: `AuditRecord.record` is a Protocol method marked no-cover; if any
concrete Sink's `record` is under-tested, the pragma could mask it. Audit
whether the pragma is still the narrowest correct scope. Effort: S. Risk: ↩️
test/coverage-only. Unblocks: confirms the coverage number isn't papering over
the audit sink.

**G5 — Add a top-level `make`/`just` task file mirroring the CI gates.**
Pitch: the verify commands (`tools/preflight.py`, `pytest -q`, `bootstrap.py
check --strict`) are documented in the EAP walkthrough but not one-command. A
`justfile`/`Makefile` would make local gate-parity a single verb. Effort: S.
Risk: ↩️ additive. Unblocks: lower-friction local verification.

---

## Category breakdown

- **A. Engine / shared code:** A1–A9 (9)
- **B. Gameplay & content:** B1–B12 (12)
- **C. Testing & CI:** C1–C10 (10)
- **D. Tooling & infra:** D1–D9 (9)
- **E. Docs & records:** E1–E9 (9)
- **F. Owner-decision unblocks:** F1–F6 (6)
- **G. Housekeeping / small wins:** G1–G5 (5)

**Total: 60 proposals.** Un-filtered by design — the owner triages tomorrow.
