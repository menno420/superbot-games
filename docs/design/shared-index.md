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
- [`economy-sim.md`](economy-sim.md) — REFERENCE: the cross-domain economy sim
  (`games/shared/sim/economy_sim.py`) enumerates every reward source across
  mining, fishing, dnd, and exploration by driving the shipped resolvers, pins
  each domain's per-hour emission, and asserts the global invariants
  `GRANT_WITHIN_GLOBAL_CAP`, `ITEM_FAUCET_MINTS_NO_CURRENCY`, and
  `NOOP_MINTS_NOTHING`.
