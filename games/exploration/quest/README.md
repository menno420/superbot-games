# Exploration quest engine

Deterministic, pure quest engine for the exploration lane. It owns every outcome
the AI DM later narrates (Q-0040): no wall-clock, no `random`/global RNG, no I/O,
no network — same inputs produce byte-identical outputs.

## Modules

| Module | What it is |
|---|---|
| `rng.py` | `DetRng` (splitmix64) + `derive_seed` (FNV-1a 64-bit, `PYTHONHASHSEED`-stable). |
| `models.py` | Enums + frozen dataclasses (`QuestTemplate`, `QuestInstance`, `RewardBundle`, …). |
| `predicates.py` | EventBus-predicate matching: `GameEvent` + a general matcher and 5 aliases. |
| `catalog.py` | The v1 bounded-menu catalog: 5 templates × 3 reward tiers with hard caps. |
| `engine.py` | Pure transition functions: `offer`/`accept`/`apply_event`/`grant_rewards`/… |
| `leverage.py` | Message-XP → DM menu-width (widens *how many* options, never amounts). |

## Public API

```python
from games.exploration.quest import engine, catalog
from games.exploration.quest.models import RewardTier
from games.exploration.quest.predicates import GameEvent

inst = engine.offer("supply_run", player_id, RewardTier.II, world_seed)
inst = engine.accept(inst)
inst = engine.apply_event(inst, GameEvent("item_delivered", {"item": "supply_crate"}))
# ... until all objectives done -> QuestState.COMPLETED
reward = engine.grant_rewards(inst)   # capped, code-owned RewardBundle
```

## Invariants

- **Determinism** — every function is pure and seedable; see `test_rng.py` and the
  `offer` determinism tests.
- **Bounded menu (Q-0040)** — the AI DM only PICKS `(template_id, RewardTier)` from
  `catalog.menu()`. Amounts are code-owned and clamped to `TIER_CAPS` / `GLOBAL_MAX`.
- **No pay-to-win (Q-0039/Q-0190)** — the prestige capability is granted only on a
  tier-III completion; it is never purchasable with currency.
- **Sim-pinned balance** — `tests/test_balance_sim.py` proves no emittable reward
  exceeds the caps, across all templates × tiers × 1000 seeds, reproducibly.

## How the host wires events

The engine does **not** subscribe to anything. The host (superbot-next exploration
plugin) runs an EventBus adapter that maps a bus event → `GameEvent(type, payload)`
and calls `engine.apply_event(instance, game_event)`, persisting the returned new
instance. Objectives advance by predicate match; the engine owns the state machine.
