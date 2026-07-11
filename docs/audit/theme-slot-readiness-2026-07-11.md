# Theme-slot readiness audit — Q-0267 across the world games

> **Status:** `audit` · 2026-07-11
>
> A grounded, per-system audit of **theme-readiness** (Q-0267): for every
> player-visible noun surface in the world games — item / species / structure
> **names**, flavour text, emoji, titles, location names, and encounter
> narration — this doc records whether the noun lives in **DATA** (a
> module-level table keyed on a *neutral* id, swappable without touching
> mechanics) or is **hardcoded in CODE** (a string literal inside branching
> logic / a mechanic). Every verdict cites real code read this session
> (`file:line`). Nothing here is invented. This is an **audit doc only** — no
> system code, README, `tests.yml`, or inbox is changed; the fixes are a
> prioritized roadmap (§5) of future merged-on-green slices.
>
> Companion to the unified-item work in
> [`../design/world-inventory-resource-contract.md`](../design/world-inventory-resource-contract.md)
> (which already flagged the item-identity leak in its §1a). The rule audited
> against is the Q-0267 theme-readiness directive; the positive exemplar it
> names is mining's "engine-not-content" discipline.

---

## 1. What Q-0267 requires

**The rule.** Every *player-visible noun* must live in DATA — a module-level
table or map keyed on a **neutral string id** — never inlined in branching logic
or a mechanic. Player-visible nouns are: item / species / structure **names**,
flavour text, emoji, titles, location names, and encounter narration. Mechanics
key on the neutral id and read the noun off the data row; they never spell the
noun in an `if`/`elif` or bake it into an f-string in a resolver.

**Why (the core/skin split).** The fleet's target architecture is a *core*
(mechanics, sim-pinned numbers, determinism) that is theme-agnostic, plus a
*skin* (the noun/flavour/emoji data) that can be swapped to re-theme the game —
"bass" → "star-koi", a mine → a reef — **without touching mechanics or their
tests**. That is only possible if the skin is a pure data surface. Where a noun
is a code key or a literal inside a resolver, the core and skin are fused: you
cannot re-theme without editing (and re-testing) mechanics, and you cannot ship
two skins over one core. Q-0267 is the discipline that keeps them separable.

The audit classifies each surface as one of:

- **✅ DATA** — noun lives in a module-level table keyed on a neutral id;
  mechanics read it off the row. Swappable by editing data alone.
- **⚠️ MIXED** — a data table exists, but some literal leaks into logic (a stray
  narration string, a noun that doubles as the mechanic key, a noun baked into
  flavour prose, or a display label emitted from an `if`/`elif`).
- **❌ CODE** — the player-visible noun is hardcoded in branching logic / a
  mechanic, with no data table behind it.

---

## 2. Per-system audit table

Grounded in code read this session. This is the load-bearing section.

### 2a. Mining (`games/mining/core/`)

