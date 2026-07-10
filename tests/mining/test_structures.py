"""structures: forge tier gating + fishing-structure severance."""

from __future__ import annotations

from games.mining.core import structures


def test_only_mining_structures_registered() -> None:
    # forge / home / campfire remain; the four fishing structures are severed.
    assert set(structures.STRUCTURES) == {"forge", "home", "campfire"}
    for gone in ("tide_pool", "dock", "boathouse", "fishery"):
        assert not structures.is_structure(gone)
        assert not hasattr(structures, gone.upper())


def test_fishing_helpers_severed() -> None:
    for gone in (
        "tide_pool_pull_mult",
        "dock_bite_speed_mult",
        "boathouse_regen_mult",
        "fishery_bonus_chance",
    ):
        assert not hasattr(structures, gone)


def test_forge_build_ladder_preserved() -> None:
    c0 = structures.forge_build_cost(0)
    assert c0 is not None
    assert c0.coins == 3_000
    assert c0.materials == {"iron": 25, "stone": 15}
    c1 = structures.forge_build_cost(1)
    assert c1 is not None
    assert c1.coins == 8_000
    assert structures.forge_build_cost(2) is None  # maxed


def test_forge_level_required_only_top_two_tiers_gate() -> None:
    assert structures.FREE_TIER_CEILING == 3
    # bronze / iron / silver gear + tools + structures need no forge.
    assert structures.forge_level_required("bronze sword") == 0
    assert structures.forge_level_required("silver chestplate") == 0
    assert structures.forge_level_required("pickaxe") == 0
    assert structures.forge_level_required("stone hut") == 0
    # gold gear → forge 1; diamond gear → forge 2.
    assert structures.forge_level_required("gold sword") == 1
    assert structures.forge_level_required("diamond helmet") == 2


def test_meets_forge_requirement_gate() -> None:
    assert structures.meets_forge_requirement("gold sword", 0) is False
    assert structures.meets_forge_requirement("gold sword", 1) is True
    assert structures.meets_forge_requirement("diamond sword", 1) is False
    assert structures.meets_forge_requirement("diamond sword", 2) is True
    # additive: a free-tier recipe crafts at forge 0.
    assert structures.meets_forge_requirement("bronze sword", 0) is True


def test_tiers_unlocked_at() -> None:
    assert structures.tiers_unlocked_at(0) == ()
    assert structures.tiers_unlocked_at(1) == ("gold",)
    assert structures.tiers_unlocked_at(2) == ("gold", "diamond")


def test_campfire_gates_cooking() -> None:
    assert structures.cooking_unlocked(0) is False
    assert structures.cooking_unlocked(1) is True
