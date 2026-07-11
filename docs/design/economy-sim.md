# Cross-domain economy sim — whole-economy emission + global invariants

> **Status:** `reference`
>
> Design + sim-pin record for `games/shared/sim/economy_sim.py` and its fast
> test suite `tests/shared/sim/`. Reachable from
> [`shared-index.md`](shared-index.md).

## Purpose

Every per-domain sim (`games/mining/sim/`, `games/fishing/sim/`, `games/dnd/sim/`,
`games/exploration/survival/`) pins **one** game's reward curve in isolation.
Nothing enumerated the whole economy at once, or asserted the cross-domain
properties no single-game sim can see: that no domain mints currency/xp it
shouldn't, that every currency/xp reward stays under the one global cap, and that
the no-op paths mint nothing.

`economy_sim.py` is that harness. It **imports and drives the shipped
resolvers/catalogs** of all four world games, computes each domain's per-hour
emission, and asserts three named global invariants. It is **read-only**: it
changes NO balance constant. The emission magnitudes are DERIVED by running the
current shipped resolvers and pinned with the tolerance bands below — so a
cross-domain regression reddens CI without this PR touching a single reward
number.

## The emission model

Two kinds of faucet exist across the economy, throttled by two different
mechanisms:

### Item faucets — energy-throttled (mining, fishing)

Mining and fishing mint **items only** at the resolver layer — zero currency,
zero global_xp, zero game_xp. Their per-hour emission is set by the shared energy
model (`games/mining/core/energy.py`: `MAX_ENERGY=60`, regen +1 every
`REGEN_SECONDS=10` → 360 energy/hr):

- **Mining** — `roll_mine_loot(...)` returns `(ore_name, amount)` with
  `amount = max(1, round(randint(1, BASE_ROLL_MAX=2) * bonus))`
  (`games/mining/core/rewards.py`). `DIG_COST=1` → **360 digs/hr**.
  Sampled baseline (no-tool, surface): **≈ 1.50 ore/dig → ≈ 540 items/hr**.
- **Fishing** — `resolve_cast(...)` returns a `CastOutcome`; a bite yields one
  fish stack via `catch_to_grant(...)`, whose `ProgressionDelta` is **explicitly
  empty** (`games/fishing/inventory/adapter.py`). `CAST_COST=2`
  (`games/fishing/core/catch.py`) → **180 casts/hr**. Sampled baseline bite rate
  at the neutral default spot ≈ `BASE_BITE_CHANCE` 0.55 → **≈ 99 items/hr**.

**Mining coins are a downstream sell-conversion, NOT a mint.** Coins exist only
when a player later sells ore at the per-unit `value` in
`games/mining/core/items.py` (stone 1 … diamond 12; weighted-mean surface ore
≈ 3.05 coins/ore). The sim reports an *informational* sell-ceiling
(`items/hr × coins/ore ≈ 1,640 coins/hr`) in the mining note and marks it a
sink-conversion, never a native mint.

### Currency/xp faucets — host-gated per-completion (dnd, exploration)

Exploration quests are the native currency/xp faucet; dnd reuses that same
engine. Neither has an in-domain cooldown, so **per-hour is host-gated** — the
domain-side pinned quantity is a **per-completion bundle**, not a rate.

- **Exploration** — `engine.grant_rewards(...)` returns exactly
  `catalog.TIER_CAPS[tier]` (`games/exploration/quest/catalog.py`):
  I = (gxp 5, game_xp 25, cur 10), II = (10, 60, 25), III = (20, 120, 50). Tier
  III is the max and equals `GLOBAL_MAX`.
- **DND** — `escort_step` (`games/dnd/core/effects.py`) reuses the exploration
  quest engine and mints exactly the tier-I bundle **(5, 25, 10)** on COMPLETE;
  `rest_noop` and `scout_narrate` mint nothing. The DM never sets amounts
  (bounded-menu, Q-0040 / D-0007).

`catalog.GLOBAL_MAX = (20, 120, 50)` is the **only** cross-domain reward
ceiling. There is **no** daily / per-hour / per-domain emission cap anywhere — the
global cap binds the quest engine + dnd, NOT the mining/fishing item faucets.

## Named invariants

- **`GRANT_WITHIN_GLOBAL_CAP`** — every currency/xp bundle (each quest
  `TIER_CAPS` tier AND the dnd escort bundle) is `<= catalog.GLOBAL_MAX`
  component-wise. `all_bundles_within_global_cap(report)`.
- **`ITEM_FAUCET_MINTS_NO_CURRENCY`** — mining & fishing native currency /
  global_xp / game_xp per hour are all `0.0` exactly.
  `item_faucets_mint_no_currency_or_xp(report)`.
- **`NOOP_MINTS_NOTHING`** — the real no-op / baseline / too-tired paths mint
  nothing: dnd `rest_noop` + `scout_narrate` (no reward), a mining NONE encounter
  (no rewards), a fishing no-bite / too-tired cast (`EMPTY_GRANT`).
  `noop_paths_mint_nothing()`.

## Pinned table

Emission values DERIVED from the current shipped resolvers over the default sweep
(`seeds=range(24)`); the fast tests re-assert them over a smaller sweep.

| domain | items/hr | native cur/gxp/game_xp | action ceiling | per-completion bundle |
|---|---|---|---|---|
| mining | **≈ 540** (band 480–600) | 0 / 0 / 0 | 360 digs/hr | — |
| fishing | **≈ 99** (band 85–115) | 0 / 0 / 0 | 180 casts/hr | — |
| dnd | 0 | 0 / 0 / 0 | host-gated | (gxp 5, game_xp 25, cur 10) |
| exploration | 0 | 0 / 0 / 0 | host-gated | (gxp 20, game_xp 120, cur 50) = GLOBAL_MAX |

**`GLOBAL_MAX = (global_xp 20, game_xp 120, currency 50)`** — the one
cross-domain ceiling; every quest tier + the dnd bundle sits at or under it.

### Tolerance bands

- `_MINING_ORE_PER_HOUR = (480.0, 600.0)` — observed ≈ 540 (≈ ±10%, clean
  integers). Mean ore/dig ≈ 1.50 × 360 digs/hr.
- `_FISHING_FISH_PER_HOUR = (85.0, 115.0)` — observed ≈ 99 (≈ ±10%). Bite rate
  ≈ 0.55 × 180 casts/hr.

The bands were derived from the **current shipped resolvers** — **no balance
number was changed** in the PR that added this sim. Regenerate with
`python3 -m games.shared.sim.economy_sim` and re-pin the bands here (only) if a
resolver's faucet constant intentionally changes; never edit a resolver to move a
band.

Per-hour currency/xp for dnd and exploration is **host-gated** (no in-domain
cooldown), so the domain-side pinned quantity is the **per-completion bundle**,
not a rate — the host decides how often a completion can occur.
