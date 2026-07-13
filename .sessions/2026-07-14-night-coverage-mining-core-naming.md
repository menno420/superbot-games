# 2026-07-14 · night coverage — pin the mining name resolver + menu taxonomy (tests)

> **Status:** `in-progress`
>
> 📊 Model: Fable · 2026-07-13T23:14:44Z · night-coverage-mining-core-naming

Coverage slice under the ORDER 008(b) production-grade standing directive:
two small sibling modules in the mining core's naming/menu area, re-scanned
this session at main `c27b25a` (578 passed):

- `games/mining/core/names.py` — **37%** (19 stmts, 12 missed; lines 41,
  57–67): the entire fuzzy item-name resolver (`_normalize` +
  `resolve_item_name`) is untested — its exact → alias → `difflib`
  resolution order, the empty-pool guard, and the "only ever returns a
  member of *candidates*" contract are all unpinned.
- `games/mining/core/taxonomy.py` — **63%** (60 stmts, 22 missed; lines 84,
  107–111, 115, 119, 127–128, 135–140, 145–148, 156–157): `category_of` is
  pinned by the Q-0267 suite, but the rest of the 3-layer menu doctrine —
  `base_type`, `pluralize`, the emoji lookups, `grouped`'s rarity ordering,
  `types_by_category`'s body-order sort, `ordered_categories` — is not.

Plan: focused tests-only slice (roughly ≤14 tests across
`tests/mining/test_names.py` (new) and `tests/mining/test_taxonomy.py`)
pinning real behavior of the missed lines at EXISTING constants — no
gameplay-constant changes, no features. Close-out will record coverage
deltas, suite count from 578, idea, and previous-session review.
