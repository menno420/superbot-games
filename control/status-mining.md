# game-mining · status
updated: 2026-07-09T19:30Z
phase: P0→P1 — pure domain ported (PR #5); grid-encounters first slice built on top (PR #11). Next: workflow seam + host adapter.
health: green — main is strict-GREEN and enforces the substrate-gate CI workflow (installed via exploration #8); both open mining PRs are mergeable_state clean with substrate-gate green.
kit: substrate-kit v1.2.0 — adopted on main by exploration's PR #3 (merged); mining CONSUMES it (the "adopt once" rule). Mining's own adoption PR #4 was CLOSED as redundant.
last-shipped: nothing merged yet from the mining lane (port on PR #5, retro on PR #9 — both awaiting owner merge). Exploration #3/#8 merged the shared kit + CI to main.
orders: acked=001,002,004 done=001 (port + design shipped to PR),004 (retro shipped to PR)

⚑ needs-owner:
- MERGE PR #5 and PR #9 — the agent cannot self-merge (auto-mode self-approval guardrail;
  verbatim denials are in docs/retro/project-review-2026-07-09-mining.md). Click-by-click:
  open each PR → Squash & merge → Confirm. Order doesn't matter now — both are based on main,
  independent, and their control/status-mining.md is byte-identical so the second merge
  auto-resolves. Alternatively, authorize the merges directly in the mining session chat.
- Aggregate control/status.md two-writer risk — the kit hardcodes a single control/status.md,
  but this repo's per-lane model needs a kit-side fix. Owner call: take the upstream
  substrate-kit fix or formalize the aggregate as manager-written.

blockers: only the self-approval merge guardrail — the agent cannot merge/arm/mark-ready its
own session PRs. Both PRs are otherwise ready (clean + CI green); merging is a one-click owner
action (or an in-chat authorization).

pr-in-flight:
- #4 mining/adopt-substrate-kit — CLOSED as redundant (kit already on main via exploration #3; "adopt once").
- #5 mining/port-pure-domain — OPEN, DRAFT, mergeable_state clean, substrate-gate CI green (head d41a849). Based on main. 18 modules → games/mining/core/, 62 tests pass; docs/design/mining-plugin-layout.md. Awaiting OWNER merge (self-approval guardrail).
- #9 mining/retro-2026-07-09 — OPEN, READY, mergeable_state clean, substrate-gate CI green (head 1d58d08). Based on main. Retro/self-review docs. Awaiting OWNER merge.
- #11 mining/grid-encounters — OPEN, DRAFT, STACKED ON #5 (base mining/port-pure-domain; retarget to main after #5 merges). Grid-encounters extension first slice, PURE DOMAIN: games/mining/core/encounters.py (feature-keyed live-rollable encounter resolver over the seeded grid) + games/mining/sim/encounters_sim.py + tests/mining/test_encounters.py. 73 tests pass (62+11). All NEW balance numbers sim-pinned (~11.6% encounter rate; depth×gear danger gradient; no pay-to-win) — evidence in docs/design/mining-grid-encounters.md §5. Do NOT auto-merge/arm/mark-ready (owner-gated). Awaiting #5 merge then retarget.

self-initiated (flagged): #4 closed as redundant (kit already on main via #3); #5 merged main
forward taking main's kit files (forward-only, no rebase); one additive reason-carrying
.substrate/check-exceptions.yml allowlist entry (D-0042/D-0043 cross-repo triage, mirrors
exploration) to stay drift-neutral strict-green; equipment.py placed in games/mining/core/
(promotion candidate for games/shared/ when a 2nd game ports); optional injectable rng threaded
through the reward rolls (byte-identical to the oracle path). #11 grid-encounters (self-initiated
build per the named-first extension): deterministic-by-default rng reconciled with §7's live-roll
intent via injectable rng; feature-keyed archetypes (one kind per CellFeature); single-exchange
combat now (multi-turn deferred); hard depth-gate + cooldown deferred to the workflow layer
(stateful, not pure); all encounter constants are NEW sim-pinned design (first core module whose
numbers originate locally, not oracle-ported); games/mining/sim/ created as the sim-harness home.

notes: docs/founding-plan-mining.md + docs/lanes.md are binding. Retro answers:
docs/retro/self-review-mining-2026-07-09.md; wake-up review: docs/retro/project-review-2026-07-09-mining.md.
Next (no owner needed): games/mining/workflow audited-op seam → Layer-3 superbot-next
SubsystemManifest host adapter (read the contract first) → grid-encounters extension → economy
sim + parity goldens.
