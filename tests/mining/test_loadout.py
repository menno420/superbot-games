"""loadout (the set-aware "Equip Best" picker) — greedy vs full-set candidates.

Pins :func:`games.mining.core.loadout.best_loadout` at the EXISTING gear
constants (games/mining/core/equipment.py — no numbers changed here):

* the per-slot greedy pick, and when a complete same-tier set (set bonus
  included) must beat it — the module's whole reason to exist is choosing
  correctly between those two candidates;
* the crossover the other way (a big enough higher-tier piece breaks the set);
* edge cases: empty / zero-qty / unequippable inventories, incomplete tiers,
  mixed-case item names.

Power arithmetic used in the comments below (power = sum of a loadout's
EffectiveStats fields): full bronze set items = 4+15+3+8+5+3 = 38, bronze set
bonus (+1 damage, +3 max_health) = +4; iron chestplate = 10 vs bronze 8;
diamond sword = 10 vs bronze 4.
"""

from __future__ import annotations

from games.mining.core import equipment
from games.mining.core.loadout import best_loadout

FULL_BRONZE = {
    "bronze sword": 1,
    "bronze shield": 1,
    "bronze helmet": 1,
    "bronze chestplate": 1,
    "bronze leggings": 1,
    "bronze boots": 1,
}

BRONZE_SET_LOADOUT = {
    equipment.WEAPON: "bronze sword",
    equipment.SHIELD: "bronze shield",
    equipment.HELMET: "bronze helmet",
    equipment.CHESTPLATE: "bronze chestplate",
    equipment.LEGGINGS: "bronze leggings",
    equipment.BOOTS: "bronze boots",
}


def test_empty_inventory_yields_empty_loadout() -> None:
    assert best_loadout({}) == {}


def test_zero_quantity_items_are_not_owned() -> None:
    # qty < 1 rows are dead stock — never equipped, never a set piece.
    assert best_loadout({"iron sword": 0, "bronze shield": -2}) == {}


def test_unequippable_items_are_ignored() -> None:
    # Resources/loot without a gear slot can't fill a loadout.
    assert best_loadout({"stone": 99, "gold ore": 5, "fish": 3}) == {}


def test_greedy_picks_strongest_owned_item_per_slot() -> None:
    picked = best_loadout(
        {"bronze sword": 1, "iron sword": 1, "torch": 1, "lantern": 1},
    )
    # iron sword (6) > bronze sword (4); lantern (4) > torch (2).
    assert picked == {equipment.WEAPON: "iron sword", equipment.LIGHT: "lantern"}


def test_every_pick_lands_in_its_own_slot() -> None:
    # Invariant: the result maps each slot to an item that equips THERE.
    inventory = {**FULL_BRONZE, "diamond pickaxe": 1, "lucky charm": 1}
    picked = best_loadout(inventory)
    for slot, item in picked.items():
        assert equipment.slot_for(item) == slot


def test_complete_set_beats_a_single_higher_tier_piece() -> None:
    # Greedy would grab the iron chestplate (10 > 8) and break the set:
    # greedy = 38 - 8 + 10 = 40, full-bronze + set bonus = 38 + 4 = 42.
    picked = best_loadout({**FULL_BRONZE, "iron chestplate": 1})
    assert picked == BRONZE_SET_LOADOUT
    assert equipment.active_set_tier(picked) == "bronze"


def test_big_enough_piece_gap_breaks_the_set() -> None:
    # diamond sword swings +6 over bronze (10 vs 4) — more than the +4 set
    # bonus, so greedy (44) beats the full-bronze candidate (42).
    picked = best_loadout({**FULL_BRONZE, "diamond sword": 1})
    assert picked[equipment.WEAPON] == "diamond sword"
    assert picked[equipment.CHESTPLATE] == "bronze chestplate"
    assert equipment.active_set_tier(picked) is None


def test_set_candidate_keeps_greedy_picks_for_non_set_slots() -> None:
    # Mining gear rides along untouched when the set candidate wins.
    inventory = {
        **FULL_BRONZE,
        "iron chestplate": 1,  # makes the set candidate the winner (42 > 40)
        "diamond pickaxe": 1,
        "diamond lantern": 1,
        "lucky charm": 1,
    }
    picked = best_loadout(inventory)
    assert picked == {
        **BRONZE_SET_LOADOUT,
        equipment.TOOL: "diamond pickaxe",
        equipment.LIGHT: "diamond lantern",
        equipment.CHARM: "lucky charm",
    }


def test_incomplete_tier_spawns_no_set_candidate() -> None:
    # Same crossover inventory as the set-beats-greedy case, minus the bronze
    # chestplate: 5/6 bronze is no set, so greedy's iron chestplate stands.
    inventory = {**FULL_BRONZE, "iron chestplate": 1}
    del inventory["bronze chestplate"]
    picked = best_loadout(inventory)
    assert picked[equipment.CHESTPLATE] == "iron chestplate"
    assert equipment.active_set_tier(picked) is None


def test_strongest_complete_tier_wins_when_two_sets_owned() -> None:
    diamond = {f"diamond {fam}": 1 for fam in
               ("sword", "shield", "helmet", "chestplate", "leggings", "boots")}
    picked = best_loadout({**FULL_BRONZE, **diamond})
    # Every diamond piece out-powers its bronze sibling, so greedy already
    # assembles the full diamond set (bonus included via compute_stats).
    assert picked == {slot: f"diamond {fam}"
                      for slot, fam in zip(equipment.SET_SLOTS,
                                           ("sword", "shield", "helmet",
                                            "chestplate", "leggings", "boots"))}
    assert equipment.active_set_tier(picked) == "diamond"


def test_mixed_case_inventory_still_resolves() -> None:
    # Inventories may carry display-cased names; slot/stat lookups lowercase.
    # Pins current behavior: when the set candidate wins, its six set-slot
    # names come back lowercased (constructed "{tier} {family}" strings),
    # regardless of the inventory's casing.
    cased = {name.title(): 1 for name in FULL_BRONZE}
    picked = best_loadout({**cased, "Iron Chestplate": 1})
    assert picked == BRONZE_SET_LOADOUT
