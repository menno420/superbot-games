# 2026-07-11 · Theme-slot readiness audit (Q-0267)

> **Status:** `complete`
>
> 📊 Model: Claude Opus · 2026-07-11T00:37:49Z · Q-0267 theme-readiness audit across world games

## Goal

Audit THEME-READINESS (Q-0267) across the world-games systems: for every
player-visible noun surface — item/species/structure names, flavor text, emoji,
titles, location names, encounter narration — determine whether it lives in DATA
(module-level tables keyed on NEUTRAL ids, swappable without touching mechanics) or is
hardcoded in CODE (string literals inside branching logic / mechanics). Deliver a
grounded per-system audit + a prioritized remediation roadmap as a DOC. Companion to
`docs/design/world-inventory-resource-contract.md`. This is an AUDIT slice — no system
code, README, tests.yml, or inbox is edited.

## What shipped

- **`docs/audit/theme-slot-readiness-2026-07-11.md`** — a grounded, per-system
  audit of Q-0267 theme-readiness across the world games (AUDIT doc only; NO
  system code, README, `tests.yml`, or inbox touched). Every player-visible-noun
  surface — item/species/structure names, flavour, emoji, titles, locations,
  encounter narration — classified ✅ DATA / ⚠️ MIXED / ❌ CODE with a `file:line`
  citation for every verdict. **Tally: 15 ✅ · 12 ⚠️ · 3 ❌ across 30 surfaces.**
  - **Load-bearing §2 audit table**, one sub-table per system. Fishing
    (`species.py`), mining titles/structures/grid/stat tables, and the quest
    catalog verified as clean data; leakage concentrates in two places.
  - **Top leaks (§3):** (1) ❌ mining encounter narration + the "creature" noun
    hardcoded in the `_resolve_*` branches (`encounters.py:160,253,269,309,321,
    335,342`) — no narration table at all; (2) ❌ item identity = display noun as
    the catalog/inventory/gear key (`items.py:66-224`, `equipment.py:139-208`);
    (3) ⚠️ menu-category nouns from `if`/`elif` (`taxonomy.py:75-82`) + inlined
    shop-section labels (`market.py:181-192`).
  - **§4 pattern decision:** per-system theme tables, NOT a shared
    `games/shared/theme/` registry — the shared surface worth having is the
    `ItemCatalog` Protocol (a shape) from the inventory contract.
  - **§5 roadmap:** 5 smallest-first behaviour-preserving slices (R1 encounter
    narration table → R2 stray-literal sweep → R5 neutral-id identity, gated on
    the inventory seam → R3 fishing scaffold → R4 count de-dup). None block ship.
  - **§6 integrity floor** (no outcome change; no pay-to-win) + **§7
    verification** (a "no inline player-strings in mechanics" test + a
    narration-from-data test).
- **Linked** from the `docs/current-state.md` read-path index ("Audits:" line) so
  the doc is reachable (docs-gate). `bootstrap.py check --strict` → exit 0;
  suite `pytest tests/ games/exploration/tests/` → 147 passed (unchanged floor).

## 💡 Session idea

The audit is a *third* independent witness (after fishing's `species.py` and the
inventory-contract doc) that the world games have already converged on **one
shape** — neutral-id mechanics + a data-only noun table — everywhere they got it
right (titles, structures, grid `_STRIKE_NOTE`, quest catalog). The two ❌ leaks
are exactly the surfaces that predate that convention (mining encounters, born as
a resolver with inline prose; item identity, born as a string-keyed dict). The
cheap win is **R1**: encounter narration is one small `_NARRATION` table away from
clean, and `grid._STRIKE_NOTE` is the copy-paste template — a <30-line
behaviour-preserving slice that closes the single highest-severity leak. Worth
promoting alongside the inventory-seam PR-1 as the first two post-audit slices.

## ⟲ Previous-session review

The inventory-contract doc (#26) set the pattern this audit follows: read the
ACTUAL code, cite `file:line`, invent nothing, and *defer* — it flagged the
item-identity leak but left the migration to a later slice rather than re-planning
it. This audit honours that seam: leak #2 (noun-as-key identity) points straight
at that doc's `ItemId`/`ItemMeta` §4 migration instead of duplicating it. The
sharper lesson carried forward is #26's own red-fail — a docs-only PR reds the
substrate-gate on the DOCS-GATE (a bad Status token / an orphan doc), not just the
⚑ line. This session used the allowed `audit` token, linked the doc from the
`current-state` read-path index, and ran `bootstrap.py check --strict` to exit 0
BEFORE the final push — turning #26's CI round-trip into a local check.
