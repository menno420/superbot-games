"""Display-table completeness registry — vocab and display tables stay in sync.

Mining core repeatedly pairs a VOCABULARY (an enum, a dataclass's fields, an
order tuple) with a DISPLAY TABLE (label/emoji/glyph dicts keyed by that
vocabulary). Nothing structural kept them in sync: a new enum member, stat
field, or biome could ship without its player-facing label and fail only at
render time (a ``KeyError`` in an embed) or silently (a ``.get`` fallback).
This module pins every such pair found by reading the mining core modules —
each sync costs one assertion here, not a bespoke test elsewhere.

Spec provenance: the display-table completeness registry card idea from
``.sessions/2026-07-14-night-coverage-mining-core-naming.md``.
"""

from __future__ import annotations

from dataclasses import fields

from games.mining.core import equipment, grid, items, market, skills, taxonomy, world
from games.mining.core.exploration import Biome
from games.mining.core.grid import CellFeature
from games.mining.core.items import ItemKind


def test_item_kind_emoji_covers_every_kind_both_ways() -> None:
    kinds = {kind.value for kind in ItemKind}
    assert kinds <= set(taxonomy._KIND_EMOJI), (
        f"ItemKind value(s) missing an emoji: {sorted(kinds - set(taxonomy._KIND_EMOJI))}"
    )
    assert set(taxonomy._KIND_EMOJI) <= kinds, (
        f"stale _KIND_EMOJI key(s): {sorted(set(taxonomy._KIND_EMOJI) - kinds)}"
    )


def test_category_label_order_and_emoji_agree() -> None:
    labels = set(taxonomy._CATEGORY_LABEL.values())
    assert labels == set(taxonomy.CATEGORY_ORDER)
    assert labels == set(taxonomy.CATEGORY_EMOJI)
    # The order tuple carries no duplicates (it IS the display order).
    assert len(taxonomy.CATEGORY_ORDER) == len(set(taxonomy.CATEGORY_ORDER))


def test_effective_stats_fields_match_labels_and_glyphs() -> None:
    field_names = [f.name for f in fields(equipment.EffectiveStats)]
    # STAT_LABELS iterates in dict order to render stat lines — pin it to the
    # dataclass's declaration order, not just the same set.
    assert list(equipment.STAT_LABELS) == field_names
    assert set(equipment.STAT_GLYPHS) == set(field_names)


def test_type_emoji_keys_are_real_catalog_base_types() -> None:
    base_types = {taxonomy.base_type(name) for name in items.catalog_names()}
    stale = set(taxonomy.TYPE_EMOJI) - base_types
    assert not stale, f"TYPE_EMOJI key(s) match no catalogued item type: {sorted(stale)}"


def test_biome_tables_cover_every_biome_both_ways() -> None:
    biomes = set(Biome)
    assert set(world.BIOME_LABELS) == biomes
    assert set(world.BIOME_EMOJI) == biomes


def test_cell_feature_tables_cover_every_feature_both_ways() -> None:
    features = set(CellFeature)
    assert set(grid._FEATURE_GLYPH) == features
    assert set(grid._FEATURE_LABEL) == features


def test_map_legend_names_every_glyph() -> None:
    for glyph in (grid.PLAYER_GLYPH, grid.FOG_GLYPH, *grid._FEATURE_GLYPH.values()):
        assert glyph in grid.MAP_LEGEND, f"glyph {glyph!r} missing from MAP_LEGEND"


def test_shop_section_labels_match_section_order() -> None:
    assert set(market.SHOP_SECTION_LABEL) == set(market._SECTION_ORDER)
    assert len(market._SECTION_ORDER) == len(set(market._SECTION_ORDER))


def test_branch_labels_cover_every_skill_branch() -> None:
    assert set(skills.BRANCH_LABELS) == set(skills.BRANCHES)
    assert len(skills.BRANCHES) == len(set(skills.BRANCHES))
