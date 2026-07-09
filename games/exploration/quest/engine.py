"""Pure deterministic quest engine — the transition core.

Every function is pure: no wall-clock, no global RNG, no I/O. State is immutable
(frozen dataclasses); transitions return a NEW ``QuestInstance``. This is the
deterministic core that owns every outcome the AI later narrates (Q-0040).
"""

from __future__ import annotations

from . import catalog, predicates
from .models import (
    ObjectiveProgress,
    QuestInstance,
    QuestState,
    QuestStateError,
    RewardBundle,
    RewardTier,
)
from .predicates import GameEvent
from .rng import derive_seed


def _instance_id(seed: int, template_id: str, player_id: str) -> str:
    """Deterministic instance id — a stable function of seed + template + player."""
    return f"q-{template_id}-{player_id}-{seed & ((1 << 32) - 1):08x}"


def offer(
    template_id: str,
    player_id: str,
    tier: RewardTier,
    world_seed: object,
) -> QuestInstance:
    """Deterministically offer a quest instance in the OFFERED state.

    The seed and instance id are derived from ``(world_seed, player_id,
    template_id, tier)`` so identical inputs yield a byte-identical instance.
    """
    template = catalog.get(template_id)
    seed = derive_seed(world_seed, player_id, template_id, tier.value)
    progress = tuple(
        ObjectiveProgress(key=obj.key, current=0, required=obj.required)
        for obj in template.objectives
    )
    return QuestInstance(
        instance_id=_instance_id(seed, template_id, player_id),
        template_id=template_id,
        kind=template.kind,
        player_id=player_id,
        seed=seed,
        tier=tier,
        state=QuestState.OFFERED,
        progress=progress,
        step=0,
    )


def accept(instance: QuestInstance) -> QuestInstance:
    """OFFERED -> ACTIVE. Raises ``QuestStateError`` from any other state."""
    if instance.state is not QuestState.OFFERED:
        raise QuestStateError(
            f"accept requires OFFERED, got {instance.state.value}"
        )
    from dataclasses import replace

    return replace(instance, state=QuestState.ACTIVE)


def apply_event(instance: QuestInstance, event: GameEvent) -> QuestInstance:
    """Advance objectives that match ``event``; complete when all are done.

    Ignored unless the instance is ACTIVE (returns it unchanged). For each
    not-yet-done objective, the predicate increment is added and clamped to
    ``required``. ``step`` bumps on every applied event. When all objectives are
    done the state becomes COMPLETED. Returns a NEW instance; never mutates.
    """
    if instance.state is not QuestState.ACTIVE:
        return instance

    template = catalog.get(instance.template_id)
    objectives_by_key = {obj.key: obj for obj in template.objectives}

    new_progress: list[ObjectiveProgress] = []
    for prog in instance.progress:
        if prog.done:
            new_progress.append(prog)
            continue
        objective = objectives_by_key[prog.key]
        increment = predicates.evaluate(
            objective.predicate, event, objective.params_dict()
        )
        if increment <= 0:
            new_progress.append(prog)
            continue
        updated = min(prog.current + increment, prog.required)
        new_progress.append(
            ObjectiveProgress(key=prog.key, current=updated, required=prog.required)
        )

    all_done = all(p.done for p in new_progress)
    new_state = QuestState.COMPLETED if all_done else instance.state

    from dataclasses import replace

    return replace(
        instance,
        progress=tuple(new_progress),
        step=instance.step + 1,
        state=new_state,
    )


def _terminal_transition(
    instance: QuestInstance, target: QuestState
) -> QuestInstance:
    """Guarded transition from OFFERED/ACTIVE to a terminal non-completed state."""
    if instance.state not in (QuestState.OFFERED, QuestState.ACTIVE):
        raise QuestStateError(
            f"cannot move to {target.value} from {instance.state.value}"
        )
    from dataclasses import replace

    return replace(instance, state=target)


def abandon(instance: QuestInstance) -> QuestInstance:
    """Player abandons the quest -> FAILED."""
    return _terminal_transition(instance, QuestState.FAILED)


def fail(instance: QuestInstance) -> QuestInstance:
    """Quest fails (objective made impossible) -> FAILED."""
    return _terminal_transition(instance, QuestState.FAILED)


def expire(instance: QuestInstance) -> QuestInstance:
    """Quest offer/active window lapses -> EXPIRED."""
    return _terminal_transition(instance, QuestState.EXPIRED)


def grant_rewards(instance: QuestInstance) -> RewardBundle:
    """Return the tier's capped reward bundle for a COMPLETED quest.

    Amounts are CODE-OWNED and fixed at the tier cap — the AI never sets them
    (Q-0040). The prestige capability is granted ONLY at tier III (play-only, never
    purchasable with currency — no pay-to-win, Q-0039 / Q-0190); tiers I and II
    grant ``capability=None``. The returned bundle never exceeds ``TIER_CAPS`` or
    ``GLOBAL_MAX``.
    """
    if instance.state is not QuestState.COMPLETED:
        raise QuestStateError(
            f"grant_rewards requires COMPLETED, got {instance.state.value}"
        )
    cap = catalog.TIER_CAPS[instance.tier]
    capability = None
    if instance.tier is RewardTier.III:
        template = catalog.get(instance.template_id)
        capability = template.prestige_capability
    return RewardBundle(
        global_xp=cap.global_xp,
        game_xp=cap.game_xp,
        currency=cap.currency,
        capability=capability,
    )
