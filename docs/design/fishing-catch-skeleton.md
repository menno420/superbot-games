# Fishing catch — walking skeleton (IMPLEMENTED)

> **Status:** `reference` · lane: game-fishing · 2026-07-11 · (walking skeleton IMPLEMENTED · **+ spot biomes**)
>
> The first fishing slice: a sparse, data-driven **catch** resolver that reuses mining's
> shipped cross-game substrate (the energy engine + the `EffectiveStats` gear model) and
> mirrors mining's determinism/sim-pin patterns. This slice ships **pure domain only** —
> resolver + species data + **spot-biome data** + sim + tests. Workflow and host wiring are
> deferred (§7). Companion to `docs/design/mining-grid-encounters.md` (whose patterns it
> follows) and the shared-RNG idea `docs/ideas/shared-deterministic-rng-seam-2026-07-10.md`.
>
> **Update (spot biomes):** the `spot_id` argument — present but inert in the first slice —
> now carries MEANING via a `games/fishing/core/spots.py` DATA table. The spot you fish
> biases *what* you catch (§Spot biomes + §5 per-spot sim-pin). Deterministic, no
> pay-to-win, all nouns-and-numbers-in-data; the neutral default profile reproduces the
> first slice's mechanical outcomes exactly.

Purpose: stand up the thinnest end-to-end fishing capability — cast → deterministic
outcome → a caught fish (or an honest empty cast) — so the plugin's three layers have a
proven pure core to build the workflow/host adapters against, without duplicating the
energy, gear, or determinism machinery mining already ships.

## 1. What ships this slice

- **`games/fishing/core/species.py`** — THE THEME DATA: the species table (four rows:
  `minnow` / `bass` / `pike` / `legend_carp`). Every player-visible noun (name, emoji,
  flavour, `size_rank`, `rarity_weight`) is a data row keyed on a *neutral* string id
  (Q-0267). Mechanics key on the ids; nouns are swappable by editing this file alone.
