"""Objective predicate matching — EventBus-predicate progress model.

Objectives advance by matching game events. The engine does NOT subscribe to
anything itself: the host's EventBus adapter turns a bus event into a
``GameEvent`` and calls ``engine.apply_event``. A predicate is a pure function
``(GameEvent, params_dict) -> int`` returning the increment for one objective
(0 when the event does not match).

The single general matcher ``event_type_match`` backs every registered alias:
- ``event_type`` — the required ``GameEvent.type``.
- ``match`` — every key/value pair here must be present & equal in the payload.
- ``count_field`` — optional payload key whose integer value is the increment;
  when absent (or the field is missing) a match increments by 1.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

Predicate = Callable[["GameEvent", Mapping[str, object]], int]


@dataclass(frozen=True)
class GameEvent:
    """A normalized game event handed to the engine by the host's EventBus adapter."""

    type: str
    payload: Mapping[str, object]


def event_type_match(event: "GameEvent", params: Mapping[str, object]) -> int:
    """General matcher: gate on event type + payload equality, then increment.

    ``params`` keys:
      - ``event_type`` (str, required): the type this predicate matches.
      - ``match`` (mapping, optional): payload keys that must all equal.
      - ``count_field`` (str, optional): payload key read as the integer increment.
    """
    want_type = params.get("event_type")
    if want_type is not None and event.type != want_type:
        return 0

    match = params.get("match") or {}
    if isinstance(match, Mapping):
        for key, value in match.items():
            if event.payload.get(key) != value:
                return 0

    count_field = params.get("count_field")
    if count_field is not None:
        raw = event.payload.get(count_field)
        if isinstance(raw, bool):  # bool is an int subclass — reject explicitly
            return 1
        if isinstance(raw, int):
            return raw
        return 1
    return 1


def _typed(event_type: str) -> Predicate:
    """Build an alias predicate that pins ``event_type`` onto the general matcher."""

    def predicate(event: "GameEvent", params: Mapping[str, object]) -> int:
        merged = dict(params)
        merged.setdefault("event_type", event_type)
        return event_type_match(event, merged)

    return predicate


# Five readable aliases used by the v1 catalog templates. Each is the general
# matcher with its event_type pinned; the template supplies ``match``/``count_field``.
_REGISTRY: dict[str, Predicate] = {
    "event_type_match": event_type_match,
    "item_delivered": _typed("item_delivered"),
    "npc_reached": _typed("npc_reached"),
    "target_defeated": _typed("target_defeated"),
    "location_reached": _typed("location_reached"),
    "captive_freed": _typed("captive_freed"),
    "clue_found": _typed("clue_found"),
}


def evaluate(
    predicate_name: str, event: "GameEvent", params: Mapping[str, object]
) -> int:
    """Look up ``predicate_name`` and return its increment for ``event``."""
    predicate = _REGISTRY.get(predicate_name)
    if predicate is None:
        raise KeyError(f"unknown predicate: {predicate_name!r}")
    return predicate(event, params)


def registered_predicates() -> tuple[str, ...]:
    """Return the sorted names of all registered predicates (for introspection/tests)."""
    return tuple(sorted(_REGISTRY))
