# D&D story game — design index

> **Status:** `reference` · lane: game-exploration · 2026-07-11
>
> Read-path index for the AI Dungeon Master story game. One hop from
> `docs/current-state.md` into the story game's design + plan set, so every doc below
> stays reachable (bootstrap `check --strict` BFS) through a single trivially-rebasing
> link.

## Designs

- [`dnd-story-design.md`](dnd-story-design.md) — the engineering design: the story game
  as a pure-domain **plugin package** (mirrors mining/fishing), the exploration-engine
  seams it **reuses** (`games/exploration/quest/**`), and the **bounded-menu contract**
  specified concretely (menu schema · what the DM sees/returns · the validate→clamp-to-
  no-op enforcement point · determinism & sim-pinning · a worked example). The first
  code PR is a one-scene walking skeleton.

## Plan / spec

- [`../planning/dnd-story-game-plan.md`](../planning/dnd-story-game-plan.md) — the
  plan/spec: the Q-0040 bounded-authority posture, session lifecycle state machine, menu
  taxonomy, versioned-JSONB persistence, budget/degrade, the `dungeon_master` AI seam,
  and the ⚑ needs-owner ship-gate.

## Substrate it builds on

- [`quest-encounter-engine.md`](quest-encounter-engine.md) — the shipped, sim-pinned
  deterministic quest/encounter engine (`games/exploration/quest/**`) the story game
  extends rather than duplicates.
