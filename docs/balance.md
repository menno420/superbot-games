# World Games — Economy Balance (auto-generated)

> **Status:** `reference`

Do NOT edit by hand — regenerate with `python3 tools/gen_balance.py`; CI enforces freshness (`--check`).

Every number below is READ from the shipped code (the source `module.py` is noted per section); this page only formats constants, it never owns them.

## Global reward ceiling

_Source: `games/exploration/quest/catalog.py` (`GLOBAL_MAX`)._

The absolute per-grant ceiling. It binds the quest engine and the DND bounded-menu effects (every grant is `<= GLOBAL_MAX` component-wise); it does NOT bind the mining / fishing item faucets (those are throttled by energy, below).

| component | value |
| --- | --- |
| global_xp | 20 |
| game_xp | 120 |
| currency | 50 |

## Action-rate ceilings (emission throttle)

_Sources: `games/mining/core/energy.py`, `games/exploration/survival/difficulty.py`, `games/fishing/core/catch.py`._

Energy is the frequency brake the owner chose instead of a per-action cooldown: each dig/cast spends energy that refills at a fixed passive rate, so sustained emission per active hour is capped by the regen, not a timer.

Mining base bar: `MAX_ENERGY` = 60, `DIG_COST` = 1, `REGEN_SECONDS` = 10 → sustained digs/hr = 3600 // REGEN_SECONDS = 360.

Survival difficulty scales the shipped bar (`TUNABLES`; Easy is byte-identical to the mining bar). Fishing casts/hr = digs/hr // `CAST_COST` (`CAST_COST` = 2).

| difficulty | max_energy | regen_seconds | cost | sustained digs/hr | sustained casts/hr |
| --- | --- | --- | --- | --- | --- |
| easy | 60 | 10 | 1 | 360 | 180 |
| hard | 40 | 20 | 1 | 180 | 90 |
| medium | 50 | 15 | 1 | 240 | 120 |

## Mining

_Sources: `games/mining/core/rewards.py`, `games/mining/core/encounters.py`, `games/mining/core/items.py`, `games/mining/core/capacity.py`._

### Loot roll (`rewards.py`)

`BASE_ROLL_MAX` = 2 · `TOOL_POWER_GAIN` = 0.0625 · `LEGACY_PICKAXE_MULT` = 1.125.

Surface ore weights (`ORE_WEIGHTS`, depth 0):

| ore | weight |
| --- | --- |
| bronze | 2.5 |
| diamond | 0.5 |
| gold | 1 |
| iron | 2 |
| silver | 1.5 |
| stone | 3 |

### Encounter tunables (`encounters.py`)

| constant | value |
| --- | --- |
| BASE_PLAYER_DAMAGE | 8 |
| BASE_PLAYER_HP | 20 |
| FLEE_ENERGY_EXTRA | 1 |
| HAZARD_ENERGY_COST | 3 |
| HAZARD_LOOT_MAX | 3 |
| HAZARD_LOOT_MIN | 1 |
| HAZARD_MAX_CHANCE | 0.25 |
| LOOT_CACHE_CHANCE | 0.6 |
| LOOT_CACHE_MAX | 6 |
| LOOT_CACHE_MIN | 3 |
| NORMAL_HAZARD_CHANCE | 0.07 |
| RICH_VEIN_CHANCE | 0.35 |
| RICH_VEIN_ENERGY_COST | 1 |
| RICH_VEIN_MAX | 4 |
| RICH_VEIN_MIN | 2 |

### Per-unit ore coin value (`items.py`)

| ore | value |
| --- | --- |
| bronze | 2 |
| diamond | 12 |
| gold | 6 |
| iron | 3 |
| silver | 4 |
| stone | 1 |
| wood | 1 |

### Storage caps + vault coin sink (`capacity.py`)

| constant | value |
| --- | --- |
| BASE_VAULT_CAP | 30 |
| MAX_VAULT_LEVEL | 6 |
| PACK_SOFT_CAP | 40 |
| VAULT_SLOTS_PER_LEVEL | 15 |
| _VAULT_UPGRADE_BASE_COST | 2000 |
| _VAULT_UPGRADE_COST_STEP | 1500 |

## Fishing

_Sources: `games/fishing/core/catch.py`, `games/fishing/core/species.py`, `games/fishing/core/spots.py`, `games/fishing/core/economy.py`._

