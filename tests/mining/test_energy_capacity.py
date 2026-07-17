"""energy + capacity/vault formulas (preserved verbatim from the oracle)."""

from __future__ import annotations

import math

from games.mining.core import capacity, energy


def test_energy_constants_preserved() -> None:
    assert energy.MAX_ENERGY == 60
    assert energy.DIG_COST == 1
    assert energy.REGEN_SECONDS == 10
    assert energy.RESTORE_VALUES == {"ration": 25, "energy drink": 50, "cooked fish": 30}


def test_settle_passive_regen_floor_divides() -> None:
    s = energy.settle(energy.EnergyState(0, 0), now=95)
    assert s.current == 9  # 95 // 10
    # sub-interval remainder preserved: updated_at advances only by whole steps.
    assert s.updated_at == 90


def test_settle_caps_at_max_and_stamps_now() -> None:
    s = energy.settle(energy.EnergyState(0, 0), now=10_000)
    assert s.current == energy.MAX_ENERGY
    assert s.updated_at == 10_000


def test_settle_is_idempotent_across_repeated_calls() -> None:
    # settling every second must equal settling once (no discarded remainder).
    once = energy.settle(energy.EnergyState(0, 0), now=57)
    step = energy.EnergyState(0, 0)
    for t in range(1, 58):
        step = energy.settle(step, now=t)
    assert step.current == once.current


def test_fresh_player_regens_to_full_from_epoch() -> None:
    # a missing DB row = (0, 0) → regenerates to full by any large 'now'.
    assert energy.settle(energy.EnergyState(0, 0), now=999_999).current == 60


def test_spend_and_can_dig() -> None:
    full = energy.EnergyState(60, 1000)
    assert energy.can_dig(full, now=1000) is True
    after = energy.spend(full, now=1000)
    assert after.current == 59
    empty = energy.EnergyState(0, 1000)
    assert energy.can_dig(empty, now=1000) is False


def test_restore_caps_at_max() -> None:
    s = energy.restore(energy.EnergyState(50, 1000), now=1000, amount=50)
    assert s.current == 60
    assert energy.restore_value("energy drink") == 50
    assert energy.restore_value("stone") is None


def test_seconds_until_already_reached_returns_zero() -> None:
    # target at or below current settled energy → already there, 0 wait.
    full = energy.EnergyState(60, 1000)
    assert energy.seconds_until(full, now=1000, target=60) == 0
    assert energy.seconds_until(full, now=1000, target=10) == 0


def test_seconds_until_reachable_target_counts_regen_seconds() -> None:
    # empty bar, no partial remainder: 5 units × 10s/unit = 50s to reach 5.
    empty = energy.EnergyState(0, 1000)
    assert energy.seconds_until(empty, now=1000, target=5) == 50
    # sub-interval remainder is credited: 7s already elapsed toward the next unit.
    assert energy.seconds_until(empty, now=1007, target=5) == 50 - 7
    # a full bar is reachable in 0s.
    assert energy.seconds_until(empty, now=1000, target=60) == 600


def test_seconds_until_unreachable_target_is_infinite_not_zero() -> None:
    # target above max_energy can never be reached by passive regen — it must
    # signal that honestly (math.inf), not read as "already reached" (0).
    full = energy.EnergyState(60, 1000)
    assert energy.seconds_until(full, now=1000, target=61) == math.inf
    assert energy.seconds_until(full, now=1000, target=999) == math.inf
    # unreachable even from an empty bar (regression: old clamp returned a
    # finite wait to the cap, masking the out-of-range target).
    empty = energy.EnergyState(0, 1000)
    assert energy.seconds_until(empty, now=1000, target=61) == math.inf
    # honors a caller-supplied max_energy for the reachability boundary.
    assert energy.seconds_until(full, now=1000, target=61, max_energy=100) == 10
    assert energy.seconds_until(full, now=1000, target=200, max_energy=100) == math.inf


def test_vault_capacity_ladder() -> None:
    assert capacity.BASE_VAULT_CAP == 30
    assert capacity.VAULT_SLOTS_PER_LEVEL == 15
    assert capacity.MAX_VAULT_LEVEL == 6
    assert capacity.vault_capacity(0) == 30
    assert capacity.vault_capacity(1) == 45
    assert capacity.vault_capacity(6) == 120
    # clamped to the ladder ceiling.
    assert capacity.vault_capacity(99) == 120


def test_vault_upgrade_cost_rises_then_maxes_out() -> None:
    assert capacity.vault_upgrade_cost(0) == 2_000
    assert capacity.vault_upgrade_cost(1) == 3_500
    assert capacity.vault_upgrade_cost(5) == 9_500
    assert capacity.vault_upgrade_cost(6) is None  # maxed → no upgrade


def test_pack_soft_cap_only_warns_never_blocks() -> None:
    assert capacity.PACK_SOFT_CAP == 40
    inv = {f"item{i}": 1 for i in range(40)}
    status = capacity.pack_status(inv)
    assert status.at_cap is True
    assert capacity.pack_warning(status) is not None
    # under cap → no warning.
    assert capacity.pack_warning(capacity.pack_status({"stone": 5})) is None


def test_distinct_types_counts_kinds_not_quantity() -> None:
    # a huge single stack is one type; zero-qty rows don't count.
    assert capacity.distinct_types({"stone": 9999, "gold": 0, "iron": 3}) == 2