| Surface | Where the nouns live (`file:line`) | Verdict | Note |
|---|---|---|---|
| Item catalog identity | `items.py:66-224` (`_CATALOG`), keyed on `name.lower()` (`items.py:327`) | ❌ | The dict **key is the player noun** ("diamond", "lucky charm", "stone hut"); the same string is the catalog key, the inventory key, and the persisted key. Re-theming any item changes a mechanic key. Also flagged in the inventory-contract doc §1a. |
| Fish→catalog bridge | `items.py:293-303` (`register_fish_species`) | ⚠️ | Folds fishing species keyed on `s.name` (display noun), dropping the neutral `species_id` — the one cross-system seam loses the neutral id. |
| Stat labels | `equipment.py:103-114` (`STAT_LABELS`) | ✅ | Keyed on **neutral `EffectiveStats` field names** ("mining_power"); values are display strings. `describe_stats` reads them off the table (`equipment.py:375-381`). Exemplar. |
| Stat glyphs (emoji) | `equipment.py:118-129` (`STAT_GLYPHS`) | ✅ | Emoji keyed on the same neutral field names. Swappable. |
| Gear→stats registry identity | `equipment.py:139-208` (`_GEAR`), keyed on `item_name.lower()` (`:275,285`) | ❌ | Stat *values* are neutral data, but the **key is the item noun** — the same noun-as-key identity leak as `_CATALOG`. |
| Gear durability | `equipment.py:225-241` (`MAX_DURABILITY`) | ⚠️ | Data table, but keyed on the item display noun. |
| Tier vocabulary | `equipment.py:61` (`TIER_ORDER`) | ⚠️ | "bronze"/"iron"/…/"diamond" are theme nouns that double as mechanic tokens and are string-built into item names (`items.py:251` `f"{tier} {family}"`) and parsed back out (`equipment.py:299` `split()[0]`). |
| Ore weights | `rewards.py:21-28` (`ORE_WEIGHTS`) | ⚠️ | Weights are mechanics; keys are ore display nouns — the ore vocabulary is duplicated here and in `_CATALOG`. |
| Explore outcomes | `rewards.py:138-144` (`EXPLORE_OUTCOMES`) | ⚠️ | Module-level table (good), but each row bakes the **noun and the amount into flavour prose** ("found 1 gold in an abandoned camp!") *and* repeats them as the `(item, delta)` fields — re-theme requires rewriting prose. |
| Lucky-strike notes | `grid.py:108-111` (`_STRIKE_NOTE`) | ✅ | Narration **templates in a table** keyed on the neutral `CellFeature` enum; the ore is injected via `.format(ore=…)` (`grid.py:174`). Exemplar. |
| Feature labels / glyphs / legend | `grid.py:187-200` (`_FEATURE_GLYPH`, `_FEATURE_LABEL`, `MAP_LEGEND`) | ✅ | All keyed on the neutral `CellFeature` enum; `describe_cell` (`grid.py:252-257`) assembles from the label data. |
| Move phrases (locations) | `grid.py:57-64` (`_MOVE_PHRASE`) | ✅ | Direction phrases keyed on neutral direction tokens. |
| Barren-cell flavour | `grid.py` — `_BARREN_NOTE` table keyed on the neutral `CellFeature` enum; `apply_cell_to_loot` reads the note off it | ✅ | **RESOLVED (R2, this PR).** The barren literal ("The rock here is barren — slim pickings.") moved out of the branch into a sibling data table beside `_STRIKE_NOTE` — byte-identical, swap-a-row test proves the table is the only source. |
| Encounter narration + monster noun | `encounters.py` — `_NARRATION` table + `_CREATURE_NOUN` row, keyed on the neutral `_Narration` slot enum; `_narrate()` assembles copy, the `_resolve_*` fns hold zero player strings | ✅ | **RESOLVED (R1, this PR).** Narration relocated from the resolver branches into a module-level data table (mirroring `grid._STRIKE_NOTE`); the "creature" noun is now a swappable row. Byte-identical to the old literals (golden test `tests/mining/test_encounter_narration.py`). Re-theme = edit data only. |
| Energy restore values | `energy.py:31-35` (`RESTORE_VALUES`) | ⚠️ | Data table, but keyed on the food display noun ("ration", "cooked fish"). |
| Energy bar glyphs | `energy.py:132-136` (`bar()`) | ⚠️ | Emoji "⚡" + "▰▱" glyphs inlined in the formatting function (minor; ambient gauge, no theme noun). |
| Name aliases | `names.py:19-37` (`ALIASES`) | ✅ | Shorthand→canonical map in a module-level table (theme-coupled by nature, but data-resident). |
| Titles | `titles.py:72-114` (`_RULES` + `Title`) | ✅ | `Title(id, label, emoji, requirement)` keyed on **neutral ids** ("the_deep", "ironclad"); `display` (`:139-141`) assembles "emoji label" from data; predicates key on neutral branch ids. Exemplar — the cleanest surface in mining. |
| Gear-shop prices | `market.py:49-107` (`GEAR_SHOP`) | ⚠️ | Data table, keyed on item display nouns. |
| Shop section labels | `market.py` — `SHOP_SECTION_LABEL` table keyed on neutral section ids (`weapons`/`armor`/`tools`); `shop_sections` resolves the id then reads the title | ✅ | **RESOLVED (R2, this PR).** The section titles ("⚔️ Weapons & shields", "🛡️ Armor", "🧰 Tools & supplies") moved out of the in-function dict literal into a module-level data table — byte-identical, grouping/order unchanged. |
| Structures (names / level names) | `structures.py:50,55,60,120-130` (`_*_LEVEL_NAMES`, `_DEFS` registry) | ✅ | `StructureDef(key, display, ladder, level_names)` keyed on **neutral structure keys** (FORGE="forge"); level names ("Cozy Cabin", "Grand Hall") are data tuples; `display_name`/`level_name` read them off the registry. Exemplar. |
| Menu category nouns | `taxonomy.py` — `_CATEGORY_LABEL` table keyed on neutral slug ids; `category_of` resolves a slug from the slot/kind branch then reads the label | ✅ | **RESOLVED (R2, this PR).** The category display nouns ("Weapons", "Armour", "Tools", "Structures", "Items") moved out of the `if`/`elif` returns into a data table; the branch now emits only neutral slugs — byte-identical labels, swap-a-row test proves it. |
| Type / kind / category emoji | `taxonomy.py:21-27,39-61` (`CATEGORY_EMOJI`, `TYPE_EMOJI`, `_KIND_EMOJI`) | ✅ | Emoji in module-level tables keyed on base-type / kind / category ids. |

