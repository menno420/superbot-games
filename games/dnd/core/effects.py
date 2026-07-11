"""The pre-priced effect REGISTRY — code-owned outcomes the DM only references by id.

The bounded-menu law (Q-0040 / D-0007): the AI Dungeon Master never computes an
amount and never mutates state. A ``MenuOption`` carries an ``effect_id`` — an id
into this registry — and nothing more. Every effect here is a PRE-DEFINED,
deterministic transition; the only number-bearing outcome (a reward) is minted by
the shipped quest engine (:func:`games.exploration.quest.engine.grant_rewards`),
which returns exactly ``catalog.TIER_CAPS[tier]`` and is always ``<= GLOBAL_MAX``
component-wise. No effect reads DM input to size an outcome.

The three skeleton effects (design §6):

* ``rest_noop``     — narrate-only NO-OP; the safe clamp target (advances nothing).
* ``scout_narrate`` — narrate-only flavour beat; emits no event, mints nothing.
* ``escort_step``   — reuses the engine: offers/accepts the ``safe_passage`` ESCORT
  quest, applies the ``npc_reached`` event, and on ``COMPLETED`` mints the tier's
  capped reward via ``engine.grant_rewards`` (amounts CODE-OWNED, never DM-set).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from games.exploration.quest import engine
from games.exploration.quest.models import QuestState, RewardBundle, RewardTier
from games.exploration.quest.predicates import GameEvent
from games.exploration.quest.rng import DetRng


@dataclass(frozen=True)
class EffectOutcome:
    """The deterministic result of applying one effect — all fields code-owned.

    ``reward`` is ``None`` for a narrate-only effect; when present it is exactly the
    engine's tier-capped bundle (``<= GLOBAL_MAX``). ``event`` is the ``GameEvent``
    the effect emitted into the engine, if any. The DM never populates either.
    """

    effect_id: str
    reward: Optional[RewardBundle] = None
    event: Optional[GameEvent] = None


@dataclass(frozen=True)
class Effect:
    """A pre-priced, deterministic transition keyed by ``effect_id``.

    ``apply`` is a pure function of the process-stable ``seed`` (and ``player_id``):
    no wall-clock, no global RNG, no I/O. It never sees DM flavour or DM-chosen
    amounts — the resolver hands it only the seed the code derived.
    """

    effect_id: str
    _apply: Callable[[int, str], EffectOutcome]

    def apply(self, *, seed: int, player_id: str) -> EffectOutcome:
        """Deterministically resolve this effect for ``(seed, player_id)``."""
        return self._apply(seed, player_id)


def _rest_noop(seed: int, player_id: str) -> EffectOutcome:
    """The narrate-only NO-OP: the clamp target. Advances no quest, mints nothing."""
    # A DetRng is seeded to honour the determinism discipline even though a no-op
    # rolls nothing — the outcome is fixed regardless of the (deterministic) stream.
    DetRng(seed)
    return EffectOutcome(effect_id="rest_noop")


def _scout_narrate(seed: int, player_id: str) -> EffectOutcome:
    """A deterministic flavour beat: emits no event and mints no reward."""
    DetRng(seed)
    return EffectOutcome(effect_id="scout_narrate")


def _escort_step(seed: int, player_id: str) -> EffectOutcome:
    """Advance the ESCORT quest through the engine; mint the capped reward on COMPLETE.

    Reuses the shipped transition core verbatim: ``offer -> accept -> apply_event ->
    grant_rewards``. The ``safe_passage`` template's single ``npc_reached`` objective
    completes in one step, so a valid escort choice mints exactly
    ``catalog.TIER_CAPS[RewardTier.I]`` (``<= GLOBAL_MAX``). The amount is chosen by
    the engine, never by the DM.
    """
    tier = RewardTier.I
    instance = engine.offer("safe_passage", player_id, tier, seed)
    instance = engine.accept(instance)
    event = GameEvent(type="npc_reached", payload={"npc": "traveler", "dest": "waystation"})
    instance = engine.apply_event(instance, event)
    reward = (
        engine.grant_rewards(instance)
        if instance.state is QuestState.COMPLETED
        else None
    )
    return EffectOutcome(effect_id="escort_step", reward=reward, event=event)


# The pre-approved, pre-priced registry. A Scene may only reference these ids
# (enforced by ``Scene.__post_init__``). Adding an outcome is a code+sim change here,
# never a DM capability.
EFFECTS: dict[str, Effect] = {
    "rest_noop": Effect("rest_noop", _rest_noop),
    "scout_narrate": Effect("scout_narrate", _scout_narrate),
    "escort_step": Effect("escort_step", _escort_step),
}


def is_effect(effect_id: str) -> bool:
    """Return whether ``effect_id`` names a registered, pre-priced effect."""
    return effect_id in EFFECTS


__all__ = ["Effect", "EffectOutcome", "EFFECTS", "is_effect"]
