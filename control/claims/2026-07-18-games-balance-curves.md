# Claim · games-balance-curves

- **Branch:** `claude/games-balance-curves`
- **Scope:** Resolve two queued owner-input balance decisions from
  `docs/NEXT-TASKS.md` (§ "Owner-input decisions queued (2026-07-18 overnight
  loop)"), both **latent / not player-reachable today**, in one flagged PR:

  - **#1 [balance] — exploration ore-scaling uses the retired runaway curve.**
    `games/mining/core/exploration.py::_scale_amount` (~line 272) scales ore
    gains by the pre-2026-06-22 steep curve `1 + mining_power // 2` (×5 at
    diamond power 8). The sim-pinned 2026-06-22 rebalance flattened the live dig
    faucet (`rewards.mine_multiplier`) to `1 + power * TOOL_POWER_GAIN`
    (`TOOL_POWER_GAIN = 0.0625` → ×1.5 at diamond) but was never propagated to
    the still-unwired exploration engine. Apply the stated owner-default:
    **propagate the flattened curve** so exploration matches the live faucet,
    reusing `rewards.TOOL_POWER_GAIN` and the same `max(1, round(...))` rounding
    the faucet uses (one source of truth for the constant).

  - **#7 [balance] — cross-game fish valuation gap.**
    `games/mining/core/items.py::register_fish_species` (~lines 282–304)
    registers each fish into the mining market worth `max(1, size_rank)` = 1–4
    coins, while `games/fishing/core/economy.py` sells the same species on the
    V043 curve at 8 / 13 / 27 / 80 — a ~20× gap. Apply the stated owner-default:
    **make the fishing V043 curve canonical** — value a registered fish by its
    fishing-economy V043 price, reusing the fishing curve as the single source
    of truth (a lazy import at host-wiring time preserves the mining core's
    import-time fishing severance; species not on the V043 curve keep the
    `max(1, size_rank)` fallback).

  Narrow changes in `games/mining/core/exploration.py::_scale_amount` and
  `games/mining/core/items.py::register_fish_species` (+ its docstring/protocol)
  plus tests in `tests/mining/test_exploration_world.py` and
  `tests/mining/test_items_market.py`. Both reversible; the exact ×-factor and
  canonical curve are balance calls the owner can override. Flagged for owner
  review.
- **Date:** 2026-07-18 (owner-authorized code slice)
- **Self-initiated:** ⚑ owner-authorized game-improvement slice (menno420, live
  2026-07-18) — two queued owner-input balance decisions resolved as one
  flagged PR.
