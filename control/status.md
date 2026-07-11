# superbot-games · status

updated: 2026-07-11T00:37:49Z
phase: theme-slot readiness audit (Q-0267) shipped — READY PR to main (green-pending); audit DOC only, no system code refactored
health: green — full suite 147 pure-domain tests pass (99 tests/ [73 mining + 26 fishing] + 48 games/exploration/tests/); no system code/README/tests.yml/inbox touched
last-shipped: theme-slot audit — docs/audit/theme-slot-readiness-2026-07-11.md
orders: acked=001,002 done=001,002

## Boot record
Landed on origin/main HEAD `800be24` (PR #26 inventory/resource contract design
doc merged; PR #25 fishing skeleton; PR #24 unified single-seat base). Branch
`feat/theme-slot-audit` off origin/main. This seat owns all of `games/**` and
reports here (single-seat status file).

## Last shipped — theme-slot readiness audit (Q-0267, 2026-07-11)
- **`docs/audit/theme-slot-readiness-2026-07-11.md`** — a grounded, per-system
  audit of THEME-READINESS (an AUDIT doc; NO system code refactored). For every
  player-visible-noun surface across the world games it records whether the noun
  lives in DATA (a module-level table keyed on a neutral id, swappable) or is
  hardcoded in CODE (a literal in branching logic), with a `file:line` citation
  for every verdict.
  - **Tally:** 15 ✅ DATA · 12 ⚠️ MIXED · 3 ❌ CODE across 30 surfaces. Fishing
    (`species.py`), mining titles/structures/grid/stat tables, and the quest
    catalog are clean data; the leakage concentrates in two places.
  - **Top leaks:** (1) ❌ mining encounter narration + the "creature" noun
    hardcoded in the `_resolve_*` branches (`encounters.py:160,253,269,309,321,
    335,342`) — no narration data table at all; (2) ❌ item identity = display
    noun as the catalog/inventory/gear key (`items.py:66-224`, `equipment.py:
    139-208`) — the inventory-contract doc §1a finding, whose `ItemId`/`ItemMeta`
    migration already owns the fix; (3) ⚠️ menu category nouns emitted from
    `if`/`elif` (`taxonomy.py:75-82`) + inlined shop-section labels
    (`market.py:181-192`).
  - **Roadmap (§5):** 5 prioritized smallest-first merged-on-green slices
    (R1 encounter narration table → R2 stray-literal sweep → R5 neutral-id
    identity, gated on the inventory seam → R3 fishing scaffold → R4 count
    de-dup). None block shipping today; all behaviour-preserving.
  - **Pattern decision (§4):** keep per-system theme tables; do NOT stand up a
    shared `games/shared/theme/` registry — the shared surface worth having is
    the `ItemCatalog` Protocol (a shape) from the inventory contract, not a global
    data store.
- **Linked** from the `docs/current-state.md` read-path index ("Audits:" line).
- **Collection:** `python3 -m pytest tests/ games/exploration/tests/ -q` →
  **147 passed** (matches the #24/#25/#26 floor). Docs-only PR — no code, README,
  tests.yml, or inbox edited. `python3 bootstrap.py check --strict` → exit 0 with
  the session card flipped to `complete`.

## Orders
`orders: acked=001,002 done=001,002`
- ORDER 001 — done (merged #24). ORDER 002 — done (superseded by Q-0265).

## Queue (inherited)
- done: fishing walking skeleton (#25); unified inventory/resource contract design
  doc (#26); theme-slot readiness audit (this PR).
- next: implement inventory-contract migration PR-1 (stand up
  `games/shared/inventory/` seam) per that doc §4; then theme-audit R1 (mining
  encounter narration table) — the smallest high-value Q-0267 fix.

## Notes
blockers: none. This is an audit doc — the actual theme-slot refactors are later,
separate merged-on-green slices (audit §5 roadmap), each behaviour-preserving and
none blocking today's ship.
