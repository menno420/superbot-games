# Buildability map — exploration / D&D domain

> **Status:** `reference` — manager-commissioned research, 2026-07-09. Verified against superbot@7480a5f and superbot-next@main. Source docs win on drift.

# BUILDABILITY MAP — exploration / federated-world / D&D story-game domain

## Component rows

### 1. Explore world hub + world registry
- **STATE: SHIPPED** — `disbot/services/world_registry.py` (WorldEntry seam, opener-as-opaque-callable so no services→views edge), `disbot/views/explore/world_hub.py` (`ExploreWorldHubView`, `!world`), mining `🗺️ Explore` re-parented. PR #1156 (plan §4 status block).
- **PLAN:** `docs/planning/explore-hub-federated-world-plan-2026-06-19.md` §4 PR 1. Q-0182 Q1 answered 2026-06-28: **flat HubView router; map/biome layer deferred**.
- **INVENTION GAP:** none for the spine. New games dock by registering one `WorldEntry`.
- **EFFORT SHAPE:** done.

### 2. Cross-game identity card (plan PR 3)
- **STATE: SHIPPED** — `game_xp_service.world_identity()` (global level = SUM(xp), per-game levels), `disbot/views/explore/world_card.py`, `🪪 World Card` button, `!worldcard`/`!mystats`. Read-only stranger-grade (Q-0080), AST-pinned no-mutation.
- **PLAN:** explore-hub plan §4 PR 3.
- **INVENTION GAP:** only "how rich should it get" (Q-0182 Q4 — explicitly riding defaults until the deferred layer is greenlit).
- **EFFORT SHAPE:** done; enrichment is execution-light.

### 3. Per-game skill trees — the open PR 2
- **STATE: designed-not-built, explicitly gated.** Verified: `player_skills` (migration 071) PK is `(user, guild, branch)` — **no `game` column**; `services/skill_service.py` is mining-only, points from the *global* game-XP level.
- **PLAN:** explore-hub plan §4 "⚠️ PR 2 reframe": remaining work = a `game` discriminator migration on a **live progression table** + the new earning model; plan itself gates it to a runtime-verified session with owner design input.
- **INVENTION GAP:** (a) migration/backfill semantics (existing tree becomes `game='mining'`?); (b) whether skill points stay funded by the *global* level or move to per-game levels (the plan is silent — this is the real fork); (c) the **global-skill catalog** ("stamina/carry/luck/xp-gain" exist only as examples in the idea doc); (d) per-game respec pricing.
- **EFFORT SHAPE:** design-medium then execution-heavy; blocked-on a runtime-verified session per the plan's own gate.

### 4. Three-XP-track earning model (incl. message-XP-as-DM-leverage)
- **STATE: decided-posture-only.** Data substrate exists: message XP (`disbot/utils/db/xp.py`), per-game-keyed `game_xp` (GAME_MINING/CRAFTING/FISHING… constants), global level = SUM. The **"per-game fast + global trickle" split and the DM-negotiation hook have zero code**.
- **PLAN:** `docs/ideas/explore-hub-federated-world-2026-06-19.md` § "Progression & gear model" (owner direction 2026-06-19, "raw but decided"); Q-0182 preamble confirms the three-track model is *decided*, shape open.
- **INVENTION GAP:** trickle ratio numbers (D0/Q-0087 sim-provable); and the message-XP→DM-leverage mechanic is **entirely undesigned** — what "negotiation leverage" mechanically is, its caps, its seam into the (nonexistent) DM. It depends on component 8.
- **EFFORT SHAPE:** design-heavy on the DM half; the trickle half is execution-medium once PR 2's fork is decided.

