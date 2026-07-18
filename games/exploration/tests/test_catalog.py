"""Catalog shape + balance-cap tests: 5 templates, 3 tiers, monotonic, in-bounds."""

from __future__ import annotations

from games.exploration.quest.catalog import (
    GLOBAL_MAX,
    TEMPLATES,
    TIER_CAPS,
    menu,
)
from games.exploration.quest.models import QuestKind, RewardTier

_NUMERIC_FIELDS = ("global_xp", "game_xp", "currency")


def test_exactly_five_templates() -> None:
    assert len(TEMPLATES) == 5
    assert len(menu()) == 5
    assert set(menu()) == set(TEMPLATES)


def test_all_five_kinds_present() -> None:
    kinds = {t.kind for t in TEMPLATES.values()}
    assert kinds == set(QuestKind)


def test_three_tiers_defined() -> None:
    assert set(TIER_CAPS) == set(RewardTier)


def test_every_tier_within_global_max() -> None:
    for tier, cap in TIER_CAPS.items():
        for field in _NUMERIC_FIELDS:
            assert getattr(cap, field) <= getattr(GLOBAL_MAX, field), (tier, field)


def test_tiers_strictly_monotonic() -> None:
    i, ii, iii = TIER_CAPS[RewardTier.I], TIER_CAPS[RewardTier.II], TIER_CAPS[RewardTier.III]
    for field in _NUMERIC_FIELDS:
        assert getattr(i, field) < getattr(ii, field) < getattr(iii, field), field


def test_every_template_has_objective_and_capability() -> None:
    for template in TEMPLATES.values():
        assert len(template.objectives) >= 1
        assert template.prestige_capability
        for obj in template.objectives:
            assert obj.required >= 1
            assert obj.predicate


def test_menu_is_ordered_ids() -> None:
    assert menu() == tuple(TEMPLATES.keys())


def test_every_template_and_objective_is_hashable() -> None:
    # The models docstring promises Objective/QuestTemplate stay hashable and
    # frozen — the reason params is a tuple of pairs. A nested dict value in
    # those pairs (as the catalog carries) must not break that invariant.
    for template in TEMPLATES.values():
        assert hash(template) == hash(template)
        for obj in template.objectives:
            assert hash(obj) == hash(obj)


def test_match_params_dict_reconstructs_plain_dict() -> None:
    # params_dict() must hand consumers the plain nested dict content unchanged.
    supply_run = TEMPLATES["supply_run"]
    (objective,) = supply_run.objectives
    assert objective.params_dict() == {"match": {"item": "supply_crate"}}

    escort = TEMPLATES["safe_passage"].objectives[0]
    assert escort.params_dict() == {"match": {"npc": "traveler", "dest": "waystation"}}
