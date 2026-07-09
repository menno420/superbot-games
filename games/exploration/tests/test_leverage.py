"""Leverage tests: base floor, hard cap, monotonicity, step boundaries."""

from __future__ import annotations

from games.exploration.quest.leverage import (
    BASE_MENU_WIDTH,
    MAX_MENU_WIDTH,
    XP_PER_EXTRA_OPTION,
    menu_width,
)


def test_zero_xp_is_base() -> None:
    assert menu_width(0) == BASE_MENU_WIDTH == 2


def test_negative_xp_is_base() -> None:
    assert menu_width(-100) == BASE_MENU_WIDTH


def test_large_xp_caps_at_max() -> None:
    assert menu_width(10_000_000) == MAX_MENU_WIDTH == 4


def test_step_at_xp_per_extra_option() -> None:
    assert menu_width(XP_PER_EXTRA_OPTION - 1) == 2
    assert menu_width(XP_PER_EXTRA_OPTION) == 3
    assert menu_width(2 * XP_PER_EXTRA_OPTION) == 4
    assert menu_width(3 * XP_PER_EXTRA_OPTION) == 4  # capped


def test_monotonic_non_decreasing() -> None:
    prev = menu_width(0)
    for xp in range(0, 5_000, 37):
        cur = menu_width(xp)
        assert cur >= prev
        assert BASE_MENU_WIDTH <= cur <= MAX_MENU_WIDTH
        prev = cur
