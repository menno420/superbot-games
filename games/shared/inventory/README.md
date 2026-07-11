# Shared inventory / resource contract

The **public shared** inventory/resource seam (claim-first per `docs/lanes.md`). The ONE
pure-domain vocabulary the world games converge on — item · quantity · reward · hold —
specified by [`../../../docs/design/world-inventory-resource-contract.md`](../../../docs/design/world-inventory-resource-contract.md)
§2 and stood up here as **migration PR-1** (§4). Additive only: nothing imports this
package yet; each system adopts it later via a thin adapter (PRs 2..6), extend-not-duplicate.

## Modules

| Module | What it is |
|---|---|
| `interface.py` | The §2 types: `ItemId` (+ `item_id`/`is_valid_item_id`), `ItemMeta`, `Stack`, `ProgressionDelta`, `Grant`, `CapStatus`, and the `ItemCatalog` / `InventoryView` / `CapacityPolicy` Protocols. Pure helpers: `empty_grant`, `merge_grants`, `add_delta`, `scale_delta`. |
| `reference.py` | `DictItemCatalog`, an immutable dict-backed `ReferenceInventory`, and `DefaultCapacityPolicy` (distinct-types soft cap, `PACK_SOFT_CAP=40`) — the conformance reference impls. |
| `conformance.py` | The reusable §7 conformance suite every future adapter runs against its own mapping. |

## Public API

```python
from games.shared.inventory.interface import (
    ItemId, ItemMeta, Stack, ProgressionDelta, Grant,
    ItemCatalog, InventoryView, CapacityPolicy, CapStatus,
    item_id, merge_grants,
)
from games.shared.inventory.reference import (
    DictItemCatalog, ReferenceInventory, DefaultCapacityPolicy,
)

catalog = DictItemCatalog((ItemMeta("ore.diamond", name="Diamond", kind="resource", value=50),))
grant = Grant(items=(Stack("ore.diamond", 3),), progression=ProgressionDelta(game_xp=10))
inv = ReferenceInventory().add_grant(grant)          # -> a NEW inventory (pure)
inv.held("ore.diamond")                              # 3
DefaultCapacityPolicy().status(inv).used             # 1 (distinct types)
```

## Invariants (design floor, spec §5 — pinned by `conformance.py`, §7)

- **Pure / deterministic** — inert data + Protocols, stdlib only. No RNG, wall-clock, or
  IO; it cannot perturb any resolver's determinism.
- **No pay-to-win** (Q-0039 / Q-0190) — the contract CARRIES amounts, it never rolls or
  derives them; there is no coin/purchase/spend lever anywhere.
- **Nouns in data** (Q-0267) — item identity is a neutral `ItemId`; every player-visible
  noun lives in `ItemMeta` / an `ItemCatalog` data row, never in a mechanic.
- **Interface changes are announced in `control/status.md`** in the same session they
  ship (`docs/lanes.md`, claim-first shared surface — mirrors the encounter seam).

The three ⚑ owner-decisions in the design doc §6 (neutral-id namespace / mining rename,
whether `currency` belongs in the contract, one shared vs per-system catalogs) are
**deferred** — they belong to the later per-system adapter PRs, not this foundation slice.
