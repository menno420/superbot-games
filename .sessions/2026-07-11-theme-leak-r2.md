# 2026-07-11 · Theme leaks R2 — mining grid/market/taxonomy nouns → data

> **Status:** 🔴 `in-progress` (born-red)
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

_(filled in on the final content commit)_

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
