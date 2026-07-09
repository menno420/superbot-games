# Quest / encounter engine — design (exploration P1, Lane C)

> **Status:** shipped v1 (deterministic core + v1 bounded-menu catalog + shared
> encounter seam + balance sim). Accurate to the code under
> `games/exploration/quest/**` and `games/shared/encounter/**`.

## 1. World / engine model

The exploration lane is a **D&D-style story game** where an AI DM narrates and a
**deterministic core owns every outcome** the AI describes (Q-0040). The engine is
the authority for quest state, objective progress, and reward amounts; the AI only
*picks* and *narrates* within hard-coded rails.

Three properties are load-bearing and enforced by tests:

- **Pure & seedable** — no wall-clock, no `random`/global RNG, no I/O, no network.
  Same inputs → byte-identical outputs. All randomness flows through `DetRng`
  (splitmix64) seeded by `derive_seed` (FNV-1a 64-bit, stable across processes and
  independent of `PYTHONHASHSEED` — Python's builtin `hash()` is salted and must
  not be used).
- **Immutable state** — quests are frozen dataclasses; every transition returns a
  **new** `QuestInstance`, never mutates.
- **Engine-not-content** — the engine is *logic*; quest templates are *data* in the
  catalog. Adding a quest is adding a template, not code.

## 2. Public API (module map)

`games/exploration/quest/`

| Module | Public surface |
|---|---|
| `rng.py` | `DetRng(seed).next_u64/randint/choice/weighted_choice`; `derive_seed(*parts)`. |
| `models.py` | `QuestKind`, `QuestState`, `RewardTier`, `Objective`, `RewardBundle`, `ObjectiveProgress`, `QuestTemplate`, `QuestInstance`, `QuestStateError`. |
| `predicates.py` | `GameEvent(type, payload)`; `event_type_match`; `evaluate(name, event, params)`; 5 aliases. |
| `catalog.py` | `TIER_CAPS`, `GLOBAL_MAX`, `TEMPLATES`, `get(id)`, `menu()`. |
| `engine.py` | `offer`, `accept`, `apply_event`, `abandon`, `fail`, `expire`, `grant_rewards`. |
| `leverage.py` | `menu_width(message_xp)`; `BASE_MENU_WIDTH`, `MAX_MENU_WIDTH`, `XP_PER_EXTRA_OPTION`. |

`games/shared/encounter/`

| Module | Public surface |
|---|---|
| `interface.py` | `EncounterTrigger`, `EncounterRequest`, `EncounterOutcome`, `EncounterResolver` (Protocol). |
| `reference.py` | `ReferenceEncounterResolver`, `ALLOWED_KINDS`. |

Quest lifecycle:

```
offer(template_id, player_id, tier, world_seed)  -> OFFERED
accept(instance)                                 -> ACTIVE
apply_event(instance, GameEvent) [xN]            -> ACTIVE ... -> COMPLETED
grant_rewards(instance)                          -> capped RewardBundle
# side transitions: abandon/fail -> FAILED, expire -> EXPIRED (from OFFERED/ACTIVE)
```

## 3. Determinism + Q-0040 bounded-menu invariants

**Q-0040 bounded authority — "the AI picks from bounded menus."** The AI DM may only:

1. **PICK** a `(template_id, RewardTier)` pair from `catalog.menu()` — a pre-approved,
   hard-capped catalog. It never invents a quest and never chooses an amount.
2. **NARRATE** the deterministic outcome the engine produced.

The AI **never** computes reward amounts and **never** mutates state. `grant_rewards`
returns exactly the tier's code-owned `RewardBundle`, always `<= TIER_CAPS[tier]` and
`<= GLOBAL_MAX` component-wise. The balance sim
(`tests/test_balance_sim.py`) proves this across every template × tier × 1000 seeds,
and proves the aggregate is reproducible on a re-run of the same seed set.

**No pay-to-win (Q-0039 / Q-0190).** A quest's `prestige_capability` unlock is granted
**only** on a **tier-III** completion — earned by play, never bought with currency.
Tiers I and II grant `capability=None`.

## 4. EventBus-predicate progress model

The engine does **not** subscribe to anything. The host's EventBus adapter normalizes
a bus event into a `GameEvent(type, payload)` and calls `apply_event`. Each
not-yet-done objective runs its predicate against the event; the returned increment is
added and **clamped to `required`**. When all objectives are done → `COMPLETED`.
`step` bumps on every applied event (an audit counter).

Predicates are pure `(GameEvent, params_dict) -> int`. One general matcher backs all
aliases:

- `event_type` — the required `GameEvent.type`.
- `match` — every payload key/value here must be present and equal.
- `count_field` — optional payload key read as an integer increment; else a match
  increments by 1 (a `bool` is rejected, not read as an int).