- **`games/fishing/core/rng.py`** — `fishing_seed(seed, spot_id)`: an independent
  splitmix64 stream (mining's family + a fishing-domain salt), integer-only so it is
  process-independent. Flagged as a promotion candidate for `games/shared/rng.py`.
- **`games/fishing/core/catch.py`** — THE RESOLVER: `resolve_cast(seed, spot_id, stats,
  *, energy, rng)` → a frozen `CastOutcome(bit, catch, narration, energy_cost)`.
  Deterministic code owns every outcome (**NO LLM anywhere**). Pure: stdlib +
  dataclasses/random only.
- **`games/fishing/sim/catch_sim.py`** — a pure, seeded sim harness sweeping casts ×
  gear tiers and aggregating the catch distribution. Every balance number in `catch.py`
  is justified by its output (§5).
- **`games/fishing/core/spots.py`** — THE SPOT DATA: three biome rows (`tide_pool` /
  `dock` / `deep_water`) keyed on neutral ids, each carrying display nouns + a catch
  profile (per-species weight multipliers + a `bite_bias`). `dock` is a neutral identity;
  the flanks bias small/common vs big/rare. See §Spot biomes.
- **`tests/fishing/`** — determinism (incl. a subprocess process-independence check),
  the reused-energy contract + honest states, theme-data-drivenness, no-pay-to-win, the
  spot-biome data + per-spot fair-access + per-spot sim-pins, and the sim-pinned
  distributions. **64 tests** (was 26 core + 20 adapter; +18 spot biomes).

## 2. Catch model + Decisions

`resolve_cast` is a **per-cast** function:

1. **Energy gate** — if `energy < CAST_COST` (2), return the honest `_TOO_TIRED`
   no-bite outcome (`bit=False`, `energy_cost=0`); it never raises.
2. **Bite roll** — a bite fires with chance `BASE_BITE_CHANCE` (0.55), raised by earned
   `bite_luck` (`+BITE_LUCK_PER_POINT` = 0.08 each, capped `MAX_BITE_CHANCE` = 0.90). A
   miss is an empty cast (`bit=False`, `energy_cost=CAST_COST`) — you still spent the cast.
3. **Species pick** — a weighted pick over the species `rarity_weight`s, scaled by two
   independent multiplicative levers: the gear lever
   `(1 + fishing_power · POWER_BIAS_PER_POINT · (size_rank−1))` (rank-1 never boosted;
   `fishing_power=0` → the base weights exactly) **and** the chosen spot's per-species
   `multiplier_for` (the spot catch profile — see §Spot biomes). The spot also nudges the
   bite chance by `bite_bias`. Both spot levers are DATA in `spots.py`.
4. **Size** — `size_rank · SIZE_PER_RANK + rng.randint(0, SIZE_JITTER)`; narration is
   assembled from the picked row's `emoji` / `flavor` / `name` (never hard-coded).

### Decisions (each decide-and-flagged; reversible)

- **D — deterministic-by-default rng, live-roll by injection.** `rng=None` derives a
  stream from `fishing_seed(seed, spot_id)` → `(seed, spot_id)` gives the same cast
  (reproducible · testable). A host wanting per-cast variance injects its own
  `random.Random`. One pure resolver serves both (mirrors mining's encounters). *Reversible.*
- **D — theme via a neutral-id data table.** Player-visible nouns live only in
  `species.py`, keyed on neutral ids; the resolver keys mechanics on ids. Re-theme =
  data edit (Q-0267). *Rationale:* the mining ore/depth-table shape, proven a second time.
- **D — gear biases, never gates (no pay-to-win).** `fishing_power`/`bite_luck` are the
  only advantage levers, and both are *earned* `EffectiveStats`; the signature exposes no
  spend lever, and every species stays reachable at zero gear (§6, Q-0039/Q-0190).
- **D — reuse the mining energy engine.** A cast debits `CAST_COST` through
  `games.mining.core.energy` — fishing shares the one energy economy (and "cooked fish"
  already tops that bar back up), no parallel fuel model.
- **D — per-cast resolver, single roll.** No multi-cast state (streaks, spot depletion,
  bait) — those are stateful-across-casts, a workflow concern, deferred (§7).

## 3. Gear via the shared `EffectiveStats`

The resolver reuses the cross-game gear→stats seam
(`games.mining.core.equipment.EffectiveStats`), reading the `fishing_power` / `bite_luck`
fields shipped in Q-0175. It imports **no** item catalog — a host asks `compute_stats` for
the block and passes it in. The fishing gear is a single CHARM-slot ladder
(`fishing charm` → `anglers charm` → `master angler charm`), so the ceiling is one charm:

| Loadout | `fishing_power` | `bite_luck` |
|---|---|---|
| fresh (no gear) | 0 | 0 |
| `fishing charm` | 2 | 1 |
| `master angler charm` (best) | 6 | 3 |

`MAX_FISHING_POWER` (6) / `MAX_BITE_LUCK` (3) pin that ceiling; a test re-asserts the best
equippable gear cannot exceed it, so a future gear row cannot silently break the sim bounds.

## 4. Determinism scheme

`fishing_seed(seed, spot_id)` mixes the world seed with the spot id's UTF-8 bytes through
the same splitmix64 step the mining grid uses, folding a fishing-domain salt
(`_FISHING_SALT`) so the fishing stream is **independent** of any mining stream at a
coincidentally-equal seed. It is integer-only (never `hash(str)`), so `(seed, spot_id)` →
the identical seed across processes — unit-tested with a subprocess check mirroring mining.
This is the third hand-rolled copy of the splitmix64 derivation in-repo (grid, encounters,
fishing) and is tagged a promotion candidate for `games/shared/rng.py`
(`docs/ideas/shared-deterministic-rng-seam-2026-07-10.md`).

## Spot biomes

`games/fishing/core/spots.py` is the second theme-data table (it mirrors `species.py`):
where you fish biases *what* you catch. A `Spot` is a pure data row keyed on a **neutral
id** — display nouns (`name` / `emoji` / `flavor`) plus the **catch profile**: a
`{species_id: multiplier}` map applied on top of each species' `rarity_weight` (a species
not named defaults to `1.0`), and a `bite_bias` nudge to the base bite chance. `resolve_cast`
resolves one profile via `spots.profile_for(spot_id)` and threads it into the bite roll and
the weighted species pick; it names no spot in a logic branch (narration is assembled from
the spot row's + species row's DATA).

Three shipped biomes — a small, demonstrable gradient:

| spot id (neutral) | biome | biases toward | bite nudge |
|---|---|---|---|
| `tide_pool` | warm shallows | the small/common tail (minnow ↑, rare ↓) | `+0.10` (easy bites) |
| `dock` | the everyday spot | nothing — a **neutral identity** profile | `0.0` |
| `deep_water` | cold deeps | the big/rare tail (pike/legend ↑, minnow ↓) | `−0.08` (stingy) |

### Decisions (each decide-and-flagged; reversible)

- **D — spot is a DATA table, not logic.** The whole spot model (nouns + weight profile +
  bite nudge) lives in `spots.py`; the resolver reads it. Re-theme/re-tune a biome = a data
  edit, zero logic change (Q-0267, the `species.py` shape a second time). *Reversible.*
- **D — bias, never gate (per-spot fair access).** Every spot weight multiplier is
  **strictly positive** (enforced in `Spot.__post_init__`), and the bite chance is floored
  at `MIN_BITE_CHANCE` (0.30). So even the rare-tail-favouring `deep_water` never gates the
  common minnow out, and even the stingiest biome keeps biting — a zero-gear angler lands
  the whole table at **every** spot (§5, Q-0039/Q-0190). No spend lever is added.
- **D — the default profile is an exact identity.** An unknown / `None` `spot_id` →
  `DEFAULT_SPOT` (empty weights, `bite_bias` 0.0). Multiplying a weight by `1.0` and adding
  `0.0` to the bite chance are exact IEEE ops, so a default-profile cast reproduces the
  first slice's **mechanical** outcome (species / size / bite / energy) byte-for-byte. The
  shipped `dock` row is the in-table neutral spot, so the skeleton's `dock`-keyed
  determinism fixtures stay green unchanged. *(Narration now names the spot — intended.)*
- **D — one resolver, gear and spot are orthogonal levers.** `fishing_power`/`bite_luck`
  (earned gear) and the spot profile (place) multiply independently; neither gates. The
  gradient holds *within* every spot (gear still quickens bites / biases the tail) and
  *across* spots (place sets the baseline), shown in §5.

## 5. Sim-pin table (evidence)

All numbers below are **new design, sim-pinned in-repo** — *not* preserved-from-oracle.
Reproduce with `python3 -m games.fishing.sim.catch_sim` (deterministic; the fast test
`tests/fishing/test_catch_sim.py` re-asserts the bounds over a smaller fixed sweep).

These bounds are pinned from *this slice's* sim run. With spot biomes the gradient is real
and ordered (not trivially wide), so the bands are honest — tight enough to redden on a
profile regression, with margin for the fast test's small-sweep sampling noise.

### 5a. Aggregate across spots (the whole-economy view · 48,000 casts/tier)

| Metric | Pinned bound | Sim result |
|---|---|---|
| Bite rate — fresh (aggregate) | 0.48–0.62 | **55.66%** |
| Bite rate — master (capped <1) | 0.70–0.88 | **79.86%** |
| Bite-rate gradient (bite_luck lever) | master > geared > fresh | **79.9% > 63.7% > 55.7%** |
| Rare-tail share of bites (fishing_power) | master > geared > fresh; master < 0.45 | **28.9% > 24.6% > 21.5%** |
| Mean caught size — grows with gear | master ≥ geared ≥ fresh | **27.9 ≥ 26.4 ≥ 25.4** |
| Gear cap | `fishing_power ≤ 6`, `bite_luck ≤ 3` | **6 / 3 (single charm)** |
| Energy per cast | = `CAST_COST` (2) | **2.00** |

### 5b. Per-spot biome sim-pin (zero-gear "fresh" baseline)

The spot profile is the lever here: same gear, different biome. Bounds are re-asserted by
`tests/fishing/test_catch_sim.py` over the small sweep.

| Spot | Fresh bite rate (bound) | Result | Fresh rare-tail share (bound) | Result | Mean size |
|---|---|---|---|---|---|
| `tide_pool` | 0.60–0.72 | **65.52%** | 0.03–0.13 | **8.11%** | **21.4** |
| `dock` (neutral) | 0.48–0.60 | **54.36%** | 0.15–0.27 | **20.44%** | **25.2** |
| `deep_water` | 0.40–0.52 | **47.12%** | 0.34–0.48 | **41.32%** | **31.0** |

**Ordered gradients (pinned):** bite rate `tide_pool > dock > deep_water`; rare-tail share
and mean size `deep_water > dock > tide_pool`; and the gear gradient (bite ↑, rare-tail ↑
with gear) still holds *within* every spot. **Fair access holds at every (spot, tier):**
minnow **and** legend_carp are both landed everywhere — even `deep_water` fresh lands minnow
(28.5% of bites) and `tide_pool` fresh lands legend_carp (1.2%). No biome gates a species.

**The load-bearing story is bias-not-gate, now in two dimensions.** `dock` (the neutral
spot) reproduces the first slice's baseline (fresh minnow 49.7% / bass 29.9% / pike 15.0% /
legend 5.4%). Fishing a different *place* re-weights that — `deep_water` fresh is minnow
28.5% / bass 30.2% / pike 28.7% / legend 12.6% — and earning *gear* re-weights it again,
independently. Every species stays reachable at zero gear at every spot; advantage (gear or
local knowledge) is earned/chosen, never bought.

