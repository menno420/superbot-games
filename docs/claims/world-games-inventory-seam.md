# Claim — world-games inventory/resource seam (games/shared/inventory/)

> **Status:** `binding`
>
> The IMPLEMENTATION claim for the `games/shared/inventory/` shared surface — migration
> **PR-1** of [`../design/world-inventory-resource-contract.md`](../design/world-inventory-resource-contract.md)
> §4. Supersedes the advisory design-only reservation
> [`world-games-inventory-contract.md`](world-games-inventory-contract.md).

project: superbot-games (single world-games seat) · date: 2026-07-11

paths (claimed): `games/shared/inventory/**` · plus this PR's own additive test dir
`tests/shared/inventory/**` and the CI count-floor bump in `.github/workflows/tests.yml`.

what: Stand up the PURE-DOMAIN foundation of the unified item · quantity · reward · hold
contract at `games/shared/inventory/` — the design doc §2 types (`ItemId`, `ItemMeta`,
`Stack`, `ProgressionDelta`, `Grant`, `CapStatus` + the `ItemCatalog` / `InventoryView` /
`CapacityPolicy` Protocols and pure helper constructors), a reference impl layer
(`reference.py`), and the reusable conformance suite (`conformance.py`, §7). Additive
only: nothing imports the package yet.

interface announcement: creating `games/shared/inventory/` is an INTERFACE CHANGE
(claim-first shared surface, `docs/lanes.md`) and is announced in `control/status.md` this
same session — mirroring the `games/shared/encounter/` seam precedent.

scope guard: PR-1 does NOT wire any existing system (no mining/fishing/exploration
adapter — those are PRs 2..6) and does NOT resolve the three ⚑ owner-decisions in the
design doc §6 (neutral-id namespace / mining rename; whether `currency` belongs in the
contract; one shared vs per-system catalogs). Those remain deferred.

lifecycle: delete or supersede this claim when the seam's public surface is stable and no
in-flight PR touches `games/shared/inventory/**`.
