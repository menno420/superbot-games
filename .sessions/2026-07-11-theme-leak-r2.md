# 2026-07-11 · Theme leaks R2 — mining grid/market/taxonomy nouns → data

> **Status:** ✅ `complete`
>
> 📊 Model: Claude Opus · 2026-07-11T01:43:42Z · clear Q-0267 theme leaks R2 (grid/market/taxonomy nouns → data)

## Goal

Clear the R2 findings of the Q-0267 theme-slot audit
(`docs/audit/theme-slot-readiness-2026-07-11.md` §5): the three remaining
player-visible nouns/labels still inlined in mining branching logic —

- `grid.py:177` — the barren-cell flavour literal
  (`"The rock here is barren — slim pickings."`) inlined in `apply_cell_to_loot`,
  a stray from its sibling `_STRIKE_NOTE`/`_FEATURE_LABEL` tables;
- `taxonomy.py:75-82` — the menu-category nouns
  (`"Weapons"/"Armour"/"Tools"/"Structures"/"Items"`) returned as literals from
  `category_of`'s `if`/`elif`;
- `market.py:181-192` — the shop-section labels
  (`"⚔️ Weapons & shields"/"🛡️ Armor"/"🧰 Tools & supplies"`) as a dict literal
  inside `shop_sections`.

Each moves into a clearly-marked module-level DATA table keyed on a **neutral
id**; the function bodies become table lookups holding **zero** player-visible
string literals. Pure relocation — every player-facing string stays
**byte-identical**, no outcome/mechanic change. One merged-on-green PR.

## What shipped

- **`games/mining/core/grid.py`** — the barren-cell flavour literal
  (`"The rock here is barren — slim pickings."`), previously inlined in the
  `apply_cell_to_loot` branch (`:177`), moved into a new `# --- cell flavour notes`
  `_BARREN_NOTE` data table keyed on the neutral `CellFeature` enum, a sibling of
  `_STRIKE_NOTE`. The branch now returns `_BARREN_NOTE[cell.feature]` — no player
  literal in the function body. Byte-identical; loot outcome untouched.
- **`games/mining/core/taxonomy.py`** — the menu-category nouns
  (`"Weapons"/"Armour"/"Tools"/"Structures"/"Items"`), previously returned as
  literals from `category_of`'s `if`/`elif` (`:75-82`), moved into a
  `# --- menu category labels` `_CATEGORY_LABEL` table keyed on **neutral slug
  ids** (`weapons`/`armour`/`tools`/`structures`/`items`). The branch resolves a
  slug from the item's slot/kind and the function reads the label off the table.
  The five values equal `CATEGORY_ORDER` (the labels that already key
  `CATEGORY_EMOJI`) — byte-identical, noun-keyed tables untouched.
- **`games/mining/core/market.py`** — the shop-section titles
  (`"⚔️ Weapons & shields"/"🛡️ Armor"/"🧰 Tools & supplies"`), previously a dict
  literal inside `shop_sections` (`:181-192`), moved into a
  `# --- shop section labels` `SHOP_SECTION_LABEL` table keyed on **neutral
  section ids** (`weapons`/`armor`/`tools`), with `_SECTION_ORDER` fixing display
  order. The function groups rows on the neutral ids and reads titles off the
  table. Byte-identical labels; grouping/order/`if rows` filter unchanged.
- **Tests (+9, `tests/mining/`).** Each module gets three guards mirroring the R1
  narration slice: (1) a **byte-identity** assert against a hand-listed golden set
  of the exact pre-refactor literals; (2) a **swap-a-row** load-bearing test (re-skin
  the data row → only that label changes, every outcome/grouping field identical);
  (3) an **AST "no inline player-label"** guard proving the function body emits no
  string constant that is a value of its label table. `test_grid.py` +3,
  `test_items_market.py` +3, new `test_taxonomy.py` +3.
- **CI floor** (`.github/workflows/tests.yml`) — collected-count floor 248 → 257
  (+9, theme leak R2).
- **Audit doc** (`docs/audit/theme-slot-readiness-2026-07-11.md`) — the three ⚠️
  rows (barren flavour / shop-section labels / menu-category nouns) flipped to ✅
  RESOLVED (R2, this PR); §3 leaks #3–#5 struck through; headline tally
  16 ✅·12 ⚠️·2 ❌ → 19 ✅·9 ⚠️·2 ❌; §5 R2 roadmap line marked SHIPPED.
- **Verification:** `pytest tests/mining/` → 88 passed (79 + 9, existing 79 green
  UNCHANGED); `pytest tests/ games/exploration/tests/` → 257 passed (= new floor);
  `bootstrap.py check --strict` → exit 0. Pure relocation — no mechanic, weight,
  price, or outcome touched.

## 💡 Session idea

Where a display noun currently doubles as its own dictionary key (mining's menu
categories: `"Weapons"` is both the returned label AND the `CATEGORY_EMOJI` /
`CATEGORY_ORDER` key), the cheapest theme-clean move is to split a **neutral
slug id** (`"weapons"`) for the branch to resolve, and keep a one-line
`slug → label` table for the display string — the branch never spells the
label, the label lives in data, and the pre-existing noun-keyed tables stay
untouched (minimal blast radius). The byte-identity proof is then trivial: the
lookup returns the exact old literal, pinned by a hand-listed golden set.

## ⟲ Previous-session review

Builds on the mining narration→data slice (PR #31, R1) which relocated the
encounter narration + "creature" noun into `encounters._NARRATION`, and mirrors
its verification discipline (golden byte-identity + a "no inline player-strings"
AST guard + a swap-a-row load-bearing test). This slice is the R2 line the audit
roadmap (§5) sequenced right after R1: the three smallest stray-literal leaks in
mining's grid/market/taxonomy. Does not touch `encounters.py` (already R1-clean)
nor the noun-as-key identity leak (R5, owned by the inventory-contract
migration). No overlap with the fishing spot-biomes slice (PR #35).

## Guard recipe

Behaviour-preservation anchors: (1) the three extracted strings equal their
pre-refactor literals byte-for-byte, pinned by hand-listed golden asserts in
`tests/mining/test_grid.py`, `test_items_market.py`, and a new
`test_taxonomy.py`; (2) an AST "no inline player-strings" guard over
`apply_cell_to_loot` / `shop_sections` / `category_of` proves the branch bodies
emit copy only via the data table; (3) a swap-a-row test per module proves the
table is the *only* label source (re-skin changes only the label, outcome
untouched). Existing mining suite (79) must stay green **unchanged** — these are
pure relocations, so any test that pinned a literal still passes.
