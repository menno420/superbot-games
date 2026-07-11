# Shared / cross-domain — design index

> **Status:** `reference`
>
> Per-domain design index for cross-game shared contracts. Linked once from
> `docs/current-state.md` so adding a shared design doc edits only THIS file, not the
> shared current-state ledger. The docs-gate reachability BFS follows the links below,
> so every doc (and its companion claims) listed here stays reachable through this index.

- [`world-inventory-resource-contract.md`](world-inventory-resource-contract.md) — PLAN:
  unify the six divergent item/reward/inventory shapes across the world games into one
  `games/shared/inventory/` contract.
  - advisory claim: [`../claims/world-games-inventory-contract.md`](../claims/world-games-inventory-contract.md)
  - migration PR-1 stands up the pure-domain seam `games/shared/inventory/` —
    implementation claim: [`../claims/world-games-inventory-seam.md`](../claims/world-games-inventory-seam.md)
- [`persistence-design.md`](persistence-design.md) — DESIGN: versioned, per-domain-namespaced
  `PlayerState` save/load contract (deterministic canonical JSON, forward-only two-tier
  migration, host owns storage / this repo owns the shape) plus the owner's cross-server
  transfer directive as three named invariants — `TRANSFER_CONSERVATION`,
  `TRANSFER_FRACTION_CAP`, `NO_INSTANT_RICHEST` — with percentages left OWNER-DECIDES.