### 2b. Fishing (`games/fishing/core/`) — the built-to-spec exemplar

| Surface | Where the nouns live (`file:line`) | Verdict | Note |
|---|---|---|---|
| Species table (name / emoji / flavour) | `species.py:46-79` (`_SPECIES`), keyed on `species_id` | ✅ | Pure data. Every player-visible noun is a row keyed on a **neutral id** ("legend_carp"); `MAX_SIZE_RANK`/lookups derive from the table (`:82-86`). The Q-0267 reference shape — **verified, not assumed**. |
| Catch narration (species-bearing) | `catch.py:187` | ✅ | Assembled **from the picked species row** — `f"{row.emoji} {row.flavor} — you land a {row.name} ({size} cm)!"`. The logic branch names no species; re-theme by editing `species.py` alone. |
| Cast status narration (no noun) | `catch.py:119,180` (`_TOO_TIRED`, empty-cast) | ⚠️ | Two generic status strings ("Too tired to cast…", "…nothing bites this time.") are inlined. They carry **no theme noun** (ambient scaffolding), so Q-0267's noun rule is not violated — but for full parity with `species.py` the scaffold belongs in a small table too (§5 R4). |
| RNG | `rng.py` (`fishing_seed`) | ✅ (n/a) | Integer-only seed derivation — no noun surface. |

### 2c. Exploration / quest (`games/exploration/quest/`) — clean data model

