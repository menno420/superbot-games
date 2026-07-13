# 2026-07-14 · night coverage — pin the mining name resolver + menu taxonomy (tests)

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-13T23:17:50Z · night-coverage-mining-core-naming

Coverage slice under the ORDER 008(b) production-grade standing directive:
two small sibling modules in the mining core's naming/menu area, re-scanned
this session at main `c27b25a` (578 passed): `games/mining/core/names.py`
at **37%** (19 stmts, 12 missed; lines 41, 57–67 — the entire fuzzy
item-name resolver untested) and `games/mining/core/taxonomy.py` at
**63%** (60 stmts, 22 missed; lines 84, 107–111, 115, 119, 127–128,
135–140, 145–148, 156–157 — everything outside the Q-0267-pinned
`category_of`).

Shipped 14 focused tests. `tests/mining/test_names.py` (new, 7 tests) pins
the resolver's documented contract: exact-match normalization returning the
*candidate's* spelling, the empty-pool guard, alias resolution only when
the target is a candidate (so muscle-memory names never escape the pool),
difflib typo rescue at the default cutoff, `cutoff` respected (1.0 rejects
the near-miss 0.7 accepts), caller aliases *replacing* (not merging) the
default map, and every `ALIASES` value being a canonical
`items.catalog_names()` entry — the module comment's "values must be
canonical catalog names" is now machine-checked against rename drift.
`tests/mining/test_taxonomy.py` (+7 tests) pins the rest of the 3-layer
menu doctrine: `base_type` last-word-lowercase, the `pluralize` rules,
`type_emoji`'s type-table-then-kind fallback, `category_emoji`'s
empty-string unknown, `grouped`'s starter→iron→gold→diamond variant order,
`types_by_category`'s body order (sword→shield, helmet→boots), and
`ordered_categories` following `CATEGORY_ORDER` not input order. Coverage:
names.py 37% → **100%**, taxonomy.py 63% → **100%**; suite 578 → **592
passed**. `python bootstrap.py check --strict` pre-flip showed only this
card's designed born-red HOLD (plus the pre-existing never-exit-affecting
owner-action advisory). Tests-only: zero gameplay-constant changes, no
features. No bug found — one latent observation, pinned not changed:
`type_emoji`'s `"📦"` default is currently unreachable (every `ItemKind`
value has a `_KIND_EMOJI` row), so the tests pin the kind-fallback path
instead.

## 💡 Session idea

This slice met the same failure shape twice: a display table that must stay
in sync with a vocabulary defined elsewhere (`_KIND_EMOJI` must cover every
`items.ItemKind`; `names.ALIASES` values must stay inside the catalog —
the latter is now pinned, the former only incidentally). Add a
**display-table completeness registry**: one parametrized test module
(e.g. `tests/shared/test_display_tables.py`) with a registry of
(vocabulary, table, relation) triples — `ItemKind` values ⊆ `_KIND_EMOJI`
keys, `EffectiveStats` field names = `STAT_LABELS`/`STAT_GLYPHS` keys,
`_CATEGORY_LABEL` values = `CATEGORY_ORDER`/`CATEGORY_EMOJI` keys — so a
new enum member or stat field cannot ship without its player-facing label,
and the next such pair costs one registry line, not a bespoke test. Dedupe
check against recent cards: the telemetry outcome backfill, the CI coverage
ratchet, the detector-trip registry (assertion strength on invariant
predicates, not enum↔table sync), the machine-readable truth-stamp anchor,
the ledger-drift check, and the cook-leg SIM-REQUEST — none asserts
vocabulary↔display-table completeness; no card idea to date does.

## ⟲ Previous-session review

The previous session is the #98/#99 wave, re-verified against
`origin/main`: #98 (squash `07be6ed`) released the
night-coverage-mining-loadout claim exactly as promised — a 3-line
control-only deletion, fast lane, nothing else touched. #99 (squash
`6b2dbe7`) delivered the economy-sim coverage slice it claimed:
`tests/shared/sim/test_economy_sim.py` landed with the 11 tests its card
describes, and its numbers replay — this session's baseline scan at
`c27b25a` collected **578 passed** (matching the card's 567→578) and found
economy_sim absent from the <100% list (matching the card's 75%→100%
claim). The wave's one structural leftover — the `night-coverage-economy-
sim` claim file outliving the merge — was released early this session via
**#100** (`d4e0cf4`, squash `c27b25a`, tests job 86957828933 green), merged
by the auto-merge enabler. #99's card idea (the detector-trip registry) was
honestly deduped against here, not recycled. Nothing overstated.
