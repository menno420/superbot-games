# 2026-07-11 · Fishing spot biomes (data-driven catch profiles, sim-pinned)

> **Status:** ✅ `complete`
>
> 📊 Model: Claude Opus · 2026-07-11T01:26:10Z · fishing spot biomes (data-driven catch profiles, sim-pinned)

## Goal

Extend the shipped fishing skeleton (`games/fishing/core/`, PR #25) with **data-driven
fishing spots (biomes)** that give the already-present `spot_id` argument MEANING: the
spot you fish biases *what* you catch. All player-visible nouns (spot name/emoji/flavour)
and all balance numbers (per-species weight multipliers, a per-spot bite modifier) live
as DATA in a new `games/fishing/core/spots.py`, mirroring `species.py`. The resolver reads
the spot profile and applies it deterministically; an unknown/None `spot_id` falls back to
a neutral default profile that reproduces prior skeleton behaviour byte-for-byte. No
pay-to-win: every spot leaves the common species reachable at zero gear, and
`fishing_power`/`bite_luck` remain the only (earned) gear levers. Sim-pinned per spot;
one merged-on-green PR (Q-0267 theme-readiness, deterministic, stdlib-only, NO LLM).

## What shipped

- **`games/fishing/core/spots.py`** — THE SPOT DATA (mirrors `species.py`): a `Spot` frozen
  dataclass + three neutral-id biome rows — `tide_pool` (warm shallows, favours the
  small/common tail, `bite_bias` +0.10), `dock` (the neutral **identity** middle spot, empty
  weights / 0.0 bias), `deep_water` (cold deeps, favours the big/rare tail, `bite_bias`
  −0.08). Each row carries display nouns (name/emoji/flavor) + a catch profile
  (`{species_id: multiplier}` over `rarity_weight`). `__post_init__` enforces every
  multiplier > 0 (fair access — bias, never gate) and freezes the mapping. `profile_for`
  returns the neutral `DEFAULT_SPOT` for an unknown/`None` id (no raise, exact identity).
- **`games/fishing/core/catch.py`** — the resolver now reads the spot profile:
  `_bite_chance(stats, spot)` adds `spot.bite_bias` and clamps to
  `[MIN_BITE_CHANCE (0.30), MAX_BITE_CHANCE (0.90)]`; `_pick_species(stats, spot, rng)`
  multiplies each species weight by `spot.multiplier_for(id)` (orthogonal to the gear lever);
  narration is assembled from the spot row's + species row's DATA (names the spot, no
  per-spot logic branch). Default profile → the first slice's mechanical outcome
  byte-for-byte (identity ×1.0 / +0.0).
- **`games/fishing/sim/catch_sim.py`** — sweeps each **spot × tier × seed**, aggregating
  per `(spot, tier)` (plus a cross-spot aggregate); `format_report` prints per-biome
  sections. Deterministic (injected per-cast rng).
- **`tests/fishing/test_spots.py`** (+13) — neutral ids, `dock`-is-identity, per-spot
  fair-access (all species reachable, ≤0 multiplier rejected), spot biases the rare tail in
  order, data-swap changes weighting not determinism, unknown/`None` → default no raise,
  cross-spot divergence, injected-rng still applies the profile.
- **`tests/fishing/test_catch_sim.py`** (+5) — per-spot pinned bounds: bite-rate /
  rare-tail / mean-size gradients across spots, the gear gradient within each spot, and
  fair access at every `(spot, tier)`.
- **`docs/design/fishing-catch-skeleton.md`** — a `## Spot biomes` section (model + four
  decide-and-flagged decisions) and a §5b per-spot sim-pin table with the pasted sim output
  in a `<details>`; §7's deferred "spot biomes" line marked DELIVERED; Status badge + counts
  refreshed. **`.github/workflows/tests.yml`** — ORDER-001 count floor 230 → 248 (+18).
- **Verification:** `pytest tests/fishing/` → 64 passed; `pytest tests/ games/exploration/tests/`
  → 248 passed (= floor); `bootstrap.py check --strict` → exit 0; sim deterministic. Existing
  fishing + adapter tests stayed **green unchanged** (`dock` neutral identity preserved the
  determinism fixtures).

## 💡 Session idea

Making the *middle* spot (`dock`) a genuine neutral-identity profile — empty weight
overrides, zero bite bias — lets the two flanking biomes (`tide_pool` favours the small
common tail, `deep_water` favours the big rare tail) carry all the bias while the existing
skeleton's `dock`-keyed determinism fixtures stay **byte-identical**. "Default reproduces
prior behaviour" becomes a provable property (identity multiply-by-1.0 / add-0.0 is exact
in IEEE), not a claim — the same capture-before/assert-after discipline the mining
narration slice used, applied to a data-additive change instead of a relocation.

## ⟲ Previous-session review

Builds directly on the fishing skeleton (PR #25 — `species.py`/`catch.py`/`rng.py`/
`catch_sim.py`, whose `resolve_cast(seed, spot_id, …)` already takes `spot_id` but does not
yet key balance on it) and on the fishing→inventory adapter (PR #33): the adapter maps
`Catch → Grant` off species ids only, so adding spots (which change *weighting*, never the
species id set) leaves it untouched. No conflict with the shared-inventory seam (PR #29) or
the mining narration→data slice (PR #31). This is the "richer species table + spot biomes"
line the skeleton design doc §7 explicitly deferred to a later slice — now delivered.

## Guard recipe

Behaviour-preservation anchor: the default/neutral spot profile
(`games.fishing.core.spots.DEFAULT_SPOT`) MUST reproduce the pre-change resolver — the
existing `tests/fishing/test_determinism.py` / `test_theme_data.py` / `test_no_pay_to_win.py`
fixtures key on `dock`, which is a neutral-identity spot, so they stay green unchanged. The
new per-spot bounds live in `tests/fishing/test_spots.py` + `test_catch_sim.py` and in
`docs/design/fishing-catch-skeleton.md` §5; regenerate with `python3 -m games.fishing.sim.catch_sim`
if a spot data row changes intentionally.
