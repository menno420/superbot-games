# 2026-07-14 · night coverage — games/mining/core/items.py (tests)

> **Status:** `in-progress`
>
> 📊 Model: Fable · 2026-07-14T00:26:10Z · night-coverage-mining-items

Coverage slice, re-confirmed this session at main `a51c5d5` (the 618-test
HEAD; re-measured again with slice A's 14 hub tests present — the numbers
are unchanged) before acting: `games/mining/core/items.py` sits at
**76%** (79 stmts, 19 missed: 340, 344, 355–356, 367, 381, 391–406,
419–427). The existing suites exercise the catalog itself (lookup,
classify, fish injection, the set-family rows) but leave these seams
dark:

- lines 340 + 344 — the `is_tool` / `is_consumable` predicates,
- lines 355–356 — `tool_tier` (known-tool tier and the unknown → 0 guard),
- line 367 — `total_value`'s sum (per-unit value × qty, zero/negative
  quantities skipped, unknown items at 1),
- line 381 — `next_tool_upgrade`'s off-every-ladder tail (None),
- lines 391–406 — the whole `sort_inventory` display helper (kind order,
  value-desc then name tiebreak, zero-qty rows dropped),
- lines 419–427 — the whole `summarize_inventory` section chunker.

Plan: ≤14 focused tests in a new `tests/mining/test_items_display.py`
(floor bumped in the same commit), pinning real behavior at EXISTING
catalog constants only (pickaxe/torch/wood/diamond/stone hut/lucky
charm rows). Tests only; a genuine bug would be pinned + HEADLINED, not
fixed here.
