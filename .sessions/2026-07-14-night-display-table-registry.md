# 2026-07-14 · night test — display-table completeness registry: vocab and display tables stay in sync

> **Status:** `in-progress`
>
> 📊 Model: Fable · 2026-07-14T02:47:06Z · night-display-table-registry

Test slice implementing the display-table completeness registry card
idea from `.sessions/2026-07-14-night-coverage-mining-core-naming.md`,
verified unimplemented at main `f3fd346`: no `test_display_tables.py`
exists anywhere; the ItemKind↔`_KIND_EMOJI` relation is covered only
incidentally, and a new enum member / stat field / biome can today ship
without its player-facing label or glyph and fail only at render time
(a `KeyError` in an embed) or silently (a `.get` fallback).

Plan: `tests/mining/test_display_tables.py` in the registered
`tests/mining/` suite (per suite-discovery rules; a `tests/shared/`
root file would force a new overlapping suite). Pin the triples the
idea named — ItemKind values ⊆ `_KIND_EMOJI` keys (taxonomy),
`EffectiveStats` field names = `STAT_LABELS`/`STAT_GLYPHS` keys
(equipment), `_CATEGORY_LABEL` values = `CATEGORY_ORDER` =
`CATEGORY_EMOJI` keys (taxonomy) — plus every sibling vocabulary↔display
pair found by reading the mining core modules: `TYPE_EMOJI` keys ⊆
catalog base types, `Biome`↔`BIOME_LABELS`/`BIOME_EMOJI` (world),
`CellFeature`↔`_FEATURE_GLYPH`/`_FEATURE_LABEL` + `MAP_LEGEND`
completeness (grid), `_SECTION_ORDER`↔`SHOP_SECTION_LABEL` (market),
`BRANCHES`↔`BRANCH_LABELS` (skills). ≤10 tests; floor bump to collected
+ `docs/balance.md` regen before flip (gen-balance gate).
