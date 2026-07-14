"""Coverage pins for ``games/mining/core/items.py`` — the display/valuation seams.

The existing suites exercise the catalog itself (lookup, classify, the fish
injection point, the set-family rows). This module pins the helper layer that
was still dark:

* the ``is_tool`` / ``is_consumable`` predicates and ``tool_tier`` (including
  its unknown-item -> 0 guard);
* ``total_value`` — per-unit value × qty, zero/negative quantities skipped,
  unknown items counted at the documented default value 1;
* ``next_tool_upgrade``'s tail — a name on NO ladder returns None;
* ``sort_inventory`` — kind order (resources, tools, consumables, structures,
  treasure), value-desc then name-asc within a kind, zero-qty rows dropped;
* ``summarize_inventory`` — one section per ItemKind present, same ordering,
  empty inventory -> no sections.

Every asserted number/name is an EXISTING catalog constant (wood/stone value 1,
iron 3, diamond 12, pickaxe TOOL value 5, torch CONSUMABLE value 2, dynamite
CONSUMABLE value 8, stone hut STRUCTURE value 10, lucky charm TREASURE
value 20). Tests only — zero gameplay-constant changes.
"""

from __future__ import annotations

from games.mining.core.items import (
    ItemKind,
    is_consumable,
    is_tool,
    next_tool_upgrade,
    sort_inventory,
    summarize_inventory,
    tool_tier,
    total_value,
)


# ---------------------------------------------------------------------------
# Predicates + tool_tier
# ---------------------------------------------------------------------------
def test_is_tool_true_for_a_catalog_tool_and_false_for_a_resource() -> None:
    assert is_tool("pickaxe") is True
    assert is_tool("wood") is False


def test_is_tool_is_case_insensitive_like_the_catalog() -> None:
    assert is_tool("Diamond Pickaxe") is True


def test_is_consumable_true_for_torch_and_false_for_a_tool() -> None:
    assert is_consumable("torch") is True
    assert is_consumable("pickaxe") is False


def test_tool_tier_reads_the_catalog_tier() -> None:
    assert tool_tier("pickaxe") == 1
    assert tool_tier("diamond pickaxe") == 4


def test_tool_tier_unknown_item_is_zero() -> None:
    assert tool_tier("zorpium drill") == 0


# ---------------------------------------------------------------------------
# total_value
# ---------------------------------------------------------------------------
def test_total_value_sums_per_unit_value_times_qty() -> None:
    # iron value 3, diamond value 12 (catalog constants).
    assert total_value({"iron": 4, "diamond": 2}) == 3 * 4 + 12 * 2


def test_total_value_skips_zero_and_negative_quantities() -> None:
    assert total_value({"iron": 0, "diamond": -3, "wood": 2}) == 2  # wood value 1


def test_total_value_counts_unknown_items_at_the_default_value_one() -> None:
    assert total_value({"mystery orb": 5}) == 5


# ---------------------------------------------------------------------------
# next_tool_upgrade — the off-every-ladder tail
# ---------------------------------------------------------------------------
def test_next_tool_upgrade_for_a_name_on_no_ladder_is_none() -> None:
    assert next_tool_upgrade("wood") is None
    assert next_tool_upgrade("zorpium drill") is None


# ---------------------------------------------------------------------------
# sort_inventory — the display ordering
# ---------------------------------------------------------------------------
def test_sort_inventory_orders_kinds_resources_first_treasure_last() -> None:
    inventory = {
        "lucky charm": 1,  # TREASURE
        "stone hut": 1,  # STRUCTURE
        "torch": 3,  # CONSUMABLE
        "pickaxe": 1,  # TOOL
        "wood": 5,  # RESOURCE
    }
    assert [name for name, _ in sort_inventory(inventory)] == [
        "wood",
        "pickaxe",
        "torch",
        "stone hut",
        "lucky charm",
    ]


def test_sort_inventory_within_a_kind_sorts_value_desc_then_name_asc() -> None:
    # All RESOURCE: diamond 12 > iron 3 > stone/wood tie at 1 -> name asc.
    inventory = {"wood": 1, "stone": 1, "iron": 1, "diamond": 1}
    assert [name for name, _ in sort_inventory(inventory)] == [
        "diamond",
        "iron",
        "stone",
        "wood",
    ]


def test_sort_inventory_drops_zero_and_negative_quantities() -> None:
    inventory = {"wood": 0, "iron": -1, "diamond": 2}
    assert sort_inventory(inventory) == [("diamond", 2)]


# ---------------------------------------------------------------------------
# summarize_inventory — sectioned display grouping
# ---------------------------------------------------------------------------
def test_summarize_inventory_chunks_one_section_per_kind_in_display_order() -> None:
    inventory = {
        "lucky charm": 1,  # TREASURE
        "torch": 3,  # CONSUMABLE value 2
        "dynamite": 1,  # CONSUMABLE value 8
        "pickaxe": 1,  # TOOL
        "wood": 5,  # RESOURCE
        "stone": 0,  # dropped
    }
    sections = summarize_inventory(inventory)
    assert [kind for kind, _ in sections] == [
        ItemKind.RESOURCE,
        ItemKind.TOOL,
        ItemKind.CONSUMABLE,
        ItemKind.TREASURE,
    ]
    as_dict = dict(sections)
    assert as_dict[ItemKind.RESOURCE] == [("wood", 5)]
    assert as_dict[ItemKind.TOOL] == [("pickaxe", 1)]
    # Within the CONSUMABLE section: dynamite (8) outranks torch (2).
    assert as_dict[ItemKind.CONSUMABLE] == [("dynamite", 1), ("torch", 3)]
    assert as_dict[ItemKind.TREASURE] == [("lucky charm", 1)]


def test_summarize_inventory_of_an_empty_inventory_has_no_sections() -> None:
    assert summarize_inventory({}) == []
    assert summarize_inventory({"wood": 0}) == []