Registered aliases (event_type pinned): `item_delivered`, `npc_reached`,
`target_defeated`, `location_reached`, `captive_freed`, `clue_found`.

## 5. The v1 bounded-menu catalog

Exactly **5 templates**, one per `QuestKind`; the ordered `menu()` is the surface the
AI picks from.

| template_id | kind | objective(s) | prestige capability (tier III) |
|---|---|---|---|
| `supply_run` | FETCH | deliver 3 `supply_crate` (`item_delivered`) | `trade_route_unlock` |
| `safe_passage` | ESCORT | traveler → waystation ×1 (`npc_reached`) | `guild_courier_unlock` |
| `cull_the_pack` | HUNT | defeat 5 `dire_wolf` (`target_defeated`) | `beast_tracker_unlock` |
| `missing_scout` | RESCUE | reach `cavern` (`location_reached`) **and** `captive_freed` | `field_medic_unlock` |
| `whispering_ruins` | MYSTERY | find 4 clues (`clue_found`) | `lorekeeper_unlock` |

**Reward tier caps** (hard ceilings; code-owned; sim-pinned):

| Tier | global_xp | game_xp | currency |
|---|---|---|---|
| I (casual) | 5 | 25 | 10 |
| II (standard) | 10 | 60 | 25 |
| III (prestige) | 20 | 120 | 50 |

`GLOBAL_MAX = (global_xp 20, game_xp 120, currency 50)` — the absolute ceiling; every
tier is `<=` it component-wise, and tiers are strictly monotonic (III > II > I on each
field). Tests pin all of this.

> **Number provenance.** The exact superbot **Q-0087 dual-track** band constants were
> not sourced into this repo. These tier ceilings are deliberately conservative,
> in-band values chosen to be **reconciled against the canonical Q-0087 bands later**;
> they exist so the engine is fully sim-pinned now. `catalog.py` is the single source
> of truth — change the caps there and the tests re-pin to whatever lands.

## 6. Shared encounter seam (claim-first)

`games/shared/encounter/` is the **public shared** encounter-resolution seam
(`docs/lanes.md` claim-first). One core serves all three **Q-0186** triggers:
`GRID_ROAM`, `EXPLORE_ACTION`, `CHAT_ACTIVITY`.

- `interface.py` — `EncounterRequest(trigger, player_id, world_seed, context)`,
  `EncounterOutcome(encounter_id, kind, payload, seed)`, and the
  `EncounterResolver` Protocol (`resolve(request) -> outcome`).
- `reference.py` — `ReferenceEncounterResolver`: deterministic, dependency-free
  (reuses `DetRng`/`derive_seed`), weighted over kinds `none=50, creature=25,
  cache=15, event=10`. It exists so exploration is unblocked now.

**Ownership.** Mining owns the **production** resolver and replaces the reference impl
via the Protocol — no consumer change. Any change to this interface's public surface
is announced in **both** lanes' status files in the same session it ships.

## 7. Message-XP → menu-width leverage

Message-XP is **DM leverage**: it only widens **how many** whitelisted story-action
options the AI may surface (AG-09 Story Actions = **2–4** buttons) — never the reward
amounts, never the outcomes.

- `BASE_MENU_WIDTH = 2`, `MAX_MENU_WIDTH = 4`, `XP_PER_EXTRA_OPTION = 500`.
- `menu_width(message_xp)` is deterministic, monotonic non-decreasing, floored at
  BASE and hard-capped at MAX (one extra option per 500 XP). Negative/zero → base.

This is the *only* place message activity feeds the AI's authority, and it is
code-computed and capped — the model never decides it (Q-0040).

## 8. How the host (superbot-next plugin) wires this

1. **Offer** — when the DM picks a `(template_id, tier)` from `menu()`, call
   `engine.offer(...)` with the player id and the run's `world_seed`; persist the
   returned `QuestInstance`.
2. **Accept** — on player acceptance, `engine.accept(instance)`.
3. **Progress** — an EventBus adapter maps each relevant bus event to
   `GameEvent(type, payload)` and calls `engine.apply_event(instance, event)`,
   persisting the new instance. Objectives advance by predicate match.
4. **Reward** — when `instance.state is COMPLETED`, call `engine.grant_rewards` and
   apply the capped bundle through the host's XP/currency/capability writers. The
   engine owns the amounts; the host owns persistence and narration.
5. **Encounters** — construct an `EncounterRequest` for a Q-0186 trigger and call the
   injected `EncounterResolver` (reference now; mining's production core later).
6. **Leverage** — pass the player's message-XP through `leverage.menu_width` to bound
   how many story-action buttons the DM may render.

## 9. Tests

`games/exploration/tests/` — `test_rng`, `test_catalog`, `test_predicates`,
`test_engine`, `test_leverage`, `test_encounter_reference`, and the balance-pin
`test_balance_sim`. Run: `python3.10 -m pytest games/exploration/tests -q`.
