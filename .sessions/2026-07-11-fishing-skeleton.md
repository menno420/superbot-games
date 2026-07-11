# 2026-07-11 · Fishing walking skeleton (games/fishing/)

> **Status:** `complete`
>
> 📊 Model: Claude Opus · 2026-07-11T00:11:50Z · fishing walking skeleton reusing mining's energy/determinism substrate

## Goal

Ship the **first fishing slice** as a self-contained pure package `games/fishing/core`
(+ a `sim/` harness + tests), mirroring the shipped mining substrate rather than
duplicating it. Deliver ONE merged-on-green PR. The slice must:

- Reuse mining's cross-game **energy engine** (`games.mining.core.energy`) directly for
  the energy cost of a cast — no parallel fuel model.
- Reuse the cross-game **`EffectiveStats`** seam (`games.mining.core.equipment`),
  reading the already-shipped `fishing_power` / `bite_luck` fields (Q-0175) as the
  gear knobs — no new stat block.
- Own a **deterministic catch resolver** (`resolve_cast`): deterministic code owns every
  outcome (NO LLM anywhere), `rng=None` → a byte-reproducible default stream from an
  **independent** splitmix64 `fishing_seed(seed, spot_id)`, injectable `rng` for live
  variance — mirroring mining's `encounters.resolve` pattern.
- Keep every player-visible noun (species names, emoji, flavour) in a **data table**
  (`species.py`) keyed on neutral ids (Q-0267 theme-readiness): mechanics key on ids,
  nouns live in data.
- Be **sim-pinned**: `sim/catch_sim.py` sweeps casts × gear tiers, aggregates the catch
  distribution, and `tests/fishing/` re-asserts the bounds (the mining sim-pin discipline).
- Prove **no pay-to-win** (Q-0039/Q-0190): `fishing_power` biases the distribution toward
  rarer/bigger fish but never gates access; a zero-gear player still catches across the
  common range; gear stats stay within sim-pinned caps.

## What shipped

- **`games/fishing/` pure package** (mirrors `games/mining/core`), all stdlib-only, no
  Discord/DB/IO:
  - **`core/species.py`** — THE THEME DATA: a four-row species table (`minnow` / `bass` /
    `pike` / `legend_carp`) keyed on neutral ids; every player-visible noun (name, emoji,
    flavour, `size_rank`, `rarity_weight`) is a data row (Q-0267). Re-theme = data edit.
  - **`core/rng.py`** — `fishing_seed(seed, spot_id)`: an INDEPENDENT splitmix64 stream
    (mining's family + a fishing-domain salt), integer-only → process-independent. Tagged
    a promotion candidate for `games/shared/rng.py`.
  - **`core/catch.py`** — THE RESOLVER: `resolve_cast(...) -> CastOutcome(bit, catch,
    narration, energy_cost)`. Deterministic code owns every outcome (NO LLM anywhere);
    `rng=None` → the deterministic `fishing_seed` stream, injectable rng for live variance.
    Bite roll (raised by `bite_luck`), `fishing_power`-biased weighted species pick, size
    roll, narration assembled from species DATA. Honest energy gate: too tired → no-bite,
    never raises.
  - **`sim/catch_sim.py`** — a pure seeded harness sweeping casts × gear tiers
    (fresh / fishing charm / master angler charm via the real `equipment` model),
    aggregating bite rate, species distribution, mean size, energy economy.
- **REUSED substrate (imported directly, not duplicated):**
  `games.mining.core.energy` (a cast spends `CAST_COST` through the shared engine — one
  energy economy; "cooked fish" already refills it) and
  `games.mining.core.equipment.EffectiveStats` (`fishing_power` / `bite_luck`, Q-0175 —
  the only advantage levers). **EXTENDED** (new independent pattern): a fishing-salted
  splitmix64 stream + the species theme-data table + the catch resolver/sim, mirroring
  mining's determinism + sim-pin patterns.
- **`tests/fishing/`** — 26 tests: determinism (incl. subprocess process-independence),
  reused-energy contract + honest states, theme-data-drivenness, no-pay-to-win (bias not
  gate; gear caps), sim-pinned bounds. **Full suite 99 passed** (73 mining + 26 fishing);
  collected by the existing `pytest tests/` gate with ZERO `tests.yml` edit.
- **`docs/design/fishing-catch-skeleton.md`** — the catch model, decisions, the gear
  seam, the determinism scheme, the sim-pin table (real sim output pasted), the
  no-pay-to-win statement, deferred slices, and exact verification commands.

## Sim-pin headline

Bias-not-gate, proven over 64,000 casts/tier: a **zero-gear angler already lands every
species** (minnow 50% / bass 30% / pike 15% / legend_carp 5% of bites); earned gear only
*shifts* toward the rare tail (master: 39/32/20/8%) and quickens bites (rate 54.7% fresh →
78.9% master, capped <90%). Mean size 25.0 → 27.6; every species reachable at every tier;
gear capped at one charm (fp 6 / bl 3); energy 2.00/cast through the reused engine. The
gradient is a *progression* incentive, never a paywall — advantage is earned, never bought.

## 💡 Session idea

`species.py` is a second independent witness (after mining's ore/depth tables and
exploration's content) that every game lane wants the same shape: **neutral-id mechanics
+ a data-only noun table**. The `fishing_seed` splitmix helper is likewise the *third*
hand-rolled copy of the same splitmix64 `(seed, …)` derivation (mining grid, mining
encounters, now fishing). Both reinforce the already-captured
`docs/ideas/shared-deterministic-rng-seam-2026-07-10.md`: promote the splitmix
derivation + its subprocess process-independence test into `games/shared/rng.py` and
migrate all three call sites in one byte-identical refactor. This slice deliberately
re-rolls it locally (volume-first) but tags it in the module docstring as promotion-ready
so the extraction has three concrete consumers when it lands.

## ⟲ Previous-session review

The grid-encounters slice (#11) set the template this session follows almost verbatim:
a pure resolver with a deterministic-default/injectable rng, a per-subsystem salt for an
independent stream, sim-pinned constants with a header comment pointing at sim+doc, and a
fast bounded test re-asserting the sim. Reusing that shape wholesale is exactly the
"leave the next session better-equipped" payoff — fishing needed no design re-litigation.
The one sharpening it flagged (a `plan`-doc that never flips to shipped is silent drift)
is honoured here: this card is born-red and flips to `complete` only when the code lands,
and the design doc is written IMPLEMENTED-on-merge, not left as a stale plan.
