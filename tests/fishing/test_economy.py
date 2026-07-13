"""Tests for the V043 fishing economy curves (``games/fishing/core/economy.py``).

Pins the sim-lab VERDICT 043 constants VERBATIM (relayed as ORDER 007 item (2),
``control/inbox.md`` @ ``d6a9526`` via PR #80): the per-species sell curve, the
``xp_to_next(L) = 50·L`` progression curve, the L10/L25 milestone surfacing,
and the stat-neutrality of levels (the module feeds no resolver lever).
"""

from __future__ import annotations

import pytest

from games.fishing.core import economy
from games.fishing.core import species as species_table


# --- Sell curve: the V043 constants, verbatim -------------------------------


def test_sell_values_are_the_v043_constants_verbatim() -> None:
    assert economy.SELL_VALUES == {
        "minnow": 8,
        "bass": 13,
        "pike": 27,
        "legend_carp": 80,
    }


def test_sell_curve_covers_exactly_the_species_table() -> None:
    # The curve is keyed on the neutral species ids — no orphan or missing key.
    assert set(economy.SELL_VALUES) == set(species_table.species_ids())


@pytest.mark.parametrize("sid", species_table.species_ids())
def test_sell_value_reads_the_table(sid: str) -> None:
    assert economy.sell_value(sid) == economy.SELL_VALUES[sid]
    assert economy.is_sellable(sid)


def test_unknown_species_is_not_sellable_and_sell_value_raises() -> None:
    assert not economy.is_sellable("kraken")
    with pytest.raises(KeyError):
        economy.sell_value("kraken")


def test_sell_values_rise_with_size_rank() -> None:
    # A structural property of the pinned curve: bigger/rarer tiers sell higher.
    ranked = sorted(species_table.all_species(), key=lambda r: r.size_rank)
    values = [economy.SELL_VALUES[r.species_id] for r in ranked]
    assert values == sorted(values)


# --- Progression curve: xp_to_next(L) = 50·L --------------------------------


def test_xp_to_next_is_fifty_times_level() -> None:
    for level in (1, 2, 9, 10, 24, 25, 100):
        assert economy.xp_to_next(level) == 50 * level


def test_xp_to_next_rejects_below_base_level() -> None:
    with pytest.raises(ValueError):
        economy.xp_to_next(0)


def test_cumulative_xp_is_the_curve_summed() -> None:
    # cumulative_xp_for(L) must equal summing xp_to_next over L1..L-1 exactly.
    total = 0
    for level in range(1, 30):
        assert economy.cumulative_xp_for(level) == total
        total += economy.xp_to_next(level)


def test_level_for_xp_walks_the_curve() -> None:
    assert economy.level_for_xp(0) == 1
    assert economy.level_for_xp(49) == 1
    assert economy.level_for_xp(50) == 2  # xp_to_next(1) = 50
    assert economy.level_for_xp(149) == 2  # next step needs +100
    assert economy.level_for_xp(150) == 3
    assert economy.level_for_xp(-5) == 1  # clamps to the base level


def test_milestones_surface_at_l10_and_l25() -> None:
    assert economy.MILESTONE_LEVELS == (10, 25)
    to_l10 = economy.cumulative_xp_for(10)
    assert economy.milestones_crossed(to_l10 - 1, to_l10) == (10,)
    to_l25 = economy.cumulative_xp_for(25)
    assert economy.milestones_crossed(to_l25 - 1, to_l25) == (25,)
    # One jump across both milestones surfaces both, in order.
    assert economy.milestones_crossed(0, to_l25) == (10, 25)
    # No crossing → nothing surfaces.
    assert economy.milestones_crossed(0, 49) == ()


# --- Stat neutrality: the economy module feeds no resolver lever ------------


def test_economy_module_is_stat_neutral_by_construction() -> None:
    """Levels are a readout: economy.py imports no resolver/equipment module.

    The V043 constraint 'levels stay STAT-NEUTRAL' is structural — nothing in
    the module's source touches ``fishing_power`` / ``bite_luck`` / the catch
    resolver, so a level CANNOT alter a cast.
    """
    import inspect

    src = inspect.getsource(economy)
    # Strip the module docstring (which NAMES the levers to disclaim them);
    # the executable body must not reference any resolver/equipment lever.
    body = src.split('"""', 2)[2]
    assert "fishing_power" not in body
    assert "bite_luck" not in body
    assert "resolve_cast" not in body
    assert "equipment" not in body
    assert "import" not in body or "from games" not in body  # no game imports
