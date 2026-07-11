# 2026-07-11 · Fishing walking skeleton (games/fishing/)

> **Status:** `in-progress`
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

_TODO — fill on the final content commit._

## Sim-pin headline

_TODO — paste the real `python3 -m games.fishing.sim.catch_sim` headline on the final commit._

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
