"""items (fish severance + injection) + market (no-arbitrage pricing)."""

from __future__ import annotations

from dataclasses import dataclass

from games.mining.core import items, market


def test_ore_ladder_values_preserved() -> None:
    assert items.item_value("stone") == 1
    assert items.item_value("bronze") == 2
    assert items.item_value("iron") == 3
    assert items.item_value("silver") == 4
    assert items.item_value("gold") == 6
    assert items.item_value("diamond") == 12
    assert items.item_value("totally unknown") == 1  # unknown → 1


def test_no_fish_in_catalog_by_default_severance() -> None:
    # the oracle folded utils.fishing.fish.SPECIES at import; the pure core does not.
    fish_rows = [n for n in items.catalog_names() if items.is_fish(n)]
    assert fish_rows == []


@dataclass(frozen=True)
class _FakeFish:
    name: str
    size_rank: int


def test_register_fish_species_injection_point() -> None:
    # Rows with no ``species_id`` fall back to size-scaled max(1, size_rank).
    items.register_fish_species([_FakeFish("salmon", 5), _FakeFish("minnow", 1)])
    assert items.is_fish("salmon") is True
    assert items.item_value("salmon") == 5  # max(1, size_rank) fallback
    assert items.item_value("minnow") == 1
    assert items.classify("salmon") is items.ItemKind.RESOURCE


@dataclass(frozen=True)
class _IdFish:
    name: str  # market key (lookups lowercase, so use a lookup-safe id here)
    size_rank: int
    species_id: str  # neutral V043 key the fishing economy prices on


def test_register_fish_species_values_on_fishing_v043_curve() -> None:
    # Decision #7 (2026-07-18): a registered fish is worth its canonical fishing
    # V043 price — the fishing economy reused as one source of truth — not the
    # retired ad-hoc max(1, size_rank). Registered under the neutral species id
    # (a lookup-safe key), each mining-market value must equal the V043 price.
    from games.fishing.core import economy, species

    rows = [_IdFish(s.species_id, s.size_rank, s.species_id) for s in species.all_species()]
    items.register_fish_species(rows)
    for r in rows:
        assert items.item_value(r.name) == economy.sell_value(r.species_id)
    # Concretely: legend_carp is 80 on the V043 curve, not 4 (its size_rank).
    assert items.item_value("legend_carp") == 80
    assert items.item_value("legend_carp") != max(1, 4)


def test_register_fish_species_off_curve_falls_back_to_size_rank() -> None:
    # A species_id absent from the V043 curve keeps the size-scaled fallback,
    # so an ad-hoc injected row still values sanely (no KeyError, no minting).
    items.register_fish_species([_IdFish("kraken", 9, "kraken")])
    assert items.item_value("kraken") == 9  # max(1, size_rank), not on V043


def test_classify_and_tool_ladder() -> None:
    assert items.classify("pickaxe") is items.ItemKind.TOOL
    assert items.classify("diamond") is items.ItemKind.RESOURCE
    assert items.classify("stone hut") is items.ItemKind.STRUCTURE
    assert items.next_tool_upgrade("pickaxe") == "iron pickaxe"
    assert items.next_tool_upgrade("diamond pickaxe") is None


def test_market_no_arbitrage_only_resources_sell() -> None:
    assert market.sell_price("gold") == 6  # RESOURCE → sellable
    assert market.sell_price("pickaxe") is None  # TOOL → never sold
    assert market.sell_price("stone hut") is None  # STRUCTURE → never sold
    assert market.sell_price("lucky charm") is None  # TREASURE → never sold
    assert market.sell_price("who knows") is None  # unknown → never sold (no minting)


def test_gear_shop_prices_preserved() -> None:
    assert market.buy_price("torch") == 10
    assert market.buy_price("diamond pickaxe") == 320
    assert market.buy_price("stone") is None  # ore isn't in the shop


def test_total_sale_value_only_counts_resources() -> None:
    inv = {"gold": 2, "diamond": 1, "pickaxe": 1}
    # 2*6 + 1*12 = 24; the pickaxe (tool) contributes nothing.
    assert market.total_sale_value(inv) == 24


# ---------------------------------------------------------------------------
# Q-0267 theme leak R2 — the shop-section titles moved out of the dict literal
# inside shop_sections into the SHOP_SECTION_LABEL data table, keyed on neutral
# section ids. Pure relocation: byte-identical labels, same grouping/order.
# ---------------------------------------------------------------------------
def test_shop_section_labels_are_byte_identical() -> None:
    """The rendered section titles equal the exact strings that were inlined at
    market.py:181-192 (hand-listed expected set), in the same display order."""
    expected = ["⚔️ Weapons & shields", "🛡️ Armor", "🧰 Tools & supplies"]
    labels = [label for label, _ in market.shop_sections()]
    assert labels == expected
    # ...and each is sourced from the data table, not a branch literal.
    assert list(market.SHOP_SECTION_LABEL.values()) == expected


def test_shop_section_labels_come_from_the_data_table() -> None:
    """Swapping a SHOP_SECTION_LABEL row re-skins only that title; the grouping
    (which items land in which section) is byte-identical — table is load-bearing."""
    before = market.shop_sections()
    original = market.SHOP_SECTION_LABEL["weapons"]
    try:
        market.SHOP_SECTION_LABEL["weapons"] = "🔱 Reef arsenal"
        after = market.shop_sections()
    finally:
        market.SHOP_SECTION_LABEL["weapons"] = original
    assert after[0][0] == "🔱 Reef arsenal"  # only the label changed
    assert [rows for _, rows in after] == [rows for _, rows in before]  # grouping unchanged
    assert [lbl for lbl, _ in after][1:] == [lbl for lbl, _ in before][1:]


def test_shop_sections_has_no_inline_player_label() -> None:
    """shop_sections emits section titles only via SHOP_SECTION_LABEL — no
    player-facing title literal survives inside the function (audit §7 recipe #1)."""
    import ast
    import inspect

    tree = ast.parse(inspect.getsource(market))
    labels = set(market.SHOP_SECTION_LABEL.values())
    offenders: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "shop_sections":
            docstring = ast.get_docstring(node, clean=False)
            for sub in ast.walk(node):
                if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                    if sub.value != docstring and sub.value in labels:
                        offenders.append(repr(sub.value))
    assert not offenders, offenders
