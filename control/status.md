# superbot-games · status

updated: 2026-07-11T01:17:42Z
phase: inventory/resource contract migration PR-2 shipped — fishing now adapts onto the shared inventory seam via a pure `games/fishing/inventory/` adapter (Catch/CastOutcome → Grant/Stack), validated by the shipped §7 conformance suite; READY PR to main (green-pending)
health: green — full suite 230 pure-domain tests pass (79 mining + 26 fishing + 20 fishing inventory adapter + 48 exploration + 57 tests/shared/inventory/); `bootstrap.py check --strict` exit 0
last-shipped: fishing → inventory adapter (migration PR-2) — `games/fishing/inventory/` maps `Catch → Stack`/`Catch → Grant`/`CastOutcome → Grant` onto `games/shared/inventory/`
orders: acked=001,002 done=001,002

## Boot record
Landed on origin/main HEAD `bb744df` (PR #31 mining narration→data; PR #29 shared inventory
seam PR-1; PR #28 theme-slot audit; PR #26 inventory/resource contract design doc; PR #25
fishing skeleton). Branch `feat/fishing-inventory-adapter` off origin/main. This seat owns
all of `games/**` and reports here (single-seat status file).

## Last shipped — fishing → shared inventory adapter (2026-07-11, migration PR-2)
- **`games/fishing/inventory/` pure adapter** (stdlib-only, no Discord/DB/IO/RNG), the first
  consumer of the shared inventory seam (PR #29):
  - `fishing_catalog()` — a per-system `ItemCatalog` built from `species.py` DATA (one
    `ItemMeta` per row; name/emoji **relayed** from the data table, `value`=`size_rank`
    carried not rolled).
  - `item_id_for_species` / `species_id_for_item` — maps each fishing `species_id` to a
    neutral `fish.<species_id>` `ItemId` at the adapter boundary ONLY (no internal rename).
  - `catch_to_stack` / `catch_to_grant` / `cast_to_grant` — `Catch → Stack(fish.<id>, qty=1,
    attrs={size,size_rank})`, wrapped as a one-stack `Grant` (empty progression — fishing has
    no XP yet); no-bite `CastOutcome → EMPTY_GRANT`. Pure, deterministic, total.
- **Shared §7 conformance passes against the fishing catalog** — `run_conformance` +
  `assert_nouns_are_data_only` re-imported from the shipped suite and run against
  `fishing_catalog()` + a `ReferenceInventory` seeded from adapter grants (round-trip
  identity, no-spend-lever, catalog-ids-neutral, capacity-in-distinct-types, re-skin).
- **Tests:** `tests/fishing/` 26 → 46 (+20 in `test_inventory_adapter.py`). Full suite
  `python3 -m pytest tests/ games/exploration/tests/ -q` → **230 passed**. CI count floor
  bumped `210 → 230` in `.github/workflows/tests.yml`.
- **Design doc §4** migration path — PR-2 (fishing adapter) marked **SHIPPED**; Status badge
  (`plan`) + reachability left intact.
- **Integrity floor held:** pure/deterministic/stdlib (no new deps, no RNG/IO); no
  pay-to-win (the adapter CARRIES fishing's already-computed values — `catch.size`, species
  data numbers — never rolls, scales, or gates by any pay lever); nouns stay in fishing's
  `species.py` data (Q-0267 — the adapter relays, introduces no new hardcoded noun).
- **No shared interface introduced** — this PR consumes the existing `games/shared/inventory/`
  contract, so no interface-change announcement is required. Fishing now has an inventory
  adapter.

## Decide-and-flag (reversible; §6 owner-decisions stay DEFERRED)
- **Per-system catalog** — fishing owns a local `ItemCatalog`; a global merged catalog is the
  §6 owner call, deferred.
- **`fish.` namespace mapping** at the adapter boundary — no persisted id changes, no
  internal rename; the §6 ⚑ neutral-id-namespace / mining-rename owner-decision stays
  deferred. The `currency`-in-contract §6 flag is untouched here.

## Orders
`orders: acked=001,002 done=001,002`
- ORDER 001 — done (merged #24). ORDER 002 — done (superseded by Q-0265).

## Queue (inherited)
- done: fishing skeleton (#25); inventory contract design doc (#26); theme-slot audit (#28);
  inventory seam PR-1 (#29); mining narration table R1 (#31); **inventory migration PR-2 —
  fishing adapter** (this PR).
- next (inventory migration): **PR-3** mining catalog adapter (closes the Q-0267 §1a gap) →
  **PR-4** quest adapter → **PR-5** encounter typed grant → **PR-6** fish→mining bridge fix.
  Also queued (theme-audit roadmap): R2 mining stray-literal sweep; R3 fishing status
  scaffold; R4 de-dupe count-in-prose.

## Notes
blockers: none. PR-2 is a pure additive adapter — no migrated system's economy or determinism
is touched, both fishing and the shared seam stay as sim-pinned as before. The design-doc §6
owner-decisions remain DEFERRED to the adapter PRs that touch them.