<details><summary>Full sim output (48,000 casts/tier · seeds 0–399 · spots {tide_pool, dock, deep_water} · 40 casts/spot)</summary>

```
casts per tier: 48,000
spots: tide_pool, dock, deep_water
species table: minnow, bass, pike, legend_carp
rare tail (size_rank ≥ 3): pike, legend_carp

[tide_pool] (bite rate · rare-tail share of bites · mean size):
  fresh    bite 65.52%  rare  8.11%  size  21.4  (bites=10,483)
  geared   bite 73.41%  rare  9.54%  size  22.1  (bites=11,746)
  master   bite 89.41%  rare 12.09%  size  23.1  (bites=14,306)
    species share of bites:
                 minnow         bass         pike  legend_carp
    fresh          64.21%       27.68%        6.91%        1.20%
    geared         60.51%       29.94%        7.93%        1.61%
    master         54.91%       33.01%        9.93%        2.16%

[dock] (bite rate · rare-tail share of bites · mean size):
  fresh    bite 54.36%  rare 20.44%  size  25.2  (bites=8,697)
  geared   bite 62.59%  rare 23.86%  size  26.3  (bites=10,014)
  master   bite 78.82%  rare 28.17%  size  27.8  (bites=12,611)
    species share of bites:
                 minnow         bass         pike  legend_carp
    fresh          49.66%       29.90%       15.01%        5.44%
    geared         44.98%       31.17%       16.84%        7.02%
    master         38.74%       33.08%       19.46%        8.71%

[deep_water] (bite rate · rare-tail share of bites · mean size):
  fresh    bite 47.12%  rare 41.32%  size  31.0  (bites=7,539)
  geared   bite 55.11%  rare 45.62%  size  32.3  (bites=8,817)
  master   bite 71.34%  rare 50.84%  size  33.8  (bites=11,414)
    species share of bites:
                 minnow         bass         pike  legend_carp
    fresh          28.51%       30.18%       28.74%       12.57%
    geared         24.69%       29.69%       30.57%       15.05%
    master         20.29%       28.87%       32.93%       17.91%

aggregate across spots (bite rate · rare-tail share · mean size):
  fresh    bite 55.66%  rare 21.49%  size  25.4  (bites=26,719)
  geared   bite 63.70%  rare 24.63%  size  26.4  (bites=30,577)
  master   bite 79.86%  rare 28.92%  size  27.9  (bites=38,331)

mean energy cost per cast: 2.00
```