### 5. Survival overlay (difficulty contract · health/hunger/energy · sim harness)
- **STATE: designed-not-built — with a drift wrinkle.** `docs/planning/rpg-survival-difficulty-design-2026-06-10.md` is the most complete unbuilt design in the domain (D0–D6, P0–P5, G1–G3, Q-0078 one-way ascent, Q-0087 dual-track bands). Verified in source: **no `difficulty` column, no health/hunger anywhere in `disbot/`**, P0 sim harness not built. **BUT universal energy shipped since** (migrations 086/088, `utils/mining/energy.py`, `utils/fishing/energy.py` — sim-pinned pace brake for *everyone*, 2026-06-22), and campfire cooking exists (`mining_workflow.cook`, cooked fish restores energy) — contradicting the plan's "Easy = no energy at all, byte-identical" D1 row and partially pre-shipping D2/D3.
- **PLAN:** the survival plan, phases P0→P5.
- **INVENTION GAP:** D1 contract **re-baseline** against shipped energy/food (which axes still differentiate difficulties); G2 numbers (owner-confirm-from-sim, by design); Medium-death penalty; whether cooked food sells (plan's own open list).
- **EFFORT SHAPE:** one design-reconcile pass, then execution-heavy. P0 harness is a named build-ready alternate in `docs/roadmap.md` (~line 247) — buildable today.

### 6. Deterministic quest/encounter engine
- **STATE: designed-foundation-only, nothing built.** Verified: **zero quest files in `disbot/`**. Encounter prior art exists only as the creature-game catch roll (`utils/creatures/encounters.py`, command-triggered) and the survival plan's biome×difficulty tables (unbuilt, D4).
- **PLAN:** `docs/planning/poketwo-musicbot-feature-mapping-plan-2026-06-20.md` Lane C — `quest_service` + `quest_progress`/`achievement_grant`, progress via existing EventBus events, engine-not-content; AG-08 (superbot-vision §4) sketches the five templates (fetch·escort·hunt·rescue·mystery) with bounded slot menus. Constraints pinned: Q-0081 single-party-first, Q-0040 AI-picks-from-menus.
- **INVENTION GAP:** quest schema + predicate language; the actual **bounded-menu catalog** (templates/targets/reward tiers/caps) — this catalog *is* the substrate the AI DM picks from, and it has never been enumerated; quest-log UI; content authoring (explicitly deferred behind Q-0182's deferred layers).
- **EFFORT SHAPE:** design-medium → execution-heavy. Lane C engine is ungated and buildable now; it is the prerequisite for both the D&D game and pets-rescue.

### 7. Wild encounters (Q-0186 Lane A)
- **STATE: designed-not-built, owner-greenlit.** Q-0186 ANSWERED 2026-06-28: build Lane A first; spawn defaults + guardrails ride the doc's defaults. Verified: no activity-spawn code exists (creature catch is `!catch`/`!hunt` only).
- **PLAN:** `docs/ideas/wild-encounters-activity-spawning-2026-06-20.md` + feature-mapping plan Lane A: debounced per-channel activity counter → spawn embed + Claim button → rewards through `economy_service`/`game_xp` (`GAME_ENCOUNTERS`), docked via `world_registry`.
- **INVENTION GAP:** near-zero — threshold/debounce, reward pool, claim shape are explicitly "refined when the runtime session builds" (Q-0186 answer text). The domain's cheapest executable win.
- **EFFORT SHAPE:** execution-heavy (small PRs, runtime-verified).

### 8. The D&D story game itself ★ the domain's largest invention gap
- **STATE: decided-posture-only / raw-idea.** No plan doc exists (verified: nothing in `docs/planning/` for it). What IS decided: Q-0040 (2026-06-09) — AI **picks quest template/reward tier/difficulty from pre-approved hard-capped menus**, thread-per-session first, per-guild opt-in off-by-default, bounded-summary persistence only (never transcripts), public surfaces first, DM mode last; Q-0082 €30/mo ceiling, visible "storyteller is sleeping" degrade; Q-0081 solo-core/single-party-first; V-10/AG-09 the "Story Actions" component (title + 2–4 buttons bound to engine-computed whitelisted legal actions; auto-continue via EventBus, e.g. `item_equipped`); ADR-002 restart-ends-session+refund. It's the owner's **#1 regret-if-missing feature** (owner-vision-ideas-2026-06-08 §25). Rebuild side: Q-0221 records "the D&D-style story game itself is NOT scheduled — known-options menu, future owner decision"; the rebuild's draft-pipeline spec uses a "10-channel D&D canary" only as a stress case.
- **PLAN:** none. Q-0040's own answer scope: needs **its own plan + the per-exposure lift + one small bounded-authority decision** before anything ships.
- **INVENTION GAP — literally never designed:**
  - **Session lifecycle**: start/join/leave/kick exist as posture lines; timeout, resume-from-summary, restart behavior with no stake, session caps per guild — none specified.
  - **Menu taxonomy**: the actual pre-approved menus (quest templates beyond AG-08's five words, reward-tier ladder, difficulty caps) have never been enumerated anywhere.
  - **Story persistence**: "bounded summary in `game_state_service` versioned-JSONB" is named, but the summary schema, scene/act structure, and what survives session end are undesigned.
  - **Story state machine**: what a turn is; how AI-narration ↔ deterministic-roll ↔ Story-Actions-click interleave; how auto-continue-on-game-event concretely re-enters the loop.
  - **Character sheets**: is the D&D character the existing world character (equipment/skills/game-XP) or a session-scoped sheet? Never asked.
  - **Multiplayer/party turn rules**: Q-0081 says single-party-first; turn order, shared vs per-player Story Actions, joining mid-session — nothing.
  - **Failure states**: story-death vs survival D5 rescue; budget exhaustion **mid-scene**; moderation interrupt; abandoned threads.
  - **Reward minting**: which deterministic owner pays out (quest engine is the obvious answer — unbuilt).
  - The **bounded-authority decision** itself (formalizing AI-selects-from-menus) — Q-0040 names it as a required gate, still open.
- **EFFORT SHAPE:** design-heavy; blocked-on the quest/encounter engine (component 6) as its deterministic substrate + its own plan + per-exposure lift.

### 9. AI orchestration seams (what exists in the old bot)
- **STATE: SHIPPED substrate.** Verified in `disbot/services/`: `ai_orchestration_policy/mutation/presets` (Phases 1–3, #612/#618/#619, incl. `AIToolBudget` + profiles), Phase-4 plan→execute→verify workflow (#634), `ai_task_router`, `ai_tool_catalogue`, `ai_tools`, `ai_gateway`, `ai_decision_audit_service`, `game_state_service` (versioned-JSONB session state — the named DM persistence pattern). Model loop live-verified (Q-0086, #707).
- **PLAN:** Q-0040's implementation sequence: deterministic games-side event/reward owner → a `dungeon_master` orchestration profile/toolset → thread-mode pilot.
- **INVENTION GAP:** the `dungeon_master` profile, its toolset, and per-session budget mapping — all unbuilt but pattern-following.
- **EFFORT SHAPE:** execution-medium **once components 6+8 exist**; the seams themselves need nothing.

### 10. Q-0221 image-generation layer
- **STATE: decided-posture-only, homed in the REBUILD not the old bot.** Q-0221 (2026-07-03): `MediaGenerationSpec` in superbot-next's **L4 AI band**, provider-agnostic adapter, consumed via the card engine's image-source seam (Q-0220/D-1: engine ships at L1c static-only, generated source activates at L4). Mandatory posture fixed at declaration: per-guild quota + global cap + cache-by-prompt-hash + kill switch + **default-OFF** + content filter + no PII. `OPENAI_API_KEY` verified in containers. The D&D game is its *named future consumer*, explicitly unscheduled.
- **PLAN:** `docs/planning/rebuild-stage1-global-review-2026-07-03.md` D-2 (§4, ~lines 152–166).
- **INVENTION GAP:** provider pick + adapter API; prompt construction from story state; quota numbers; scene style consistency. All deferrable to L4.
- **EFFORT SHAPE:** execution-medium; blocked-on rebuild sequencing (L1c card engine → L4).

### 11. Biome/location map layer (deferred)
- **STATE: deferred by owner decision** (Q-0182 Q1: flat router first). Building blocks shipped: seed-deterministic mining grid x,y,z with z↔biome (`utils/mining/grid.py`, #1281/#1282, Q-0173); fishing Phase-2 boat travel to coordinate+biome destinations with location specialties is captured-later (`fishing-open-world-expansion-plan` Phase 2+ — "bonuses first, hard location-locks only for a few, later").
- **INVENTION GAP:** the whole cross-game map model (destination catalog, travel rules, which activities become location-gated). Deliberately parked.
- **EFFORT SHAPE:** design-heavy + owner-gated; do not build.

### 12. Pets-via-quests
- **STATE: designed-not-built.** Verified: **no `player_pets` migration exists** — nothing of the pets plan shipped. Plan: `docs/planning/pets-companions-plan-2026-06-09.md` P1–P4 (eggs/care/perks/showcase) + Q-0078 "both paths" amendment (quest-rescue = rare-species path *once the quest engine exists*; party 1→3; scout/gold-sense as encounter-table modifiers per AG-07).
- **INVENTION GAP:** small for P1–P2 (species catalog, sink sizing — plan's own open list). One **drift wrinkle to flag**: the creature game shipped since (#1208+) and `!creatures` even aliases `pets` — the pets plan predates it and needs a one-pass dedup/reconcile (companions vs creature collection) before building.
- **EFFORT SHAPE:** execution-heavy for P1–P2; rescue path blocked-on component 6.

### 13. Sibling world activities (context rows)
- **Fishing** — Phase 1 SHIPPED deep (21-fish set, minigame #1296–#1304, bait+crafting #1329/#1337/#1338, boat/deepwater venue #1340, coral structures #1596–#1605, gear stats #1504, loadout presets #1499); Phase 2+ boat-travel captured-later. Docked in the world hub.
- **Creature game** — SHIPPED (catch/collection #1208, level-normalized PvP #1213/#1230, leaderboards #1244; Q-0187: original IP, normalized PvP, tiered roster).
- **Hybrid gear auto-equip toggle** — deferred (Q-0182 Q3); its per-user config surface question is now resolved by Q-0184 (user-chosen scope surface), so only the toggle itself remains.

## TOP 5 open design decisions before the domain is purely buildable

1. **Write the D&D story-game plan + take the Q-0040 bounded-authority decision** (the one named ship-gate). *Recommended default:* formalize AG-09 Story Actions as the **only** AI-emitted component (2–4 engine-whitelisted actions; code enforces legality/caps at click); thread-per-session on `game_state_service` JSONB; **no stakes v1** (ADR-002 restart = clean end, nothing to refund); single-player v1 (Q-0081); world character = the story character (reuse equipment/skills, no separate sheet). This one decision + doc collapses component 8's entire gap list into executable slices.
2. **Enumerate the bounded-menu catalog / quest-engine schema and build Lane C now** (ungated). *Recommended default:* AG-08's five templates × 3 reward tiers × Q-0087-band caps as the v1 menus; `quest_service` + EventBus-predicate progress per the Lane C spec; content authoring stays deferred. It's the deterministic substrate the DM, pets-rescue, and wild-encounter rewards all dock into — highest-leverage single build.
3. **PR 2 fork: where per-game skill points come from + the `player_skills` `game` migration.** *Recommended default:* additive `game` column defaulting `'mining'` (backfill, PK extension); points funded per-game from that game's XP with the global level keeping a small shared point pool; trickle ratio ~15% proven by a P0-style sim before merge; execute in a runtime-verified session (the plan's own gate).
4. **Re-baseline the survival D1 contract against shipped universal energy** (the plan's "Easy = no energy, byte-identical" is now factually false — migrations 086/088 shipped energy for everyone). *Recommended default:* energy stays the universal pace layer as shipped; difficulty modulates only health/hunger/encounters/death/loot; build the P0 sim harness (already a roadmap build-ready alternate) and present G2 numbers from it.
5. **Design the message-XP → DM-leverage mechanic as a deterministic code-side modifier.** *Recommended default:* message-level tiers widen the AI's *menu* (better reward-tier options unlocked / one reroll per session), computed by code, capped, never model-decided — decide-and-flag inside the D&D plan doc (decision 1) rather than as a separate owner round.

Not on the list because already decided: wild encounters (Q-0186 is greenlit with defaults — purely executable, the domain's cheapest next win); the hub shape (Q-0182 Q1 answered); the map layer (deliberately deferred — don't design it).

**Summary:** Buildability map complete — spine (hub/registry/identity card) and AI seams are shipped; wild encounters is greenlit-executable; skill-tree PR 2, survival overlay, quest engine, and pets are designed-but-unbuilt with named gaps; the D&D story game is the domain's one genuinely undesigned pillar (no plan doc, session lifecycle/menus/state machine/party rules/failure states all uninvented, gated by Q-0040's own plan+lift+authority-decision requirement), with the Q-0221 image layer parked in the rebuild's L4 band.
