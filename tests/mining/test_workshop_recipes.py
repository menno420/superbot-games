"""workshop (repair pricing derives from shop) + recipes (pure, injectable)."""

from __future__ import annotations

from games.mining.core import recipes, workshop


def test_repair_base_derives_from_shop_price() -> None:
    assert workshop.REPAIR_RATE == 0.5
    # torch shop price 10 → full repair = ceil(10 * 0.5) = 5.
    assert workshop.repair_base("torch") == 5
    # diamond pickaxe 320 → ceil(320 * 0.5) = 160.
    assert workshop.repair_base("diamond pickaxe") == 160
    assert workshop.repair_base("not in shop") is None


def test_repair_cost_proportional_to_wear() -> None:
    # pickaxe: shop 25 → base ceil(12.5)=13; max_durability 60.
    # from remaining 0 → missing 60 → ceil(13 * 60/60) = 13.
    assert workshop.repair_cost("pickaxe", 0) == 13
    # fully repaired → None (nothing to pay).
    assert workshop.repair_cost("pickaxe", 60) is None


def test_wear_plan_shape_preserved() -> None:
    assert set(workshop.WEAR_PLAN) == {"mine", "explore", "duel"}
    # mine wears the tool (always) + light (underground only).
    assert workshop.WEAR_PLAN["mine"] == (("tool", False), ("light", True))


def test_durability_bar_renders() -> None:
    assert workshop.durability_bar(60, 60).endswith("60/60")
    assert workshop.durability_bar(0, 60).startswith("▱")


def test_recipes_defaults_pure_no_io() -> None:
    r = recipes.load_recipes()
    assert r == recipes.DEFAULT_RECIPES
    assert r["pickaxe"] == {"wood": 2, "stone": 3}
    # A fresh top-level dict (oracle-faithful ``dict(DEFAULT_RECIPES)`` shallow
    # copy): adding/removing recipes doesn't mutate the module default.
    r["new recipe"] = {"stone": 1}
    assert "new recipe" not in recipes.DEFAULT_RECIPES


def test_recipes_injection_normalises_like_the_oracle_loader() -> None:
    injected = {"Stone Hut": {"Stone": 7}, "junk": "nope", "bad": {"x": "y"}}
    out = recipes.load_recipes(injected)
    assert out == {"stone hut": {"stone": 7}}  # lower-cased, non-int/junk skipped
    # an empty/invalid payload falls back to the safe defaults.
    assert recipes.load_recipes({}) == recipes.DEFAULT_RECIPES
    assert recipes.load_recipes("garbage") == recipes.DEFAULT_RECIPES