Tiers are built through the real `equipment` model (`compute_stats` on the fishing charm
ladder), so every stat is exactly what a player who *earned* that gear would have —
`geared` = one `fishing charm` (fp 2 / bl 1); `master` = one `master angler charm`
(fp 6 / bl 3). The same per-cast rng stream faces every tier at a given spot (apples-to-apples).

</details>

## 6. No pay-to-win

The resolver takes **no** coin/purchase/spend/premium input — its signature exposes no
such lever (asserted by `test_resolver_exposes_no_spend_or_purchase_lever`). The *only*
inputs that improve a cast are `EffectiveStats.fishing_power` / `bite_luck`, which come
solely from **gear earned in-domain**. Crucially the lever is a **bias, not a gate**: a
zero-gear angler still lands every species across the common range (and even the
legendary tail), while gear only shifts the distribution and quickens bites (§5). Gear
stats are capped at the single-charm ceiling (`MAX_FISHING_POWER` / `MAX_BITE_LUCK`), so
no loadout can push fishing past the sim's bounds. (Founding plan Q-0039/Q-0190.)

## 7. Deferred to later slices

- **Multi-cast state** — bite streaks, per-spot depletion/cooldown, bait/rod consumables,
  weather windows. These track state *across casts* → a host/workflow concern, not pure
  domain. The resolver stays per-cast; the workflow decides *whether/when* to call it.
- **~~A richer species table + spot biomes~~ — spot biomes DELIVERED** (this update:
  `spots.py` + the §Spot biomes model + the §5b per-spot sim-pin). A *richer species table*
  (more rows, size records) stays deferred — the shape already supports it by adding rows.
- **Workflow + host wiring** — the audited op that debits `energy_cost` and adds the
  `catch` in one transaction (Layer 2), and the superbot-next command/panel binding
  (Layer 3). This slice ships only the pure core they build against.
- **Shared-RNG extraction** — promote `fishing_seed`'s splitmix derivation to
  `games/shared/rng.py` with all three call sites migrated
  (`docs/ideas/shared-deterministic-rng-seam-2026-07-10.md`).

## 8. Verification

- `python3 -m pytest tests/fishing/ -q` → **64 passed**.
- `python3 -m pytest tests/ games/exploration/tests/ -q` → **248 passed** (no regression).
- `python3 -m pytest tests/ games/exploration/tests/ --collect-only -q | grep -cE '::'` →
  **248** (the ORDER-001 count floor, bumped 230 → 248 for the +18 spot-biome tests).
- `python3 -m games.fishing.sim.catch_sim` → the §5 per-spot distributions (deterministic).