### Catch resolver (`catch.py`)

| constant | value |
| --- | --- |
| BASE_BITE_CHANCE | 0.55 |
| BITE_LUCK_PER_POINT | 0.08 |
| CAST_COST | 2 |
| MAX_BITE_CHANCE | 0.9 |
| MAX_BITE_LUCK | 3 |
| MAX_FISHING_POWER | 6 |
| MIN_BITE_CHANCE | 0.3 |

### Species (`species.py`)

| species_id | size_rank | rarity_weight |
| --- | --- | --- |
| bass | 2 | 30 |
| legend_carp | 4 | 5 |
| minnow | 1 | 50 |
| pike | 3 | 15 |

### Spot bite biases (`spots.py`)

| spot_id | bite_bias |
| --- | --- |
| deep_water | -0.08 |
| dock | 0 |
| tide_pool | 0.1 |

### Fishing economy (V043) (`economy.py`)

The sim-pinned VERDICT 043 sell + progression curves, wired verbatim (ORDER 007). The seam's `sell` consumes the fish from the haul — sell-OR-cook, never both. Levels are STAT-NEUTRAL readouts: they never feed `fishing_power` / `bite_luck` or any resolver lever.

Per-species sell value (`SELL_VALUES`) + per-catch XP (`ProgressionDelta.game_xp = size_rank`, read off `species.py`):

| species_id | sell (coins) | xp per catch |
| --- | --- | --- |
| bass | 13 | 2 |
| legend_carp | 80 | 4 |
| minnow | 8 | 1 |
| pike | 27 | 3 |

Progression: `XP_PER_LEVEL` = 50 — advancing FROM level L costs `xp_to_next(L) = 50·L` (base level 1). Milestones SURFACE (a readout, never a stat) at L10 / L25; the cumulative XP each needs is derived from the same curve:

| milestone | total xp to reach |
| --- | --- |
| L10 | 2250 |
| L25 | 15000 |

## DND

_Sources: `games/dnd/core/effects.py`, `games/dnd/data/scenes.py`, `games/dnd/core/models.py`._

The AI DM only picks a pre-priced option id; it never sizes an outcome. The `escort_step` effect mints the tier-I quest bundle (global_xp 5 / game_xp 25 / currency 10); the other skeleton effects mint nothing.

| effect_id | mints |
| --- | --- |
| escort_step | tier-I bundle (5/25/10) |
| rest_noop | nothing (narrate-only) |
| scout_narrate | nothing (narrate-only) |

`MAX_MENU_SIZE` = 4 (the walking-skeleton scene `waystation_road` offers 3 options). Every option is `<= GLOBAL_MAX` (bounded-menu posture).

## Exploration quests

_Sources: `games/exploration/quest/catalog.py`, `games/exploration/quest/leverage.py`._

Per-tier reward bundles (`TIER_CAPS`), each `<= GLOBAL_MAX`:

| tier | global_xp | game_xp | currency |
| --- | --- | --- | --- |
| I | 5 | 25 | 10 |
| II | 10 | 60 | 25 |
| III | 20 | 120 | 50 |

Menu-width leverage (`leverage.py`): `BASE_MENU_WIDTH` = 2, `MAX_MENU_WIDTH` = 4, `XP_PER_EXTRA_OPTION` = 500.

## Test suite floors

_Sources: `tests/EXPECTED_SUITES.txt` + each suite's `EXPECTED_MIN_TESTS.txt`._

The per-suite pytest count floors the CI coverage ratchet enforces (ORDER-001).

| suite | min tests |
| --- | --- |
| `games/exploration/tests` | 61 |
| `services/tests` | 216 |
| `tests/cross_cli` | 4 |
| `tests/dnd` | 75 |
| `tests/exploration` | 23 |
| `tests/fishing` | 125 |
| `tests/mining` | 196 |
| `tests/shared/inventory` | 57 |
| `tests/shared/rng` | 11 |
| `tests/shared/sim` | 40 |
| `tests/tools` | 35 |

## Notes

Per-hour currency/xp for DND and exploration is host-gated (there is no in-domain cooldown, so the host decides how often a scene/quest can be run). Cross-domain per-hour emission enumeration lives in the economy sim; folding those derived numbers into this page is a follow-up once that sim lands on main.

