---
state: captured
origin: consumer:menno420/superbot
shipped_pr: null
shipped_repo: null
merged_date: null
outcome: open
---

# Shared deterministic-RNG seam in games/shared (2026-07-10)

> **Status:** `ideas`
>
> **State:** captured (gen-2 night-prep seed by the grand-review session).

**One line:** extract mining's splitmix64 `(seed, coords…)` convention into a tiny
`games/shared/rng.py` helper (derive-a-child-rng + process-independence test pattern) so
exploration and every future game plugin get byte-reproducible, subprocess-stable
determinism from one audited implementation instead of rolling their own.

**Why:** both gen-1 lanes independently needed the same property — mining pinned it in
`games/mining/core/grid.py` (splitmix64, subprocess-tested), exploration built its own
injectable-RNG engine — and the grid-encounters slice (#11) already derives child rngs
from mining's convention. The superbot-next plugin contract expects deterministic
replayable domains; one shared seam means one place to prove it. Shared ground → follow
`docs/lanes.md`: claim first, name ONE executor.

**First step:** lift the splitmix64 derivation + the subprocess determinism test into
`games/shared/` with both existing call sites migrated in the same PR (pure refactor,
byte-identical outputs asserted).

**Size:** small (one module + two call-site migrations + tests).
