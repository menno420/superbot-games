# D&D story game — plan / spec (exploration P3 → P4)

> **Status:** `plan` — closes the Q-0040 ship-gate; routes the bounded-authority
> decision to the owner (⚑ needs-owner at the foot of this doc). This is a
> plan/spec, not code. It sits on top of the already-shipped deterministic
> quest/encounter engine (`docs/design/quest-encounter-engine.md`).

## 0. What this doc is

The exploration domain's one genuinely undesigned pillar is the **D&D story game**
itself (buildability map §8: "the domain's largest invention gap"). Q-0040's own
answer scope names three prerequisites before anything ships: **its own plan**, the
**per-exposure lift**, and **one small bounded-authority decision**. The deterministic
substrate (the quest/encounter engine) is now **built** — this doc supplies the plan
and routes the bounded-authority decision. It:

1. Fixes the **binding posture** (Q-0040 bounded-menu) as the design's spine.
2. States the **recommended v1 defaults** (manager-flagged, from
   `control/inbox-exploration.md` ORDER 002 + buildability map decision-1), each with
   a one-line rationale.
3. Specifies the **uninvented pieces** this plan must define (session state machine,
   menu taxonomy, persistence schema, character sheet, failure states, AI seam, image
   seam, consumed substrate).
4. Ends with a prominent **⚑ needs-owner** gate.

## 1. Binding posture — Q-0040 bounded-menu (the spine)

**The AI Dungeon Master picks ONLY from pre-approved, hard-capped menus enforced by
code. It never computes amounts and never mutates state.** Deterministic code — the
engine under `games/exploration/quest/**`, already built — owns every outcome the AI
narrates.

Concretely, the DM's entire authority is two verbs:

1. **PICK** a whitelisted option from an engine-offered, code-capped menu
   (`catalog.menu()` for quests; a Story Action menu for turns; a `(template_id,
   RewardTier)` pair for rewards).
2. **NARRATE** the deterministic outcome the engine already computed.

Everything with a number attached — reward amounts, objective progress, capability
unlocks, menu width — is computed by pure code (`engine.grant_rewards`,
`engine.apply_event`, `leverage.menu_width`) and clamped to hard caps
(`catalog.TIER_CAPS`, `GLOBAL_MAX`, `MAX_MENU_WIDTH`). The worst case a compromised or
hallucinating model can produce is *a legal, game-approved, capped outcome*.

## 2. Recommended v1 defaults (recommendation · rationale)

Each row is the **recommended** design. The Q-0040 posture row (⚑) needs owner
sign-off; the rest are decide-and-flag (recommendation stands unless vetoed at the
gate).

