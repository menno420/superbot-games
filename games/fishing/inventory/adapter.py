"""The fishing ↔ shared-inventory mapping — pure, deterministic, stdlib-only.

Reads fishing's neutral-id theme table (:mod:`games.fishing.core.species`) and the resolver's
frozen outputs (:mod:`games.fishing.core.catch`) and relays them into the shared §2 contract
types (:mod:`games.shared.inventory.interface`). Nothing here rolls or scales a value; every
number and noun is CARRIED from fishing's own data (design doc §5).
"""

from __future__ import annotations

from games.fishing.core import species as species_table
from games.fishing.core.catch import Catch, CastOutcome
from games.shared.inventory.interface import (
    EMPTY_GRANT,
    Grant,
    ItemId,
    ItemMeta,
    ProgressionDelta,
    Stack,
    item_id,
)
from games.shared.inventory.reference import DictItemCatalog

# The adapter-boundary namespace for a fishing item id. A species' neutral key
# ``"legend_carp"`` maps to the neutral ``ItemId`` ``"fish.legend_carp"``. This is the
# ONLY place the mapping lives; no fishing/mining internal id is renamed (design doc §6,
# reversible decide-and-flag). Reusing this one constant as the namespace tag keeps the
# adapter from introducing any *new* hardcoded string.
FISH_NAMESPACE = "fish"

# Item kind for a landed fish in the shared catalog — a caught resource (mirrors the
# reference suite's ``kind="resource"`` for fishing rows). A mechanic constant, not a
# player-visible noun; the display nouns (name/emoji) come from ``species.py`` DATA.
_FISH_KIND = "resource"


def item_id_for_species(species_id: str) -> ItemId:
    """Map a fishing ``species_id`` to its neutral shared ``ItemId`` (``fish.<species_id>``).

    Validated through :func:`games.shared.inventory.interface.item_id`, so a non-neutral
    species key could never leak in as an identity — the boundary guard. The species ids in
    ``species.py`` are already lowercase-underscore, so every one yields a valid neutral id.
    """
    return item_id(f"{FISH_NAMESPACE}.{species_id}")


def species_id_for_item(item: ItemId) -> str:
    """Inverse of :func:`item_id_for_species`: strip the ``fish.`` namespace back to the key.

    Raises ``ValueError`` if ``item`` is not a ``fish.<species_id>`` id — the map is only
    defined over the fishing namespace.
    """
    prefix = f"{FISH_NAMESPACE}."
    if not item.startswith(prefix):
        raise ValueError(f"not a fishing item id: {item!r} (expected '{prefix}<species_id>')")
    return item[len(prefix) :]


def _meta_for(row: species_table.Species) -> ItemMeta:
    """Build the shared ``ItemMeta`` for one species row — every noun RELAYED from data."""
    return ItemMeta(
        item_id=item_id_for_species(row.species_id),
        name=row.name,  # display noun — relayed from species.py, not authored here
        kind=_FISH_KIND,
        stackable=True,
        # A CARRIED display magnitude (bigger species rank higher) — read straight off the
        # data row, never rolled or scaled. No pay lever touches it.
        value=row.size_rank,
        emoji=row.emoji,  # display glyph — relayed from species.py
        tags=frozenset({FISH_NAMESPACE}),
    )


def fishing_catalog() -> DictItemCatalog:
    """The fishing-local ``ItemCatalog`` — one ``ItemMeta`` per ``species.py`` row.

    Per-system catalog (design doc §6, reversible): fishing owns its own catalog behind the
    shared ``ItemCatalog`` Protocol; a global merged catalog stays an owner-deferred call.
    Rebuilt from the single source of truth (``species.all_species()``) so adding/removing a
    species row changes the reachable ids with zero adapter change.
    """
    return DictItemCatalog(tuple(_meta_for(row) for row in species_table.all_species()))


def reachable_item_ids() -> tuple[ItemId, ...]:
    """Every ``ItemId`` this adapter can emit, in species-table order.

    A theme-data guard surface: the returned ids are exactly ``fish.<key>`` for each key in
    ``species.py``. Swap/remove a species row and this set changes — proving the nouns (and
    the reachable identities) live in fishing's data, not in the adapter.
    """
    return tuple(item_id_for_species(sid) for sid in species_table.species_ids())


def catch_to_stack(catch: Catch) -> Stack:
    """Map a landed :class:`Catch` to a shared :class:`Stack` (qty 1, ``size`` in attrs).

    The per-instance magnitude (``catch.size``) rides in ``attrs`` per the contract §2c
    (one stack type; non-fungible magnitude as an attr, not a parallel subtype). ``size_rank``
    is relayed from the species row so a consumer knows the tier without the catalog. Pure:
    a straight translation of the frozen catch, no roll.
    """
    row = species_table.get(catch.species_id)
    return Stack(
        item=item_id_for_species(catch.species_id),
        qty=1,
        attrs={"size": catch.size, "size_rank": row.size_rank},
    )


def catch_to_grant(catch: Catch) -> Grant:
    """Wrap a :class:`Catch` as the ONE reward shape — a :class:`Grant` of one stack.

    Progression carries the V043 sim-pinned curve VERBATIM (sim-lab VERDICT 043,
    relayed as ORDER 007 item (2) in ``control/inbox.md`` @ ``d6a9526``):
    ``ProgressionDelta.game_xp = size_rank`` per catch — the rank is read straight
    off the species row, never rolled or scaled here. No currency is granted on a
    catch (coins come only from the separate SELL leg, so one fish yields
    sell-OR-cook, never both). Levels derived from this XP stay STAT-NEUTRAL
    (:mod:`games.fishing.core.economy`). The delta is a pure function of the
    species row, so the grant stays deterministic (equal ``Catch`` →
    frozen-equal ``Grant``).
    """
    row = species_table.get(catch.species_id)
    return Grant(
        items=(catch_to_stack(catch),),
        progression=ProgressionDelta(game_xp=row.size_rank),
    )


def cast_to_grant(outcome: CastOutcome) -> Grant:
    """Map a resolved :class:`CastOutcome` to a :class:`Grant`.

    No bite (an empty cast, or too tired to cast) → :data:`EMPTY_GRANT` (the identity for
    ``merge_grants`` — a cast that landed nothing grants nothing). A bite → the catch's grant.
    Pure and total: never raises, mirrors the resolver's honest no-bite contract.
    """
    if not outcome.bit or outcome.catch is None:
        return EMPTY_GRANT
    return catch_to_grant(outcome.catch)


__all__ = [
    "FISH_NAMESPACE",
    "item_id_for_species",
    "species_id_for_item",
    "fishing_catalog",
    "reachable_item_ids",
    "catch_to_stack",
    "catch_to_grant",
    "cast_to_grant",
]
