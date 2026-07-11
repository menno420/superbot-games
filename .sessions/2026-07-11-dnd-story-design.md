# 2026-07-11 · D&D story game design (bounded-menu AI DM)

> **Status:** `complete`
>
> 📊 Model: Claude Opus · 2026-07-11T01:55:35Z · D&D story game design (bounded-menu AI DM)

## Goal

Author the engineering design doc for the **AI Dungeon Master story game** as a
pure-domain **plugin package** for superbot-next — the last unstarted domain of the
world seat. Docs-only: `docs/design/dnd-story-design.md` + a `docs/design/dnd-index.md`
read-path index + one link line in `docs/current-state.md`. The doc must be grounded in
the shipped code (cite the exploration quest engine seams it reuses) and pin the
**bounded-menu law** (Q-0040 / D-0007) concretely: the menu schema, what the DM sees,
what it returns, the validate→clamp-to-no-op enforcement point, determinism & sim-pinning,
and a worked example. First code PR is a one-scene walking skeleton (named, not built).

## What shipped

- **`docs/design/dnd-story-design.md`** (`reference`) — the design: package shape mirroring
  mining/fishing (`games/story/` core/data/sim/workflow + host-adapter seam); the exact
  reused engine seams (`rng.py:52` `DetRng` / `:36` `derive_seed`, `engine.py` offer/accept/
  apply_event/grant_rewards, `predicates.py` `GameEvent`/`evaluate`, `catalog.py` `TIER_CAPS`/
  `GLOBAL_MAX`, `leverage.py:16` `menu_width`); the bounded-menu contract with dataclass
  shapes (`Scene`/`MenuOption`/`DMChoice`), the DM I/O payloads, the `resolve()` clamp core,
  a worked scene + resolution table; theme-readiness (Q-0267); the walking-skeleton file list
  + tests; the P-queue; the integrity checklist.
- **`docs/design/dnd-index.md`** (`reference`) — read-path index (design + plan + substrate).
- **`docs/current-state.md`** — one added bullet linking `dnd-index.md` (trivial rebase vs #34).

## 💡 Session idea

The bounded-menu law reads as an AI-safety abstraction, but the shipped
`games/exploration/quest/**` already *is* its reference implementation one level down —
`catalog.menu()` hands the DM a list of `template_id` **keys** (never bundles),
`grant_rewards` clamps every amount to `TIER_CAPS`, and `leverage.menu_width` caps option
*count* in code. So the story-game contract isn't a new invention to defend; it's the same
"pick a pre-approved id, code owns the amount" pattern lifted from quest-selection up to
scene-selection. Writing the design as "the menu law, one level up" (with `resolver.resolve`
as the single clamp choke-point that mirrors `grant_rewards`' cap choke-point) makes the
whole surface auditable by analogy to code that already exists and is sim-pinned — the
model's worst case stays "a legal capped outcome, or a deterministic no-op."

## ⟲ Previous-session review

This previous-session review builds directly on the exploration lane's shipped substrate:
the quest/encounter engine (PR-series, 48 tests incl. the balance-pin sim) and the
existing plan/spec `docs/planning/dnd-story-game-plan.md` (Q-0040 posture, session
lifecycle, persistence, budget, the ⚑ ship-gate). This design is the *engineering*
companion the plan pointed at but did not contain — the package shape, the concrete
bounded-menu dataclasses, the clamp rule, and the walking-skeleton cut. It mirrors the
fishing walking-skeleton design (`docs/design/fishing-catch-skeleton.md`, PR #25) as its
structural template and adopts the theme-readiness pattern proven three times in-repo
(`grid.py` `_STRIKE_NOTE`, `encounters.py` `_NARRATION`, `fishing/species.py`). No code,
tests, workflows, or control/status touched — docs-only, reachable through `dnd-index.md`.

## Old-superbot oracle

Best-effort porting oracle checked via the public raw path: `cogs/adventure.py`,
`cogs/story.py`, `cogs/dnd.py`, `cogs/dungeon.py` on `menno420/superbot@main` all return
**HTTP 404** — no story/DM module is present/reachable in old superbot. The design is
therefore grounded entirely in the shipped `superbot-games` engine, not a port.