| # | Default (recommended) | Rationale (one line) |
|---|---|---|
| D-1 ⚑ | **Story Actions = the ONLY AI-emitted component** (V-10/AG-09): a title + **2–4 whitelisted buttons**; auto-continue driven via EventBus. The AI emits nothing else — no free-form state, no amounts. | Collapses the entire attack surface to "pick a whitelisted button"; every amount/outcome stays code-owned. *(This is the Q-0040 bounded-authority gate — see ⚑ needs-owner.)* |
| D-2 | **Thread-per-session** on **versioned JSONB summaries** (bounded summary persistence, **never raw transcripts**). Public **thread first** → persistent-channel → **DM mode last**. | Threads keep moderation visible and bound cost; summaries (not transcripts) cap storage and PII; public-first is the safe exposure ladder (Q-0040). |
| D-3 | **No stakes v1** — no failure/death economy in the first cut. | Removes the hardest-to-balance system from v1; restart is a clean end with nothing to refund (ADR-002). |
| D-4 | **Single-player v1** (Q-0081 solo / single-party-first). Party turn rules are trivial in v1; leave the seam. | Turn order / shared-vs-per-player Story Actions are the deepest multiplayer design; deferring them ships the core sooner. |
| D-5 | **World character = story character** — one identity; read-only cross-game card (Q-0080). | Reuses shipped equipment/skills/game-XP; no separate session sheet to invent, sync, or reconcile. |
| D-6 | **Opt-in OFF by default per guild**; hard budget caps: **per-guild daily cap + per-session turn cap**; **degrade-CLOSED** on exhaustion ("the storyteller is sleeping"). | Honors the Q-0082 €30/mo ceiling and never silently overspends; off-by-default keeps moderation ahead of exposure. |
| D-7 | **Restart ends the session + refunds** (ADR-002). | With no stakes (D-3) a restart is a clean teardown; any consumed per-session budget/turns are returned. |
| D-8 | **Message-XP → DM-leverage** = the **already-built** deterministic capped code-side menu-**widening** modifier (`games/exploration/quest/leverage.py`: `menu_width` 2→4, +1 per 500 XP, hard cap 4). It widens **how MANY** options the AI may surface — never amounts, never outcomes. | The only place chat activity feeds the DM's authority, and it is code-computed + capped; the model never sets it (Q-0040). *Built and sim-pinned.* |
| D-9 | **Reward minting** flows through the built bounded-menu catalog + `engine.grant_rewards` (tier-capped, code-owned, **no pay-to-win**). The AI picks `(template_id, tier)`; the engine clamps to `TIER_CAPS` / `GLOBAL_MAX`. | Reuses the shipped, sim-pinned reward path; capability unlocks are tier-III-only, earned by play, never bought (Q-0039 / Q-0190). |

**Code citations (already shipped, this session):**

- Menu-widening leverage: `games/exploration/quest/leverage.py` —
  `BASE_MENU_WIDTH = 2`, `MAX_MENU_WIDTH = 4`, `XP_PER_EXTRA_OPTION = 500`;
  `menu_width(message_xp)` is deterministic, monotonic, floored at 2, hard-capped at 4.
- Reward minting: `games/exploration/quest/engine.py` `grant_rewards(instance)` returns
  exactly `catalog.TIER_CAPS[tier]`, always `<= GLOBAL_MAX` component-wise; tier-III
  grants the template's `prestige_capability`, tiers I/II grant `capability=None`.
- Bounded catalog: `games/exploration/quest/catalog.py` — `TEMPLATES` (5 templates),
  `TIER_CAPS`, `GLOBAL_MAX`, `menu()` (the ordered surface the DM picks from).

## 3. The uninvented pieces this plan must define

### 3.1 Session lifecycle state machine

The DM session is a wrapper *around* many quest instances; it has its own lifecycle
distinct from the per-quest `QuestState` machine already in `models.py`.

```
        offer ──accept──▶ active ──turn loop──▶ resolve ──▶ close
          │                  │                                 ▲
          │ decline/timeout  │ restart (ADR-002)               │
          ▼                  ▼                                 │
        (dropped)          refund ───────────────────────────┘
```

