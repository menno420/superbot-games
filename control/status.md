# superbot-games · status

updated: 2026-07-11T01:49:48Z
phase: theme leaks R2 cleared — mining's grid/market/taxonomy player-visible nouns moved out of branching logic into swappable DATA tables keyed on neutral ids; READY PR to main (green-pending)
health: green — full suite 257 pure-domain tests pass (88 mining + 44 fishing core + 20 fishing inventory adapter + 48 exploration + 57 tests/shared/inventory/); `bootstrap.py check --strict` exit 0
last-shipped: theme leaks R2 cleared (grid/market/taxonomy → data) — `grid._BARREN_NOTE` (barren flavour, keyed on `CellFeature`), `taxonomy._CATEGORY_LABEL` (menu-category nouns, keyed on neutral slug ids), `market.SHOP_SECTION_LABEL` (shop-section titles, keyed on neutral section ids). Each branch now emits only neutral ids and reads the label off the table; every string byte-identical to its pre-refactor literal, no mechanic/weight/price/outcome change (Q-0267 R2, audit roadmap §5)
orders: acked=001,002 done=001,002
blockers: none
notes: CI count floor bumped 248 → 257 (+9 theme-R2 tests: 3 per module — a hand-listed byte-identity golden, a swap-a-row load-bearing test, and an AST "no inline player-label" guard). Existing mining suite (79) stayed green UNCHANGED — pure relocations, wording byte-identical. Audit `docs/audit/theme-slot-readiness-2026-07-11.md` R2 rows flipped ⚠️→✅ (barren flavour / shop-section labels / menu-category nouns); headline tally 16 ✅·12 ⚠️·2 ❌ → 19 ✅·9 ⚠️·2 ❌. Did NOT touch `encounters.py` (R1-clean) nor the noun-as-key identity leak (R5, owned by the inventory-contract migration).

## Boot record
Landed on origin/main HEAD `3e46e66` (PR #35 fishing spot biomes; PR #33 fishing → shared
inventory adapter; PR #31 mining narration→data; PR #29 shared inventory seam PR-1; PR #28
theme-slot audit; PR #25 fishing skeleton). Branch `feat/theme-leak-r2` off origin/main.
This seat owns all of `games/**` and reports here (single-seat status file).

## Last shipped — theme leaks R2 (2026-07-11, mining nouns → data)
- **`games/mining/core/grid.py`** — barren-cell flavour literal moved from the
  `apply_cell_to_loot` branch into a `_BARREN_NOTE` data table keyed on `CellFeature`
  (sibling of `_STRIKE_NOTE`); the branch returns the lookup, no inline literal.
- **`games/mining/core/taxonomy.py`** — `category_of` now resolves a neutral slug id
  from the item's slot/kind and reads the display noun off `_CATEGORY_LABEL`; the five
  labels equal `CATEGORY_ORDER`, byte-identical, noun-keyed tables untouched.
- **`games/mining/core/market.py`** — `shop_sections` groups rows on neutral section ids
  and reads titles off `SHOP_SECTION_LABEL` (`_SECTION_ORDER` fixes display order);
  labels/grouping/order byte-identical.
- **+9 tests** (`test_grid.py`, `test_items_market.py`, new `test_taxonomy.py`): per module
  a byte-identity golden, a swap-a-row load-bearing test, and an AST no-inline-label guard.
- **No pay-to-win / no mechanic change:** a re-skin changes what a noun is *called*, never
  what it *does* or costs — every weight, price, gate, and outcome is untouched (Q-0039 /
  Q-0190). Determinism code not touched; only string source moves inline → table lookup.

## Orders
`orders: acked=001,002 done=001,002`
- ORDER 001 — done (merged #24). ORDER 002 — done (superseded by Q-0265).

## Queue (inherited)
- done: fishing skeleton (#25); inventory contract design doc (#26); theme-slot audit (#28);
  inventory seam PR-1 (#29); mining narration table R1 (#31); inventory migration PR-2 —
  fishing adapter (#33); fishing spot biomes (#35); **mining theme leaks R2** (this PR).
- next (inventory migration): **PR-3** mining catalog adapter (closes the Q-0267 §1a gap) →
  **PR-4** quest adapter → **PR-5** encounter typed grant → **PR-6** fish→mining bridge fix.
  Also queued (theme-audit roadmap): R3 fishing status scaffold; R4 de-dupe count-in-prose.
  Fishing follow-ups: a richer species table and multi-cast state (streaks, per-spot
  depletion) stay deferred (§7).