| Surface | Where the nouns live (`file:line`) | Verdict | Note |
|---|---|---|---|
| Quest names / summaries / objective text | `catalog.py:32-120` (`TEMPLATES`) | ✅ | `QuestTemplate(title, summary, objectives=…)` rows keyed on **neutral `template_id`** ("supply_run", "cull_the_pack"). All narration ("Deliver three supply crates to the outpost.") is a **data field** in the module-level table. |
| Objective match targets (nouns) | `catalog.py:44,59,75,91` (`params` match dicts) | ✅ | Match targets are **neutral ids in data** — `{"item": "supply_crate"}`, `{"species": "dire_wolf"}`, `{"loc": "cavern"}`, `{"npc": "traveler"}` — read by `predicates.py`, never spelled in logic. |
| Objective counts | `catalog.py:40,76,116` (`description` vs `required`) | ✅ (note) | The count is stated in both the prose ("Defeat 5 dire wolves") and the `required=5` field — a mild prose/field duplication (same shape as mining's `EXPLORE_OUTCOMES`), but fully data-resident. |
| Reward / capability ids | `models.py:56-63` (`RewardBundle`), `catalog.py:47` (`prestige_capability`) | ✅ | Capability grants are **neutral ids** ("trade_route_unlock") in data; amounts are code-owned, capped, and carry no noun. |

### 2d. Shared encounter seam (`games/shared/encounter/`) — theme-free by construction

| Surface | Where the nouns live (`file:line`) | Verdict | Note |
|---|---|---|---|
| Outcome payload | `interface.py:38-45` (`EncounterOutcome`) | ✅ (n/a) | Carries `kind: str` + an **opaque `payload: Mapping`** — no narration, no display noun surface to leak. |
| Reference kind table | `reference.py:19` (`_KINDS`) | ✅ | Kind ids ("none", "creature", "cache", "event") in a **module-level tuple**; the resolver renders no narration (payload is `{"trigger", "intensity"}`, `reference.py:44-47`) — nothing player-visible is hardcoded. |

---

## 3. Leak inventory (the ❌ / ⚠️ findings, worst first)

Ordered by severity: a **noun inside mechanics logic** is worse than a
**noun-as-key** is worse than a **stray label / prose duplication**.

**Severity 1 — noun in mechanics logic (❌ → ✅ RESOLVED):**

1. ~~**Mining encounter narration + the "creature" noun**~~ — **RESOLVED (R1,
   this PR, `feat/mining-narration-data`).** Was: every encounter's player-facing
   string was an f-string literal *inside* the resolver branches, and the enemy
   noun **"creature"** had no data table anywhere. Now: a module-level
   `_NARRATION` table (keyed on the neutral `_Narration` slot enum) + a
   `_CREATURE_NOUN` row; a pure `_narrate()` assembles every string and the
   `_resolve_*` branches hold zero player literals — matching fishing
   (`species.py`) and grid (`_STRIKE_NOTE`). Byte-identical output, pinned by a
   golden test.

**Severity 2 — noun doubles as the mechanic key (❌):**

2. **Item identity = display noun as the key** — `items.py:66-224` (`_CATALOG`)
   and `equipment.py:139-208` (`_GEAR`), both keyed on `name.lower()`. The
   player noun *is* the catalog / inventory / persisted / gear key, so a
   re-theme rewrites mechanic keys and stored data. This is the inventory-
   contract doc's §1a finding; its `ItemId` + `ItemMeta` proposal is the fix
   and it already owns the migration (§4 of that doc) — this audit only points
   at it, it does not re-plan it.

**Severity 3 — stray labels, prose duplication, noun-keyed data tables (⚠️):**

3. ~~**Menu category nouns emitted from `if`/`elif`**~~ — **RESOLVED (R2, this
   PR).** `taxonomy.category_of` now resolves a neutral slug and reads the label
   off `_CATEGORY_LABEL`; the branch emits no display noun.
4. ~~**Shop section labels inlined**~~ — **RESOLVED (R2, this PR).**
   `market.shop_sections` groups on neutral section ids and reads titles off the
   `SHOP_SECTION_LABEL` table.
5. ~~**Barren-cell flavour inlined**~~ — **RESOLVED (R2, this PR).** The
   `grid.py` barren note moved into the sibling `_BARREN_NOTE` data table
   beside `_STRIKE_NOTE`.
6. **Noun + amount baked into explore prose** — `rewards.py:138-144`.
7. **Fish-bridge drops the neutral id** — `items.py:293-303`.
8. **Fishing status scaffold inlined** — `catch.py:119,180` (no noun; parity-only).
9. **Noun-keyed data tables** (data-resident but keyed on the display noun):
   `equipment.MAX_DURABILITY` (`:225`), `rewards.ORE_WEIGHTS` (`:21`),
   `energy.RESTORE_VALUES` (`:31`), `market.GEAR_SHOP` (`:49`),
   `equipment.TIER_ORDER` (`:61`). These all fold into fix #2 (they key on the
   same noun identity) and need no separate work once the neutral-id migration
   lands.

