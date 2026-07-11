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
