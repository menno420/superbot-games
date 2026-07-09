# 2026-07-09 · Grid-encounters first slice (games/mining/core/encounters.py)

> **Status:** `in-progress`
>
> automation-agent · high · build · lane: game-mining · branch: mining/grid-encounters

## Goal (in-progress — born-red hold)

Build the **grid-encounters** extension's first slice as PURE DOMAIN, stacked on #5's
`mining/port-pure-domain`. Layer a live-rollable **encounter resolver** on top of the
seed-deterministic grid: `games/mining/core/encounters.py` resolves an `EncounterOutcome`
from a `Cell` (keyed off `CellFeature`), `EffectiveStats`, remaining energy, and an
injected/derived `rng`. Reuse the existing reward/item tables (no parallel economy),
`EffectiveStats.damage/defense/max_health` for hazard combat, and the grid's splitmix64
seed convention for reproducibility. Add a pure sim harness
(`games/mining/sim/encounters_sim.py`), sim-pin every new balance number, and add
`tests/mining/` coverage (determinism incl. subprocess, additive-safety, distributions
within pinned bounds, no-pay-to-win, purity). Mark the seam IMPLEMENTED in the design doc.

_This card opens born-red on purpose (Q-0133 analogue); flipped to `complete` as the
deliberate final step once the work + close-out docs are in._
