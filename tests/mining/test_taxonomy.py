"""taxonomy: the Q-0267 theme leak R2 extraction of the menu-category nouns.

``category_of`` used to ``return`` the display nouns
("Weapons"/"Armour"/"Tools"/"Structures"/"Items") as literals straight out of an
``if``/``elif`` (audit ``taxonomy.py:75-82``). They now live in the
``_CATEGORY_LABEL`` data table keyed on neutral slug ids; the branch resolves a
slug and the function reads the label off the table. This suite proves the move
is a **pure relocation**: byte-identical labels, the table is the only source,
and no player-facing label survives inside the branch.
"""

from __future__ import annotations

import ast
import inspect

from games.mining.core import taxonomy


def test_category_labels_are_byte_identical() -> None:
    """Each sample item classifies to the exact category noun it did pre-refactor
    (hand-listed expected mapping) — the labels are byte-identical relocations."""
    expected = {
        "iron sword": "Weapons",
        "shield": "Weapons",  # shields sit with weapons (combat gear)
        "iron helmet": "Armour",
        "pickaxe": "Tools",
        "lantern": "Tools",
        "lucky charm": "Tools",  # CHARM slot
        "stone hut": "Structures",
        "gold": "Items",  # a bare resource → the Items bucket
    }
    for name, label in expected.items():
        assert taxonomy.category_of(name) == label, name
    # The five labels are exactly the data-table values, in CATEGORY_ORDER.
    assert list(taxonomy._CATEGORY_LABEL.values()) == list(taxonomy.CATEGORY_ORDER)


def test_category_labels_come_from_the_data_table() -> None:
    """Swapping a _CATEGORY_LABEL row re-skins only that category's noun; every
    other category is unchanged — proof the table is the load-bearing source."""
    # items in NON-weapon categories — their labels must be untouched by the swap.
    others = ["iron helmet", "pickaxe", "stone hut", "gold"]
    before = {n: taxonomy.category_of(n) for n in others}
    original = taxonomy._CATEGORY_LABEL["weapons"]
    try:
        taxonomy._CATEGORY_LABEL["weapons"] = "Armaments"
        assert taxonomy.category_of("iron sword") == "Armaments"
        after = {n: taxonomy.category_of(n) for n in others}
    finally:
        taxonomy._CATEGORY_LABEL["weapons"] = original
    assert after == before  # no other category label moved


def test_category_of_has_no_inline_player_label() -> None:
    """category_of emits category nouns only via _CATEGORY_LABEL — no display
    label literal survives inside the branch bodies (audit §7 recipe #1). The
    neutral kind token "structure" (a comparison id, never shown) is allowed."""
    tree = ast.parse(inspect.getsource(taxonomy))
    labels = set(taxonomy._CATEGORY_LABEL.values())
    offenders: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "category_of":
            docstring = ast.get_docstring(node, clean=False)
            for sub in ast.walk(node):
                if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                    if sub.value != docstring and sub.value in labels:
                        offenders.append(repr(sub.value))
    assert not offenders, offenders


# --- the 3-layer menu helpers (grouping / ordering / labels) ---------------
# category_of is pinned above (Q-0267); the rest of the menu doctrine —
# base_type, pluralize, the emoji lookups, grouped's rarity order,
# types_by_category's body order, ordered_categories — sat untested.
# Everything below runs at EXISTING constants (real catalog items).


def test_base_type_is_the_lowercased_last_word() -> None:
    """"iron sword" → "sword"; a single-word item is its own type; casing
    never leaks into the type key."""
    assert taxonomy.base_type("iron sword") == "sword"
    assert taxonomy.base_type("Iron Sword") == "sword"
    assert taxonomy.base_type("pickaxe") == "pickaxe"


def test_pluralize_rules() -> None:
    """Already-plural words stay (boots, leggings); sibilant endings take
    "es" (torch → torches, box → boxes); everything else takes "s"."""
    assert taxonomy.pluralize("boots") == "boots"
    assert taxonomy.pluralize("leggings") == "leggings"
    assert taxonomy.pluralize("torch") == "torches"
    assert taxonomy.pluralize("box") == "boxes"
    assert taxonomy.pluralize("sword") == "swords"


def test_type_emoji_prefers_the_type_table_then_falls_to_kind() -> None:
    """A base type in TYPE_EMOJI wins; an unlisted base falls back to the
    sample item's kind emoji (dynamite → consumable 🧨, an unknown name
    classifies as resource → ⛏️)."""
    assert taxonomy.type_emoji("sword", "iron sword") == taxonomy.TYPE_EMOJI["sword"]
    assert taxonomy.type_emoji("dynamite", "dynamite") == "🧨"
    assert taxonomy.type_emoji("goo", "mystery goo") == "⛏️"


def test_category_emoji_known_and_unknown() -> None:
    """Every declared category has its emoji; an unknown label renders as
    the empty string (no crash, no placeholder)."""
    for cat in taxonomy.CATEGORY_ORDER:
        assert taxonomy.category_emoji(cat) == taxonomy.CATEGORY_EMOJI[cat] != ""
    assert taxonomy.category_emoji("Nonsense") == ""


def test_grouped_buckets_by_base_type_and_orders_variants_by_rarity() -> None:
    """Variants inside a group read starter → iron → gold → diamond
    (material_rank, then name) regardless of input order; distinct base
    types never share a bucket."""
    shuffled = ["diamond pickaxe", "pickaxe", "gold pickaxe", "iron pickaxe", "iron sword"]
    groups = taxonomy.grouped(shuffled)
    assert groups == {
        "pickaxe": ["pickaxe", "iron pickaxe", "gold pickaxe", "diamond pickaxe"],
        "sword": ["iron sword"],
    }


def test_types_by_category_orders_types_by_equip_slot() -> None:
    """Within a category, types follow equipment.SLOTS body order: weapons
    read sword → shield, armour reads head-to-toe helmet → boots."""
    names = ["iron boots", "iron helmet", "shield", "iron sword", "stone hut", "pickaxe"]
    by_cat = taxonomy.types_by_category(names)
    assert by_cat["Weapons"] == ["sword", "shield"]
    assert by_cat["Armour"] == ["helmet", "boots"]
    assert by_cat["Tools"] == ["pickaxe"]
    assert by_cat["Structures"] == ["hut"]


def test_ordered_categories_follows_display_order_not_input_order() -> None:
    """Only the categories present appear, always in CATEGORY_ORDER —
    feeding structures first cannot promote them above Weapons/Tools."""
    assert taxonomy.ordered_categories(["stone hut", "pickaxe", "iron sword"]) == [
        "Weapons",
        "Tools",
        "Structures",
    ]
    assert taxonomy.ordered_categories([]) == []

