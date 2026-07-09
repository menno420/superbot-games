# game-exploration — founding plan

> **Status:** `plan` — founding brief, manager-seeded 2026-07-09

## Mission

Own the **federated exploration world** and the **D&D story game**: one world, one
character, one economy — where each subsystem still feels like its own complete game —
plus the AI-Dungeon-Master story layer, built on a deterministic quest/encounter engine
that owns every outcome the AI narrates.

## The work

### 1. Federated-world doctrine (owner framing — the direction)

The owner's world model (superbot `docs/ideas/explore-hub-federated-world-2026-06-19.md`):
each subsystem (mining, fishing, exploration…) **feels like its own game but shares one
world, one character, one economy**. Three XP tracks, each with a distinct job:

| Track | Earned by | Job |
|---|---|---|
| **Message XP** | chatting | **negotiation leverage vs. the AI Dungeon Master** |
| **Global game XP** | playing any game (slow trickle) | global skills — a leg-up everywhere, including games not yet started |
| **Per-game XP** | playing that game (fast) | that game's own skill tree — each game stays its own mastery climb |

**Q-0182 (BINDING, owner-answered 2026-06-28): the hub stays a flat router.** A flat hub
routes into each game; the **biome/location map layer is deferred**. Do not build the map
layer ahead of its gate.

### 2. Deterministic quest/encounter engine

The prerequisite Q-0040 names: the AI narrates and chooses, deterministic code owns
outcomes — so the deterministic substrate must exist first. Pure domain, seedable,
**sim-tested**: quest templates, encounter roll tables keyed (biome × difficulty), reward
tables with hard caps. It **consumes the shared encounter engine from `games/shared/`**
(mining implements it first for grid encounters; interface changes are claim-first per
[docs/lanes.md](lanes.md)). Superbot's **Q-0186 wild encounters** (chat-activity-triggered
spawns, owner-decided Lane-A-first on superbot's side) is a **sibling consumer** of the
same engine — design the trigger seam so all three triggers (grid roam, exploration
action, chat activity) fit one resolution core.

### 3. Survival overlay (the rpg-survival plan)

Per superbot `docs/planning/rpg-survival-difficulty-design-2026-06-10.md`:

- Difficulty `easy / medium / hard`; **Easy ≡ the base game, byte-identical** — the whole
  overlay is a pure addition behind the player's choice.
- **One-way ascent (Q-0078):** upgrade difficulty anytime, never downgrade.
- Axes: **health / hunger / energy** — lazy clocks derived from timestamps on read, no
  background tasks.
- **Simulation harness BEFORE any tuning ships.** The sim is the methodology that proves
  a tuning satisfies the Q-0087 dual-track bar before it lands; numbers without sim
  evidence do not ship.

### 4. The D&D story game

**BINDING posture — Q-0040 (owner-answered: "AI picks from bounded menus"):**

- The AI **picks from pre-approved, hard-capped menus** — quest template, reward tier,
  difficulty — **enforced by deterministic code**. It **never computes amounts and never
  mutates state**; the worst case is always a capped, game-approved outcome.
- **Thread-per-session first**; persistent-channel and DM modes come later, in that order.
- **Per-guild opt-in, off by default**; public surfaces first so moderation sees
  everything.
- **Hard budget caps:** per-guild daily budget + per-session turn cap; on exhaustion the
  feature degrades closed with a clear message — never silent overspend.
- Bounded summary persistence only; never raw transcripts.
- Message XP = negotiation leverage vs. the DM — the doctrine's chat↔world fusion.

**Image generation for story scenes is a named future layer (Q-0221) — not scheduled.**
Reserve the seam; don't build it.

## Hard rails — BINDING

- **No pay-to-win (Q-0039 / Q-0190):** free for everyone, forever; power earned, never
  bought.
- **All balance numbers sim-pinned before shipping** (superbot `tools/sim` discipline).
- **Q-0087 dual-track:** casual minutes earn capability; grind earns prestige; grind is
  never mandatory.
- **Deterministic core:** pure, seedable state machines; RNG injected; the AI-authority
  posture above is absolute — deterministic code owns every outcome.
- No production-bot writes; forward-only git; decide-and-flag, never wait.

## Roadmap

- **P0** — kit/lane setup: verify kit adoption (adopt only if mining hasn't yet —
  coordinate via the lanes.md once-only rule); lane claim; design docs (world model,
  engine spec).
- **P1** — the quest + encounter engine: pure, deterministic, sim-tested; the
  shared-engine consumption seam against `games/shared/`.
- **P2** — survival sim harness (before any tuning ships).
- **P3** — D&D thread-pilot design: menu catalogs (quest templates, reward tiers,
  difficulty), the story state machine.
- **P4** — host integration + the AI layer (bounded-menu selection over the deterministic
  engine), when superbot-next's plugin contract lands.
- **P5** — live playtest.
