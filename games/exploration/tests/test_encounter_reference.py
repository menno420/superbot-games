"""Reference encounter resolver tests: determinism, triggers, allowed kinds."""

from __future__ import annotations

from games.shared.encounter.interface import (
    EncounterRequest,
    EncounterResolver,
    EncounterTrigger,
)
from games.shared.encounter.reference import (
    ALLOWED_KINDS,
    ReferenceEncounterResolver,
)


def _req(trigger: EncounterTrigger, seed: object = "w", player: str = "p1") -> EncounterRequest:
    return EncounterRequest(
        trigger=trigger,
        player_id=player,
        world_seed=seed,
        context={"zone": "north", "step": 3},
    )


def test_satisfies_protocol() -> None:
    assert isinstance(ReferenceEncounterResolver(), EncounterResolver)


def test_deterministic_per_request() -> None:
    r = ReferenceEncounterResolver()
    req = _req(EncounterTrigger.GRID_ROAM)
    assert r.resolve(req) == r.resolve(req)


def test_all_three_triggers_resolve_to_known_kind() -> None:
    r = ReferenceEncounterResolver()
    for trigger in EncounterTrigger:
        outcome = r.resolve(_req(trigger))
        assert outcome.kind in ALLOWED_KINDS
        assert outcome.payload["trigger"] == trigger.value


def test_different_seeds_can_differ() -> None:
    r = ReferenceEncounterResolver()
    kinds = {
        r.resolve(_req(EncounterTrigger.GRID_ROAM, seed=f"w{i}")).kind
        for i in range(50)
    }
    # Across many seeds the reference table should produce more than one kind.
    assert len(kinds) > 1


def test_outcome_kind_always_in_allowed_set() -> None:
    r = ReferenceEncounterResolver()
    for i in range(300):
        for trigger in EncounterTrigger:
            outcome = r.resolve(_req(trigger, seed=i, player=f"p{i}"))
            assert outcome.kind in ALLOWED_KINDS
            assert 1 <= outcome.payload["intensity"] <= 5
