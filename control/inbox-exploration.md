# control/inbox-exploration.md — orders to game-exploration

> **ONE writer: the manager.** Never edit this file. Report order progress ONLY in
> `control/status-exploration.md` (one writer per file — protocol: `control/README.md`).

## ORDER 001 · 2026-07-09T14:23Z · status: new
priority: P1
do: (1) Verify substrate-kit adoption (`check --strict` green) — adopt from
`menno420/substrate-kit` per its README ONLY if mining hasn't already done it; coordinate
via the docs/lanes.md once-only rule. (2) Read `docs/founding-plan-exploration.md` +
`docs/lanes.md` — both binding. (3) Correct your seeded `control/status-exploration.md`.
(4) Begin roadmap P0→P1: write the design docs for the quest/encounter engine (world
model, engine spec, shared-engine seam), then build the deterministic engine core with
sim tests.
why: founding order — stand the exploration Project up on its lane.
done-when: status-exploration.md reports acked=001 and the engine design doc + the first
engine PR merged.

## ORDER 002 · 2026-07-09T14:34Z · status: new
priority: P1
do: Read docs/research/buildability-map-exploration.md (reference, verify against sources). Your P1 work order, decided-and-flagged: (1) FIRST BUILD = the deterministic quest/encounter engine (Lane C shape: quest_service + EventBus-predicate progress, engine-not-content) with the v1 bounded-menu catalog = five templates × 3 reward tiers × Q-0087-band caps — this catalog is the substrate the AI DM later picks from; (2) WRITE the D&D story-game plan doc — the map's decision-1 defaults are the manager's recommendation (Story Actions as the only AI-emitted component, thread-per-session on versioned JSONB summaries, no stakes v1, single-player v1, world character = story character) — this plan doc closes the Q-0040 ship-gate and routes its bounded-authority decision to the owner via ⚑ needs-owner when drafted; (3) re-baseline the survival D1 contract against shipped universal energy before building the sim harness; (4) design message-XP→DM-leverage inside the D&D plan as a deterministic code-side menu-widening modifier, capped, never model-decided. Wild encounters (Q-0186) stay with their existing greenlight — coordinate via the shared engine interface in games/shared/ (claim-first per lanes.md).
why: the domain is design-heavy; this sequences invention before construction, engine before dice.
done-when: status-exploration.md acks 002; the quest-engine design doc + D&D plan draft exist with ⚑ flags for the owner's bounded-authority sign-off.
