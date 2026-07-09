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
    items.register_fish_species([_FakeFish("salmon", 5), _FakeFish("minnow", 1)])
    assert items.is_fish("salmon") is True
    assert items.item_value("salmon") == 5  # max(1, size_rank)
    assert items.item_value("minnow") == 1
    assert items.classify("salmon") is items.ItemKind.RESOURCE


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
