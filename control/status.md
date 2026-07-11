# superbot-games · status

updated: 2026-07-11T00:56:29Z
phase: inventory/resource contract migration PR-1 shipped — new shared seam `games/shared/inventory/` stood up (pure foundation only, nothing wired yet); READY PR to main (green-pending)
health: green — full suite 204 pure-domain tests pass (73 mining + 26 fishing + 48 exploration + 57 tests/shared/inventory/); `bootstrap.py check --strict` exit 0
last-shipped: shared inventory seam PR-1 — games/shared/inventory/ (interface + reference + conformance)
orders: acked=001,002 done=001,002

## Boot record
Landed on origin/main HEAD `9722233` (PR #28 theme-slot audit; PR #26 inventory/resource
contract design doc; PR #25 fishing skeleton; PR #24 unified single-seat base). Branch
`feat/shared-inventory-seam` off origin/main. This seat owns all of `games/**` and reports
here (single-seat status file).

## INTERFACE CHANGE announced (shared-surface rule, docs/lanes.md)
**New public shared seam `games/shared/inventory/`** — claim-first per `docs/lanes.md`,
claimed by `docs/claims/world-games-inventory-seam.md` (`binding`, supersedes the advisory
contract claim). This is **migration PR-1** of
`docs/design/world-inventory-resource-contract.md` §4. Creating the package is an interface
change, announced here in the same session it ships (mirrors the `games/shared/encounter/`
precedent).

## Last shipped — shared inventory seam PR-1 (2026-07-11)
- **`games/shared/inventory/`** — the pure-domain foundation of the unified
  item · quantity · reward · hold contract (design doc §2). Stdlib-only, no Discord/DB/IO,
  frozen dataclasses + `@runtime_checkable` Protocols:
  - **`interface.py`** — `ItemId` (neutral str alias + `item_id`/`is_valid_item_id`
    validator rejecting display nouns), `ItemMeta` (the only re-theme surface, Q-0267),
    `Stack(item, qty, attrs)` (qty may be negative = a loss; attrs read-only),
    `ProgressionDelta`, `Grant` (the ONE reward shape), `CapStatus`, and the `ItemCatalog`
    / `InventoryView` / `CapacityPolicy` Protocols. Pure helpers `empty_grant` /
    `merge_grants` / `add_delta` / `scale_delta`.
  - **`reference.py`** — `DictItemCatalog`, an immutable `ReferenceInventory`, and
    `DefaultCapacityPolicy` (distinct-types soft cap pinned to mining's `PACK_SOFT_CAP=40`).
  - **`conformance.py`** — the reusable §7 conformance suite future per-system adapters
    re-run to prove round-trip identity, no-spend-lever, determinism, theme-data-only
    nouns, and capacity semantics.
- **Additive only:** nothing imports the seam yet — correct for a foundation slice. No
  existing system code, README, or other lane touched.
- **Tests:** `tests/shared/inventory/` — 57 tests, collected by the existing `tests/`
  gate. Full suite `python3 -m pytest tests/ games/exploration/tests/ -q` → **204 passed**.
  CI count floor bumped `147 → 204` in `.github/workflows/tests.yml`.
- **Integrity floor held:** pure/deterministic (inert data + Protocols, no RNG/IO);
  no pay-to-win (the contract carries amounts, never rolls them — conformance §7.2 pins
  no coin/purchase/spend lever); nouns-in-data (item identity is a neutral id; all
  player-visible nouns live in `ItemMeta`/`ItemCatalog` data — Q-0267).

## Orders
`orders: acked=001,002 done=001,002`
- ORDER 001 — done (merged #24). ORDER 002 — done (superseded by Q-0265).

## Queue (inherited)
- done: fishing walking skeleton (#25); inventory/resource contract design doc (#26);
  theme-slot readiness audit (#28); inventory seam PR-1 (this PR).
- next: inventory migration **PR-2 — fishing adapter** (`Catch → Stack`, `species.py`
  as an `ItemCatalog` — smallest, already neutral-id), then PR-3 mining catalog adapter
  (closes the §1a Q-0267 gap), then PR-4 quest / PR-5 encounter typed grant / PR-6
  fish→mining bridge fix. Also queued: theme-audit R1 (mining encounter narration table).

## Notes
blockers: none. PR-1 is the pure foundation only — per-system adapters (PRs 2..6) are
later separate merged-on-green slices. The **three owner-decisions** in the design doc
§6 remain DEFERRED, not resolved here: (1) neutral-id namespace + the mining inventory-key
rename (a data migration the owner must approve); (2) whether `currency` belongs in the
shared contract or stays quest-only; (3) one shared `ItemCatalog` vs per-system catalogs.
They belong to the adapter PRs that actually touch them.
