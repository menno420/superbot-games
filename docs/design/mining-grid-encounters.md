# Mining grid-encounters — first slice (IMPLEMENTED)

> **Status:** `implemented` · lane: game-mining · 2026-07-09
>
> The first named-next extension past the pure mining port (Q-0198): a sparse,
> feature-keyed **encounter** layer over the seed-deterministic grid. This slice
> ships pure domain only — resolver + sim + tests. Combat depth, host wiring, and a
> stateful depth-gate/cooldown are deferred (see §7). Companion to
> `docs/design/mining-plugin-layout.md` §7 (which now points here) and the founding
> brief `docs/founding-plan-mining.md`.

## 1. What ships this slice

- **`games/mining/core/encounters.py`** — a pure resolver that layers encounters on
  top of `grid.cell_at`. Given `(seed, cell, stats, energy, rng)` it returns a frozen
  `EncounterOutcome` (kind · resolution · narration · rewards · damage_taken ·
  energy_cost). Pure: stdlib + dataclasses/enum/random only; no Discord/DB/IO.
- **`games/mining/sim/encounters_sim.py`** — a pure, seeded sim harness that sweeps
  `(seed, x, y, z)` cells × character tiers and aggregates the outcome distributions.
  Every balance number in the resolver is justified by its output (§5).
- **`tests/mining/test_encounters.py`** — determinism (incl. a subprocess
  process-independence check), the additive-safety invariant, no-pay-to-win, and the
  sim-pinned distributions (re-asserted over a fixed subset).

The pure port's 62 tests + these 11 = **73 tests pass**.

## 2. Encounter model

The resolver is a **two-stage, per-action** function:

1. **Trigger** (keyed on `CellFeature` only — never on stats). Most actions on most
   cells return `EncounterKind.NONE` (the baseline), so encounters stay *sparse*:

   | CellFeature | on trigger | trigger chance |
   |---|---|---|
   | `NORMAL` | `HAZARD` (combat) | `NORMAL_HAZARD_CHANCE` = 7%, depth-scaled, capped 25% |
   | `RICH` | `RICH_VEIN` (richer ore, no combat) | `RICH_VEIN_CHANCE` = 35% |
   | `TREASURE` | `LOOT_CACHE` (packed cache) | `LOOT_CACHE_CHANCE` = 60% |
   | `BARREN` | never — always `NONE` | 0% |

   Because the trigger reads only `CellFeature`, two players on the same cell face the
   same *category* of encounter — the grid's shared-world property carries over.

2. **Resolution** — resolve the triggered kind:
   - `LOOT_CACHE` / `RICH_VEIN` → an ore reward = `round(base × cell.richness) +
     loot_bonus (+ luck for caches)`, item = the cell's featured resource. No combat.
   - `HAZARD` → single-exchange combat against a depth-scaled creature (§3).

`Resolution ∈ {NONE, COLLECTED, WON, FLED, LOST}` records how it went (the sim reads
win/flee/lose rates off this).

### Decisions (each decide-and-flagged; reversible)

- **D — feature-keyed archetypes, one kind per feature.** The simplest mapping that
  reaches a real capability: hazards live on the common `NORMAL` cells, the two "good"
  features (`RICH`/`TREASURE`) pay out, `BARREN` is dead. *Rationale:* keeps the trigger
  a pure function of the already-deterministic grid content and gives each feature a
  distinct meaning without a second content table.
