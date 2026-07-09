"""Engine lifecycle tests: determinism, guards, progress, clamping, rewards."""

from __future__ import annotations

import pytest

from games.exploration.quest import catalog, engine
from games.exploration.quest.models import (
    QuestState,
    QuestStateError,
    RewardTier,
)
from games.exploration.quest.predicates import GameEvent


def _deliver(item: str = "supply_crate") -> GameEvent:
    return GameEvent(type="item_delivered", payload={"item": item})


def test_offer_is_deterministic() -> None:
    a = engine.offer("supply_run", "p1", RewardTier.II, "world-42")
    b = engine.offer("supply_run", "p1", RewardTier.II, "world-42")
    assert a == b
    assert a.seed == b.seed
    assert a.instance_id == b.instance_id
    assert a.state is QuestState.OFFERED
    # Distinct inputs -> distinct seed/id.
    c = engine.offer("supply_run", "p2", RewardTier.II, "world-42")
    assert c.seed != a.seed
    assert c.instance_id != a.instance_id


def test_offer_zeroes_progress() -> None:
    inst = engine.offer("supply_run", "p1", RewardTier.I, "w")
    assert len(inst.progress) == 1
    assert inst.progress[0].current == 0
    assert inst.progress[0].required == 3


def test_accept_guard() -> None:
    inst = engine.offer("supply_run", "p1", RewardTier.I, "w")
    active = engine.accept(inst)
    assert active.state is QuestState.ACTIVE
    with pytest.raises(QuestStateError):
        engine.accept(active)  # already ACTIVE


def test_single_objective_lifecycle_to_completed() -> None:
    inst = engine.accept(engine.offer("supply_run", "p1", RewardTier.I, "w"))
    for _ in range(3):
        inst = engine.apply_event(inst, _deliver())
    assert inst.state is QuestState.COMPLETED
    assert inst.step == 3
    assert inst.progress[0].current == 3


def test_multi_objective_lifecycle_to_completed() -> None:
    inst = engine.accept(engine.offer("missing_scout", "p1", RewardTier.III, "w"))
    inst = engine.apply_event(
        inst, GameEvent(type="location_reached", payload={"loc": "cavern"})
    )
    assert inst.state is QuestState.ACTIVE  # one objective still open
    inst = engine.apply_event(inst, GameEvent(type="captive_freed", payload={}))
    assert inst.state is QuestState.COMPLETED


def test_events_ignored_when_not_active() -> None:
    offered = engine.offer("supply_run", "p1", RewardTier.I, "w")
    # OFFERED (not ACTIVE) -> event ignored, unchanged.
    assert engine.apply_event(offered, _deliver()) == offered
    completed = engine.accept(offered)
    for _ in range(3):
        completed = engine.apply_event(completed, _deliver())
    assert completed.state is QuestState.COMPLETED
    # Further events after COMPLETED are ignored.
    assert engine.apply_event(completed, _deliver()) == completed


def test_overshoot_clamps_to_required() -> None:
    inst = engine.accept(engine.offer("cull_the_pack", "p1", RewardTier.I, "w"))
    big = GameEvent(type="target_defeated", payload={"species": "dire_wolf", "n": 99})
    # count_field not used by this template, so each event increments by 1.
    for _ in range(10):
        inst = engine.apply_event(inst, big)
    assert inst.progress[0].current == 5  # clamped to required
    assert inst.state is QuestState.COMPLETED


def test_mismatched_events_do_not_advance() -> None:
    inst = engine.accept(engine.offer("supply_run", "p1", RewardTier.I, "w"))
    inst = engine.apply_event(inst, _deliver(item="rock"))
    assert inst.progress[0].current == 0
    assert inst.state is QuestState.ACTIVE
    assert inst.step == 1  # step still bumps


def test_grant_rewards_equals_tier_cap() -> None:
    inst = engine.accept(engine.offer("supply_run", "p1", RewardTier.II, "w"))
    for _ in range(3):
        inst = engine.apply_event(inst, _deliver())
    bundle = engine.grant_rewards(inst)
    cap = catalog.TIER_CAPS[RewardTier.II]
    assert bundle.global_xp == cap.global_xp
    assert bundle.game_xp == cap.game_xp
    assert bundle.currency == cap.currency


def test_grant_rewards_requires_completed() -> None:
    inst = engine.accept(engine.offer("supply_run", "p1", RewardTier.I, "w"))
    with pytest.raises(QuestStateError):
        engine.grant_rewards(inst)


def test_tier_iii_grants_capability() -> None:
    inst = engine.accept(engine.offer("supply_run", "p1", RewardTier.III, "w"))
    for _ in range(3):
        inst = engine.apply_event(inst, _deliver())
    bundle = engine.grant_rewards(inst)
    assert bundle.capability == "trade_route_unlock"


def test_tier_i_and_ii_grant_no_capability() -> None:
    for tier in (RewardTier.I, RewardTier.II):
        inst = engine.accept(engine.offer("supply_run", "p1", tier, "w"))
        for _ in range(3):
            inst = engine.apply_event(inst, _deliver())
        assert engine.grant_rewards(inst).capability is None


def test_terminal_transitions() -> None:
    offered = engine.offer("supply_run", "p1", RewardTier.I, "w")
    assert engine.abandon(offered).state is QuestState.FAILED
    assert engine.expire(offered).state is QuestState.EXPIRED
    active = engine.accept(offered)
    assert engine.fail(active).state is QuestState.FAILED
    # Cannot re-transition a terminal instance.
    with pytest.raises(QuestStateError):
        engine.abandon(engine.fail(active))