**Headline tally:** **19 ✅ · 9 ⚠️ · 2 ❌** across 30 audited surfaces (mining
encounter narration flipped ❌→✅ in `feat/mining-narration-data`, R1; the three
mining stray-literal ⚠️ — barren flavour, shop-section labels, menu-category
nouns — flipped ⚠️→✅ in `feat/theme-leak-r2`, R2). The
world games are *mostly* theme-ready: fishing, titles, structures, quest
catalog, and mining's grid/stat tables are clean data. The concentration of
leakage is (a) mining encounter narration and (b) the item-identity model — both
already have homes (a small extraction; the inventory contract).

---

## 4. Proposed theme-slot pattern

**Target shape (per system):** a module-level `theme`/`data` table of frozen
rows keyed on a **neutral id**, plus mechanics that key on the id and read every
noun/emoji/flavour off the row. Narration is assembled from row fields (or from a
narration-template table keyed on a neutral outcome enum), never spelled in a
resolver branch. This is exactly what already ships in:

- **`games/fishing/core/species.py`** — `Species(species_id, name, emoji, flavor,
  …)` rows; `catch.py:187` assembles narration from the row. The reference.
- **`games/mining/core/titles.py`** — `Title(id, label, emoji, requirement)` rows
  in `_RULES`; `display()` assembles from data.
- **`games/mining/core/structures.py`** — a `StructureDef` **registry** keyed on
  neutral structure keys.
- **`games/mining/core/grid.py`** — `_STRIKE_NOTE` shows the narration-template-in-
  a-table pattern that `encounters.py` should adopt.

**Decision — one shared `games/shared/theme/` registry, or per-system tables?**
**Recommendation: per-system tables; do NOT stand up a shared theme registry.**
The world games have *structurally different* noun shapes — a fishing `Species`
carries `size_rank`/`rarity_weight`, a mining `ItemDef` carries `kind`/`tier`, a
`Title` carries an earn `requirement`, a `QuestTemplate` carries `objectives`. A
single global table would either flatten these into a lossy union or become a
bag of per-system sub-tables — no real sharing, more coupling. The thing worth
sharing is the **pattern**, not the data store: the neutral-id + data-row
lookup, which the inventory-contract doc already generalises as the `ItemMeta` +
`ItemCatalog` **Protocol** (`world-inventory-resource-contract.md` §2a). That
Protocol is a *shape*, adopted per system by a thin table — the correct shared
surface. So: keep each system's theme table local; let the (future) shared
`ItemCatalog` Protocol be the only cross-system contract. Flagged for the owner:
if a future "global re-skin" feature ever needs to enumerate *all* nouns across
games at once, revisit — but nothing today needs it.

---

## 5. Remediation roadmap

Prioritized, **smallest-first**, each a future merged-on-green slice — no
big-bang. **None of these block shipping today**: every leak is cosmetic-refactor
scope (moving a noun to data), the games are playable and sim-pinned as-is.

- **R1 — Mining encounter narration table (closes ❌ #1; smallest high-value
  fix).** ✅ **SHIPPED** (this PR, `feat/mining-narration-data`). Added a
  module-level `_NARRATION` table to `encounters.py` keyed on a neutral
  `_Narration` slot enum (finer than `(EncounterKind, Resolution)` so the two
  distinct FLED copies each get a row) plus a `_CREATURE_NOUN` row; a pure
  `_narrate(...)` helper `.format(...)`s the template and the `_resolve_*` fns hold
  **zero** player strings — mirroring `grid.py`'s `_STRIKE_NOTE`. Proven
  byte-identical by a golden characterization test captured from the pre-change
  resolver (`tests/mining/test_encounter_narration.py`).
- **R2 — Sweep mining's stray literals into their sibling tables.** ✅ **SHIPPED**
  (this PR, `feat/theme-leak-r2`). Moved the `grid.py:177` barren line into a new
  `_BARREN_NOTE` table beside `_STRIKE_NOTE`; moved the `market.py:181-192`
  section labels into `SHOP_SECTION_LABEL` (keyed on neutral section ids) and the
  `taxonomy.py:75-82` category nouns into `_CATEGORY_LABEL` (keyed on neutral
  slug ids). Each branch now emits only neutral ids and reads the label off the
  table; all three strings are byte-identical, pinned by hand-listed golden
  asserts + a swap-a-row load-bearing test + an AST "no inline player-label"
  guard (`tests/mining/test_grid.py`, `test_items_market.py`, `test_taxonomy.py`).
  Tiny, mechanical, behaviour-preserving — the full mining suite stayed green
  unchanged.