- **D — deterministic-by-default rng, live-roll by injection** (reconciles the task's
  determinism requirement with §7's "live-roll" intent). `rng=None` derives a stream
  from the grid's splitmix64 `(seed, x, y, z)` convention (§4) → `(seed,x,y,z)` gives
  the *same* encounter (reproducible · testable · matches grid determinism). A host
  wanting the founding "two players' runs differ" variance injects its **own** `rng`
  seeded with player/action entropy. One pure resolver serves both. *Rationale:*
  determinism is a property of the *default*, not a constraint on the host — the live
  roll is one `rng=` argument away, and purity/testability are preserved for free.
- **D — single-exchange combat now, multi-turn deferred.** A WON/FLED/LOST outcome from
  one damage-vs-toughness comparison + one hit. *Rationale:* the simplest model that
  already makes earned gear decisive and depth dangerous (§5); multi-turn HP attrition
  is a fast-follow that reuses the same stat inputs.
- **D — rewards reuse the existing ore/depth tables, no parallel economy.** Reward
  items are drawn from `rewards.ore_weights_for_depth(z)` (or the cell's featured ore);
  no bespoke token is minted. *Rationale:* keeps encounters inside the one economy the
  rest of mining already balances (no-pay-to-win, §6).

## 3. Hazard combat (via `EffectiveStats`)

Reuses the cross-game combat stats deathmatch reads — `damage` / `defense` /
`max_health` — so a bare miner has a floor and earned gear is the only lever:

```
monster_toughness = roll(HAZARD_BASE_TOUGHNESS + z·HAZARD_TOUGHNESS_PER_DEPTH, ±40%)
monster_power     = roll(HAZARD_BASE_POWER     + z·HAZARD_POWER_PER_DEPTH,     ±40%)
player_damage     = BASE_PLAYER_DAMAGE (8) + stats.damage
player_hp         = BASE_PLAYER_HP (20)    + stats.max_health

WON   if player_damage ≥ monster_toughness  → graze = max(0, power·0.5 − defense); ore loot
FLED  elif (power − defense) < player_hp     → hit  = max(0, power·0.5 − defense); no loot
LOST  else                                   → hit  = min(player_hp, power − defense); no loot
```

Too drained to fight (`energy < HAZARD_ENERGY_COST`) → a forced retreat (a scrape, no
loot) so a spent player is never trapped. Energy costs: hazard engage 3 (+1 to flee),
rich vein 1, loot cache 0.

## 4. Determinism scheme

`encounter_seed(seed, x, y, z)` reuses the grid's `(seed, x, y, z)` splitmix64 mixing,
then folds a domain salt (`_ENCOUNTER_SALT`) through one more splitmix step so the
encounter stream is **independent** of the grid's feature-selection stream at the same
cell (mixing the same base twice with no salt would correlate the two rolls). It is
integer-only, so it never touches Python's per-process string-hash randomisation —
`(seed, x, y, z)` → the identical encounter across processes (unit-tested with a
subprocess check, mirroring `test_grid.py`).

## 5. Sim-pin table (evidence)

All numbers below are **new design, sim-pinned in-repo** — *not* preserved-from-oracle.
Reproduce with `python3 -m games.mining.sim.encounters_sim` (deterministic; the fast
test re-asserts the bounds over a smaller fixed sweep).

| Metric | Pinned bound | Sim result (276,480 actions) |
|---|---|---|
| Overall encounter rate (sparse) | 8–15% | **11.6%** |
| `NONE` share (baseline dominates) | ≥ 85% | **88.4%** |
| Per-depth hazard share | ≤ 25% ceiling; rises with depth | 5.1% (z0) → 10.0% (z15) |
| Win rate — earned-gear gradient | veteran > geared > fresh | **64.8% > 42.6% > 16.6%** |
| Lost rate — competent never overwhelmed | geared ≤ 5%, veteran ≤ 1% | **0.0% / 0.0%** |
| Mean hazard damage — gear protects | veteran < fresh | **0.5 < 11.7** |
| Surface survivable bare-handed | z0 fresh win ≥ 90% | **100%** |
| Deep needs gear | z15 fresh win ≤ 5%, lost ≥ 50% | **0% win / 91.1% lost** |
| Loot-cache yield (baseline) | mean 7–12 | **9.3** (p90 12) |
| Rich-vein yield (baseline) | mean 4–8 | **5.9** (p90 8) |
| Hazard-win ore (baseline) | mean 1.5–3.5 | **2.1** (p90 3) |

**The load-bearing story is the depth × gear gradient** — a bare miner clears the
surface (100% win) but is overwhelmed in the deep (91% lost at z15), while a player in
earned gear never loses. That gradient *is* the no-pay-to-win incentive: the only way to
survive the deep is gear/skill earned in-domain.

<details><summary>Full sim output (276,480 actions · seeds 0–23 · x,y ∈ [−24,24) · z ∈ {0,3,6,10,15})</summary>

```
actions sampled: 276,480
overall encounter rate: 11.6%

kind frequency (overall):
  none        88.42%  (244,456)
  hazard       6.89%  (19,040)
  loot_cache   1.27%  (3,504)
  rich_vein    3.43%  (9,480)

hazard chance by depth (share of actions that are hazards):
  z=0    5.08%
  z=3    5.96%
  z=6    5.82%
  z=10   7.61%
  z=15   9.97%

hazard resolution by tier (won / fled / lost · mean dmg):
  fresh    won 16.6%  fled 41.4%  lost 41.9%  dmg 11.7  (n=19,040)
  geared   won 42.6%  fled 57.4%  lost  0.0%  dmg  2.6  (n=19,040)
  veteran  won 64.8%  fled 35.2%  lost  0.0%  dmg  0.5  (n=19,040)

baseline-tier hazard resolution by depth (won / fled / lost · mean dmg):
  z=0   won 100.0%  fled  0.0%  lost  0.0%  dmg  3.0  (n=2,808)
  z=3   won 10.9%  fled 89.1%  lost  0.0%  dmg  5.2  (n=3,296)
  z=6   won  0.0%  fled 86.3%  lost 13.7%  dmg  9.0  (n=3,216)
  z=10  won  0.0%  fled 40.1%  lost 59.9%  dmg 15.2  (n=4,208)
  z=15  won  0.0%  fled  8.9%  lost 91.1%  dmg 19.1  (n=5,512)

reward yield (baseline tier · mean / p50 / p90 / max):
  loot_cache    9.3 /   10 /   12 /   12  (n=3,504)
  rich_vein     5.9 /    6 /    8 /    8  (n=9,480)
  hazard        2.1 /    2 /    3 /    3  (n=3,168)

mean energy cost per triggered encounter: 2.33
```

Tiers are built through the real `equipment` model (`compute_stats` on full same-tier
gear sets), so every stat is exactly what a player who *earned* that gear would have —
no invented combat numbers. `geared` = full iron set + iron pickaxe + lucky charm;
`veteran` = full diamond set + diamond pickaxe + lucky charm.

</details>

## 6. No pay-to-win

Encounter outcomes and rewards take **no** coin / purchase / spend / premium input — the
resolver's signature exposes no such lever (asserted by
`test_resolver_exposes_no_spend_or_purchase_lever`). The *only* input that improves an
outcome is `EffectiveStats`, which comes solely from **gear and skills earned in-domain**
(mined ore → smelted → forged gear; allocated skill points). Rewards are drawn from the
existing ore/depth tables — no bespoke currency is minted
(`test_rewards_only_use_the_existing_item_vocabulary`). The sim's gear gradient (§5) is
therefore a *progression* incentive, never a paywall: advantage is earned, not bought.
(Founding plan Q-0039/Q-0190.)

## 7. Deferred to later slices

- **Multi-turn combat depth** — HP attrition across exchanges, monster variety, a real
  flee-vs-fight *choice*. This slice's single-exchange model already makes gear decisive;
  depth is a fast-follow reusing the same `EffectiveStats` inputs.
- **A hard depth-gate + per-action cooldown** (design-doc §7's `z ≥ 10` / ~5-action
  cooldown). These are **stateful across actions** — they track "how many actions since
  the last encounter" — which is a host/workflow concern, not pure domain. The pure
  resolver stays per-action; the workflow layer decides *whether to call it* and threads
  the cooldown. (The resolver already carries the depth-danger via `HAZARD_DEPTH_SCALE`.)
- **Host wiring** — a navigator button/`ResultRender` that surfaces the encounter, and the
  workflow op that applies `damage_taken` / `energy_cost` / `rewards` in one audited
  transaction (Layer 2/3 of the plugin, `docs/design/mining-plugin-layout.md` §2–3).

## 8. Verification

- `python3 -m pytest tests/mining/` → **73 passed**.
- `python3 -m games.mining.sim.encounters_sim` → the §5 distributions (deterministic).
- `python3 bootstrap.py check --strict` → green.
