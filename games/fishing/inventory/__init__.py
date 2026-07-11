"""Fishing → shared-inventory ADAPTER (contract migration PR-2).

A thin, pure adapter mapping the fishing domain's catch output
(:class:`games.fishing.core.catch.Catch` / :class:`CastOutcome`) onto the already-shipped
``games/shared/inventory/`` §2 contract (PR #29). This is the smallest migration step
(design doc ``docs/design/world-inventory-resource-contract.md`` §4, PR-2) — fishing is
already neutral-id (``species.py``), so this is a *pure mapping* with no Q-0267 remediation.

Integrity floor (design doc §5), preserved by construction:

* **Pure / deterministic / stdlib-only.** No Discord, DB, IO, wall-clock, or RNG. The
  adapter is a translation of already-resolved values; equal inputs build equal grants.
* **No pay-to-win** (Q-0039 / Q-0190). The adapter CARRIES the values fishing already
  computed (``catch.size``, a species' data numbers); it never rolls, scales, or gates by
  any pay lever. There is no coin/purchase/spend input anywhere.
* **Nouns stay in fishing's data** (Q-0267). Every player-visible noun (a species' name,
  emoji) is read straight off ``games.fishing.core.species`` and relayed into an
  ``ItemMeta`` row — the adapter introduces NO new hardcoded noun and holds no mechanic
  that names a species.

Decide-and-flag (reversible, no owner sign-off — design doc §6):

* **Per-system catalog.** The catalog here is fishing-local (built from ``species.py``),
  not a global merged catalog. The §6 "one shared vs per-system catalog" owner-decision
  stays DEFERRED; per-system is the doc's own assumption.
* **``fish.<species_id>`` namespace mapping** at the adapter boundary ONLY. No fishing or
  mining internal id is renamed and no persisted data changes; the map is old↔new at the
  seam. The §6 ⚑ neutral-id-namespace / mining-rename owner-decision stays DEFERRED.
"""

from __future__ import annotations

from .adapter import (
    FISH_NAMESPACE,
    cast_to_grant,
    catch_to_grant,
    catch_to_stack,
    fishing_catalog,
    item_id_for_species,
    reachable_item_ids,
    species_id_for_item,
)

__all__ = [
    "FISH_NAMESPACE",
    "cast_to_grant",
    "catch_to_grant",
    "catch_to_stack",
    "fishing_catalog",
    "item_id_for_species",
    "reachable_item_ids",
    "species_id_for_item",
]
