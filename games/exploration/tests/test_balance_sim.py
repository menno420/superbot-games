"""Balance-pin: no reward the engine can emit exceeds the Q-0087 caps; results are reproducible."""

from __future__ import annotations

from games.exploration.quest import catalog, engine
from games.exploration.quest.models import (
    QuestInstance,
    QuestState,
    QuestTemplate,
    RewardTier,
)
from games.exploration.quest.predicates import GameEvent

_NUMERIC_FIELDS = ("global_xp", "game_xp", "currency")
_SEEDS = range(1000)


def _satisfying_events(template: QuestTemplate) -> list[GameEvent]:
    """Build the exact events that complete every objective of a template.

    For the v1 aliases the predicate name equals the event type, and the
    objective's ``match`` params are the required payload; one event per unit of
    ``required``.
    """
    events: list[GameEvent] = []
    for obj in template.objectives:
        match = obj.params_dict().get("match") or {}
        payload = dict(match) if isinstance(match, dict) else {}
        for _ in range(obj.required):
            events.append(GameEvent(type=obj.predicate, payload=dict(payload)))
    return events


def _run_lifecycle(template_id: str, tier: RewardTier, seed: int) -> QuestInstance:
    inst = engine.accept(engine.offer(template_id, f"p{seed}", tier, f"world-{seed}"))
    for ev in _satisfying_events(catalog.get(template_id)):
        inst = engine.apply_event(inst, ev)
    return inst


def _aggregate() -> tuple[int, int, int, int]:
    """Run the full matrix, returning aggregate reward totals + capability count."""
    total_g = total_gx = total_c = cap_count = 0
    for template_id in catalog.menu():
        for tier in RewardTier:
            for seed in _SEEDS:
                inst = _run_lifecycle(template_id, tier, seed)
                assert inst.state is QuestState.COMPLETED
                bundle = engine.grant_rewards(inst)

                cap = catalog.TIER_CAPS[tier]
                for f in _NUMERIC_FIELDS:
                    val = getattr(bundle, f)
                    assert val <= getattr(cap, f), (template_id, tier, f)
                    assert val <= getattr(catalog.GLOBAL_MAX, f), (template_id, tier, f)

                if bundle.capability is not None:
                    assert tier is RewardTier.III, (template_id, tier)
                    cap_count += 1
                else:
                    assert tier is not RewardTier.III

                total_g += bundle.global_xp
                total_gx += bundle.game_xp
                total_c += bundle.currency
    return total_g, total_gx, total_c, cap_count


def test_balance_within_caps_and_reproducible() -> None:
    first = _aggregate()
    second = _aggregate()
    # Reproducibility: identical aggregate totals on a re-run of the same seed set.
    assert first == second
    # Capability appears exactly once per tier-III lifecycle: 5 templates x 1000 seeds.
    assert first[3] == 5 * len(_SEEDS)