- **R3 — Fishing status-scaffold table (parity).** Lift `catch.py:119,180` into a
  `_STATUS_NARRATION` table so `catch.py` has *zero* inline player strings, full
  parity with `species.py`. (Lowest urgency — no noun leaks today.)
- **R4 — De-duplicate count-in-prose.** Where a count is baked into flavour prose
  *and* a field (`rewards.py:138-144`, `catalog.py` objective descriptions),
  render the prose from the field so the number has one source. Cosmetic.
- **R5 — Neutral-id item identity (closes ❌ #2; largest, already owned).** Migrate
  `_CATALOG`/`_GEAR` from noun-as-key to a neutral `ItemId` + `ItemMeta` row.
  **This is the inventory-contract doc's own migration** (`world-inventory-
  resource-contract.md` §4, PR-1…): the theme audit does not re-plan it — it
  confirms the theme motivation and defers to that roadmap. Gated on the shared
  `games/shared/inventory/` seam landing first. Fixes leak #2 and dissolves the
  noun-keyed-table ⚠️ cluster (item #9 in §3) in one move.

Dependency order: R1–R4 are independent and can land in any order; R5 follows the
inventory-contract seam. Recommended sequence: **R1 → R2 → (R5 when the seam
lands) → R3 → R4**.

---

## 6. Integrity floor

Remediation is **behaviour-preserving refactoring, not redesign**:

- **No outcome may change.** Moving a noun/narration string into a data table
  must leave every deterministic outcome byte-identical — same species picked,
  same ore drawn, same amounts, same resolution. The extracted narration string
  must equal the pre-refactor literal exactly. Determinism code (the splitmix64
  seeds, the sim-pinned constants, the resolver branches' *logic*) is **not
  touched** — only the *string source* moves from an inline literal to a table
  lookup. Pin each extraction with a test asserting the assembled narration
  equals the old literal for every branch.
- **No pay-to-win introduced.** Theme extraction touches **no** weight, amount,
  gate, or price — `ORE_WEIGHTS`, `rarity_weight`, the gear stat rows, and the
  energy economy stay exactly as sim-pinned. A re-skin changes what a noun is
  *called*, never what it *does* or costs (Q-0039 / Q-0190). The neutral-id
  migration (R5) likewise only renames keys — the values it carries are
  unchanged.

---

## 7. Verification (how a future slice proves a system is theme-clean)

A system is theme-clean when **no player-facing literal appears in a mechanics
module** and **all narration flows through a data lookup**. A future slice proves
it with:

1. **A "no inline player-strings in mechanics" test.** Scan the mechanics module
   (e.g. `encounters.py`, `catch.py`) for string literals containing letters +
   whitespace / emoji outside the designated data tables, and assert the set is
   empty. Fishing's `catch.py` passes once R3 lands; mining's `encounters.py`
   passes once R1 lands. (Docstrings and neutral ids are excluded.)
2. **A "narration comes from data" test.** Assert the set of narration templates
   the resolver can emit equals the keys of the module's narration table — so a
   new branch cannot ship an inline string without a table row. This is the
   generalisation of fishing's existing discipline, where the theme tests key on
   the **neutral species ids**, not the display strings (`species.py:8-11`
   states this contract explicitly).
3. **A byte-identity guard on the move.** For each extraction, a test pins the
   assembled output against the known-good literal (the §6 integrity floor made
   executable), so the refactor cannot silently alter copy.
4. **A re-skin smoke test (optional, proves the payoff).** Swap a theme table for
   an alternate skin in a test fixture and assert mechanics + sim bounds are
   unchanged — demonstrating the core/skin split actually holds.
