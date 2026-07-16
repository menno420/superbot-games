---
state: promoted
origin: consumer:menno420/superbot
shipped_pr: null
shipped_repo: null
merged_date: null
outcome: open
---

# Shared deterministic-RNG seam in games/shared (2026-07-10)

> **Status:** `ideas`
>
> **State:** built · in-flight in PR
> [#150](https://github.com/menno420/superbot-games/pull/150) (2026-07-16). The
> ship fields stay null until the PR merges — the merge flips them to
> `outcome: shipped` per this backlog's frontmatter convention.

**Built (PR #150):** mining's integer splitmix64 `(seed, coords…)` mix was
extracted **verbatim** into `games/shared/rng.py` (`mix64` + `cell_seed`), and
mining's two call sites — `games/mining/core/grid.py` (`_cell_seed`) and
`games/mining/core/encounters.py` (`encounter_seed`, plus deletion of its
duplicate private `_cell_seed`) — now consume it with byte-identical outputs
(a 7 658-record sequence hash held equal before/after). Focused unit tests
live in `tests/shared/rng/`. Deliberately scoped to mining: exploration's RNG
is the *canonical* splitmix64 (a different algorithm), and fishing's clean copy
is the named next migration, so this stayed a contained, behavior-preserving
refactor rather than a fleet-wide rewrite.

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
