"""Predicate matching tests: match, mismatch, count_field increments."""

from __future__ import annotations

from games.exploration.quest.predicates import (
    GameEvent,
    evaluate,
    event_type_match,
    registered_predicates,
)


def test_match_increments_by_one() -> None:
    ev = GameEvent(type="item_delivered", payload={"item": "supply_crate"})
    assert evaluate("item_delivered", ev, {"match": {"item": "supply_crate"}}) == 1


def test_mismatch_is_zero() -> None:
    ev = GameEvent(type="item_delivered", payload={"item": "rock"})
    assert evaluate("item_delivered", ev, {"match": {"item": "supply_crate"}}) == 0


def test_wrong_event_type_is_zero() -> None:
    ev = GameEvent(type="target_defeated", payload={"item": "supply_crate"})
    assert evaluate("item_delivered", ev, {"match": {"item": "supply_crate"}}) == 0


def test_count_field_increment() -> None:
    ev = GameEvent(type="clue_found", payload={"amount": 3})
    assert evaluate("clue_found", ev, {"count_field": "amount"}) == 3


def test_count_field_missing_defaults_to_one() -> None:
    ev = GameEvent(type="clue_found", payload={})
    assert evaluate("clue_found", ev, {"count_field": "amount"}) == 1


def test_count_field_bool_not_treated_as_int() -> None:
    ev = GameEvent(type="clue_found", payload={"amount": True})
    assert evaluate("clue_found", ev, {"count_field": "amount"}) == 1


def test_general_matcher_direct() -> None:
    ev = GameEvent(type="npc_reached", payload={"npc": "traveler", "dest": "waystation"})
    params = {
        "event_type": "npc_reached",
        "match": {"npc": "traveler", "dest": "waystation"},
    }
    assert event_type_match(ev, params) == 1
    # A partial payload mismatch -> 0.
    ev2 = GameEvent(type="npc_reached", payload={"npc": "traveler", "dest": "town"})
    assert event_type_match(ev2, params) == 0


def test_unknown_predicate_raises() -> None:
    ev = GameEvent(type="x", payload={})
    try:
        evaluate("does_not_exist", ev, {})
    except KeyError:
        pass
    else:
        raise AssertionError("expected KeyError for unknown predicate")


def test_registry_contains_aliases() -> None:
    names = registered_predicates()
    for alias in (
        "item_delivered",
        "npc_reached",
        "target_defeated",
        "location_reached",
        "captive_freed",
        "clue_found",
    ):
        assert alias in names
