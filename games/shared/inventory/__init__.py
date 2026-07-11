"""Shared inventory / resource contract — the unified item · qty · reward · hold seam.

A PURE-DOMAIN plugin foundation (migration PR-1 of
``docs/design/world-inventory-resource-contract.md`` §4): the ONE vocabulary the world
games converge on, so the six divergent reward/inventory shapes (mining, fishing, quest,
encounter) each map on via a thin per-system adapter (PRs 2..6 — NOT here). Nothing
imports this package yet; that is correct for a foundation slice.

* No Discord / DB / IO — frozen dataclasses + ``@runtime_checkable`` Protocols, stdlib
  only. The HOST STORE seam is left open: a host binds a concrete ``InventoryView`` over
  whatever it persists; the contract stays a pure interface.
* Nouns in data (Q-0267): item identity is a neutral ``ItemId``; player-visible nouns
  live in ``ItemMeta`` / an ``ItemCatalog`` data row, never in this package.
* No pay-to-win (Q-0039 / Q-0190): the contract CARRIES amounts, it never rolls them.

**Interface-change rule** (claim-first shared surface, ``docs/lanes.md``): creating this
package and any later change to its public surface is an INTERFACE CHANGE and must be
announced in ``control/status.md`` in the same session it ships — mirroring the
``games/shared/encounter/`` seam precedent.

Public API::

    from games.shared.inventory.interface import (
        ItemId, ItemMeta, ItemCatalog, Stack, ProgressionDelta, Grant,
        InventoryView, CapacityPolicy, CapStatus,
        item_id, is_valid_item_id, empty_grant, merge_grants, add_delta, scale_delta,
    )
    from games.shared.inventory.reference import (
        DictItemCatalog, ReferenceInventory, DefaultCapacityPolicy, PACK_SOFT_CAP,
    )
    from games.shared.inventory import conformance  # the reusable §7 adapter suite
"""