| State | Meaning | Allowed transitions |
|---|---|---|
| **offer** | Session offered in a guild channel; opt-in gate + budget check pending. | → `active` (player opts in, budget available); → dropped (decline / timeout / budget exhausted → "storyteller is sleeping"). |
| **active** | Thread open; turn loop running. | → `resolve` (a turn's quest completes); → `refund` (restart, ADR-002); → close (turn cap / daily cap hit → degrade-CLOSED). |
| **turn loop** (sub-state of active) | DM offers a Story Action menu → player picks → engine applies event(s) → DM narrates → auto-continue via EventBus. | back to `active`; a completing quest → `resolve`. |
| **resolve** | A quest reached `COMPLETED`; `engine.grant_rewards` mints the capped bundle; host applies it. | → `active` (next beat) or → `close`. |
| **close** | Session ended cleanly (finished / turn cap / daily cap). Summary persisted (D-2). | terminal. |
| **refund** | Restart teardown (D-7): session ends, consumed per-session budget/turns returned. | → close. |

v1 has **no failure/death state** (D-3); the seam for one is noted in §3.5.

### 3.2 Menu taxonomy — the closed set of Story Action menu types

Every Story Action menu the DM may surface is a **whitelisted, code-owned** menu. The
DM never authors a menu; it picks one *from* the closed set below, and the engine fills
its buttons (2–4, width bounded by `leverage.menu_width`). The set maps onto the 5
quest kinds already in the catalog plus three connective menus:

| Menu type | Backed by | Buttons (whitelisted actions) |
|---|---|---|
| **FETCH** | `QuestKind.FETCH` (`supply_run`) | accept-quest · deliver-progress · abandon · (leverage: alt-route option) |
| **ESCORT** | `QuestKind.ESCORT` (`safe_passage`) | accept · advance-escort · abandon · (leverage: shortcut option) |
| **HUNT** | `QuestKind.HUNT` (`cull_the_pack`) | accept · engage-target · abandon · (leverage: track option) |
| **RESCUE** | `QuestKind.RESCUE` (`missing_scout`) | accept · reach-location · free-captive · abandon |
| **MYSTERY** | `QuestKind.MYSTERY` (`whispering_ruins`) | accept · investigate-clue · abandon · (leverage: extra-clue option) |
| **TRAVEL** | connective (no quest) | move-to-node · rest-here · look-around |
| **SOCIAL** | connective (no quest) | talk · barter · listen |
| **REST** | connective (no quest) | short-rest · make-camp · continue |

Every button is a code-defined legal action; the click emits a `GameEvent` (or a
connective no-op) — the engine, not the model, decides what it does. The number of
buttons rendered is `min(len(available_actions), menu_width(message_xp))`.

### 3.3 Story persistence schema — versioned JSONB summary

**Bounded summary only; never raw transcripts** (D-2). One versioned JSONB blob per
session, evolvable via the `version` field:

```jsonc
{
  "version": 1,                 // schema version — migrate forward, never break old rows
  "beats": [                    // append-only, HARD-CAPPED length (e.g. last N beats kept)
    { "t": 0, "menu": "FETCH", "action": "accept", "quest": "supply_run" }
  ],
  "entities": {                 // named NPCs/places seen — bounded key count
    "traveler": { "kind": "npc", "state": "escorting" }
  },
  "open_threads": [             // unresolved narrative hooks — bounded count
    "the missing scout"
  ],
  "last_menu": "ESCORT"         // the menu type currently offered (resume anchor)
}
```

Bounds are enforced by code on every write (drop oldest beats past the cap, cap entity
and open-thread counts). Nothing here holds a raw message, PII, or a reward amount —
amounts live only in the engine's `RewardBundle` and the host's XP/currency writers.
This is the `game_state_service` versioned-JSONB pattern named in the buildability map
(§8/§9), reused rather than reinvented.

### 3.4 Character sheet = the world character

There is **no session-scoped sheet** (D-5). The D&D character *is* the world character:

- **Fields:** identity, equipment, per-game skills, global game-XP level, message-XP
  (the leverage input). All already exist on the world character.
- **Read-only cross-game** (Q-0080): the story game reads the card; it never mutates it
  outside the audited reward path (`engine.grant_rewards` → host writers).

### 3.5 Failure states — v1 = none; where they attach later

v1 ships **no stakes** (D-3): no story-death, no hunger/health economy, no
budget-mid-scene "game over". The seams where failure attaches in a later cut:

- **Story-death / stakes** → a `failed` sub-state off `active` (mirrors the engine's
  existing `QuestState.FAILED`), gated on the survival overlay's difficulty contract
  (see `docs/design/survival-d1-rebaseline.md`).
- **Budget exhaustion mid-scene** → already handled as **degrade-CLOSED** (D-6), not a
  failure: the session closes cleanly with "the storyteller is sleeping".
- **Moderation interrupt / abandoned thread** → `close` with a reason; no penalty in
  v1.

### 3.6 AI orchestration seam — the `dungeon_master` profile

Unbuilt but **pattern-following**: a `dungeon_master` orchestration profile/toolset
that follows superbot's shipped `ai_orchestration` **plan → execute → verify** pattern
(buildability map §9: `ai_orchestration_policy/mutation/presets`, Phase-4 workflow,
`AIToolBudget`, `game_state_service`). Its defining constraint:

> **The profile's ONLY tool is "pick a Story Action from the offered menu."**

It cannot call a tool that writes state, computes a number, or emits free-form
mechanics — the toolset is a single `select_story_action(menu, choice_index)` bounded
to the engine-offered menu. The per-session `AIToolBudget` maps onto the D-6 turn cap.
This is the concrete realization of the Q-0040 posture at the model layer.

### 3.7 Image-gen seam — Q-0221, reserved, NOT built

Reserve the Q-0221 image-generation seam and **do not build or schedule it**. Its
mandatory posture is fixed at declaration (default-**OFF**, per-guild quota + global
cap + cache-by-prompt-hash + kill switch + content filter + no PII). The D&D game is
its named *future* consumer only; it activates in superbot-next's L4 band, not here.

### 3.8 Consumes (already built)

- **Quest/encounter engine** — `games/exploration/quest/**` (offer/accept/apply_event/
  grant_rewards, the 5-template catalog, tier caps, message-XP leverage). Built +
  sim-pinned this session.
- **Shared encounter seam** — `games/shared/encounter/interface.py` (`EncounterResolver`
  Protocol, `EncounterRequest`/`EncounterOutcome`, `EncounterTrigger` GRID_ROAM/
  EXPLORE_ACTION/CHAT_ACTIVITY) with a deterministic reference resolver. Mining owns the
  production resolver and replaces the reference impl via the Protocol (claim-first).

## 4. Build sequence (P3 → P4)

- **P3 (this doc + follow-ons):** menu catalogs (done for quests; Story Action menu
  taxonomy above), the session state machine, the persistence schema. Design-only.
- **P4 (gated on the ⚑ decision + superbot-next's plugin contract):** the
  `dungeon_master` profile/toolset over the deterministic engine, thread-mode pilot,
  budget wiring.

---

## ⚑ needs-owner — the Q-0040 bounded-authority ship-gate

**PRIMARY (blocks P3 → P4):** approve the Q-0040 **bounded-authority posture** as the
ship-gate for the D&D game:

> **"Story Actions are the sole AI-emitted component; the deterministic engine owns
> all amounts and all state mutation; every menu is hard-capped in code."**

**Recommendation: APPROVE.** This is the one gate blocking the P3 → P4 build. The
deterministic substrate it depends on is already built and sim-pinned
(`games/exploration/quest/**`, 48 tests green incl. the balance-pin sim); approving the
posture unblocks the host-integration + AI layer. The posture is maximally conservative
— the model's worst case is a legal, capped, game-approved outcome.

**SECONDARY (decide-and-flag — recommendation stands unless vetoed):**

- **Budget-cap numbers (D-6):** the per-guild daily cap and per-session turn cap are
  in-band placeholders pending superbot's real Q-0082 €30/mo-derived constants.
  *Recommend:* set them from the €30/mo ceiling once the real budget model is imported;
  degrade-CLOSED behavior is fixed regardless.
- **Public-vs-DM ordering (D-2):** *Recommend* public thread → persistent-channel → DM,
  in that order (moderation-visible first). This matches the Q-0040 exposure ladder.
- **Q-0087 reward caps (D-9):** the catalog tier caps are conservative in-band
  placeholders; *recommend* reconciling with superbot's real Q-0087 dual-track bands
  when available (numbers are sim-pinned meanwhile — change `catalog.py`, tests re-pin).
