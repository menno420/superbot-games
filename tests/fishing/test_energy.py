"""Energy — a cast spends ``CAST_COST`` through the REUSED mining energy engine, and an
out-of-energy player gets an honest no-bite (never an exception).

Fishing does not roll its own fuel model: it debits :data:`catch.CAST_COST` through
``games.mining.core.energy`` (the same passive-regen engine mining digs against), so the
two games share one energy economy.
"""

from __future__ import annotations

from games.fishing.core import catch
from games.mining.core import energy


def test_a_cast_reports_the_cast_cost_energy() -> None:
    # With a full bar, a cast (bite or not) costs exactly CAST_COST.
    out = catch.resolve_cast(1, "dock", energy=energy.MAX_ENERGY)
    assert out.energy_cost == catch.CAST_COST


def test_cast_cost_is_spent_through_the_reused_energy_engine() -> None:
    # The workflow layer would debit the reported cost via the shared engine; prove the
    # round-trip lands where the engine says it should (no parallel fuel math).
    now = 1_000_000
    state = energy.EnergyState(current=energy.MAX_ENERGY, updated_at=now)
    out = catch.resolve_cast(1, "dock", energy=state.current)
    assert energy.can_dig(state, now, cost=out.energy_cost)  # affordable
    after = energy.spend(state, now, cost=out.energy_cost)
    assert after.current == energy.MAX_ENERGY - catch.CAST_COST


def test_insufficient_energy_is_an_honest_no_bite_not_an_exception() -> None:
    # Below the cast cost → no bite, no catch, nothing spent — and it never raises.
    out = catch.resolve_cast(1, "dock", energy=catch.CAST_COST - 1)
    assert out.bit is False
    assert out.catch is None
    assert out.energy_cost == 0


def test_zero_energy_still_returns_a_valid_outcome() -> None:
    out = catch.resolve_cast(42, "reef", energy=0)
    assert isinstance(out, catch.CastOutcome)
    assert out.bit is False and out.catch is None and out.energy_cost == 0


def test_exactly_enough_energy_can_cast() -> None:
    # A player with exactly CAST_COST can cast (the gate is `< CAST_COST`, not `<=`).
    out = catch.resolve_cast(1, "dock", energy=catch.CAST_COST)
    assert out.energy_cost == catch.CAST_COST


def test_cooked_fish_feeds_back_into_the_shared_energy_engine() -> None:
    # The reused engine already knows "cooked fish" restores energy — fishing's own
    # output (fish → cooked) tops the same bar back up. One economy, both directions.
    assert energy.restore_value("cooked fish") == 30
