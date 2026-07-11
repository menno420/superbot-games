# Fishing catch — walking skeleton (IMPLEMENTED)

> **Status:** `reference` · lane: game-fishing · 2026-07-11 · (walking skeleton IMPLEMENTED)
>
> The first fishing slice: a sparse, data-driven **catch** resolver that reuses mining's
> shipped cross-game substrate (the energy engine + the `EffectiveStats` gear model) and
> mirrors mining's determinism/sim-pin patterns. This slice ships **pure domain only** —
> resolver + species data + sim + tests. Workflow and host wiring are deferred (§7).
> Companion to `docs/design/mining-grid-encounters.md` (whose patterns it follows) and the
> shared-RNG idea `docs/ideas/shared-deterministic-rng-seam-2026-07-10.md`.

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
- **`tests/fishing/`** — determinism (incl. a subprocess process-independence check),
  the reused-energy contract + honest states, theme-data-drivenness, no-pay-to-win, and
  the sim-pinned distributions. **26 tests**; the full suite is **99 passed** (73 mining
  + 26 fishing), collected by CI's existing `pytest tests/` with no workflow edit.

## 2. Catch model + Decisions

`resolve_cast` is a **per-cast** function:

1. **Energy gate** — if `energy < CAST_COST` (2), return the honest `_TOO_TIRED`
   no-bite outcome (`bit=False`, `energy_cost=0`); it never raises.
2. **Bite roll** — a bite fires with chance `BASE_BITE_CHANCE` (0.55), raised by earned
   `bite_luck` (`+BITE_LUCK_PER_POINT` = 0.08 each, capped `MAX_BITE_CHANCE` = 0.90). A
   miss is an empty cast (`bit=False`, `energy_cost=CAST_COST`) — you still spent the cast.
3. **Species pick** — a weighted pick over the species `rarity_weight`s, with each
   species' weight scaled by `(1 + fishing_power · POWER_BIAS_PER_POINT · (size_rank−1))`
   so `fishing_power` biases toward the bigger/rarer tail (rank-1 never boosted;
   `fishing_power=0` → the base weights exactly).
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

## 5. Sim-pin table (evidence)

All numbers below are **new design, sim-pinned in-repo** — *not* preserved-from-oracle.
Reproduce with `python3 -m games.fishing.sim.catch_sim` (deterministic; the fast test
`tests/fishing/test_catch_sim.py` re-asserts the bounds over a smaller fixed sweep).

**Skeleton note:** these bounds are pinned from *this slice's* sim run and are
**trivially wide** — they exist to redden CI on a balance regression, not to encode a
tuned economy. Tighten them as the species table and gear ladder grow.

| Metric | Pinned bound | Sim result (64,000 casts/tier) |
|---|---|---|
| Bite rate — fresh (base) | 0.48–0.62 | **54.71%** |
| Bite rate — master (bite_luck-raised, capped <1) | 0.70–0.88 | **78.93%** |
| Bite-rate gradient (bite_luck lever) | master > geared > fresh | **78.9% > 62.8% > 54.7%** |
| Rare-tail share of bites (fishing_power lever) | master > geared > fresh; master < 0.45 | **28.1% > 23.2% > 20.0%** |
| Mean caught size — grows with gear | master ≥ geared ≥ fresh | **27.6 ≥ 26.0 ≥ 25.0** |
| Fair access — common species at every tier | minnow + bass landed by all tiers | **yes (all tiers)** |
| Fair access — bare angler reaches whole table | fresh catches all 4 species | **yes** |
| Gear cap | `fishing_power ≤ 6`, `bite_luck ≤ 3` | **6 / 3 (single charm)** |
| Energy per cast | = `CAST_COST` (2) | **2.00** |

**The load-bearing story is bias-not-gate.** A zero-gear angler already lands every
species — minnow 50% / bass 30% / pike 15% / legend_carp 5% of bites — and gear only
*shifts* that toward the rare tail (master: 39% / 32% / 20% / 8%) while quickening bites.
No species is ever locked behind gear; advantage is earned in-domain, never bought.

<details><summary>Full sim output (64,000 casts/tier · seeds 0–399 · spots {dock, deep_lake, reef, river_bend} · 40 casts/spot)</summary>

```
casts per tier: 64,000
species table: minnow, bass, pike, legend_carp
rare tail (size_rank ≥ 3): pike, legend_carp

per-tier outcomes (bite rate · rare-tail share of bites · mean size):
  fresh    bite 54.71%  rare 19.96%  size  25.0  (bites=35,013)
  geared   bite 62.80%  rare 23.23%  size  26.0  (bites=40,194)
  master   bite 78.93%  rare 28.14%  size  27.6  (bites=50,517)

per-tier species distribution (share of bites):
                 minnow         bass         pike  legend_carp
  fresh          50.08%       29.96%       14.91%        5.05%
  geared         46.12%       30.65%       16.87%        6.36%
  master         39.40%       32.46%       19.89%        8.26%

mean energy cost per cast: 2.00
```

Tiers are built through the real `equipment` model (`compute_stats` on the fishing charm
ladder), so every stat is exactly what a player who *earned* that gear would have —
`geared` = one `fishing charm` (fp 2 / bl 1); `master` = one `master angler charm`
(fp 6 / bl 3). The same per-cast rng stream faces every tier (apples-to-apples).

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
- **A richer species table + spot biomes** — more rows, spot-keyed weight tables (a
  `deep_lake` favouring the rare tail), size records. The data-driven shape already
  supports this by adding rows/tables; the skeleton keeps four species for stable bounds.
- **Workflow + host wiring** — the audited op that debits `energy_cost` and adds the
  `catch` in one transaction (Layer 2), and the superbot-next command/panel binding
  (Layer 3). This slice ships only the pure core they build against.
- **Shared-RNG extraction** — promote `fishing_seed`'s splitmix derivation to
  `games/shared/rng.py` with all three call sites migrated
  (`docs/ideas/shared-deterministic-rng-seam-2026-07-10.md`).

## 8. Verification

- `python3 -m pytest tests/fishing/ -q` → **26 passed**.
- `python3 -m pytest tests/ -q` → **99 passed** (73 mining + 26 fishing; no regression).
- `python3 -m pytest tests/ --collect-only -q | tail -3` → **99 collected** (fishing
  tests picked up by the existing `tests/` root gate — no `tests.yml` edit).
- `python3 -m games.fishing.sim.catch_sim` → the §5 distributions (deterministic).
