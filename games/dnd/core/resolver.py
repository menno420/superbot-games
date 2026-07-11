"""``resolve`` — the validate -> clamp -> apply core (the bounded-menu law, §4.4).

This is the single choke point that keeps the AI Dungeon Master's authority to "pick
one pre-approved button". In order:

1. **Cap** the surfaced menu by the code-computed width
   (:func:`games.exploration.quest.leverage.menu_width` — chat activity widens the
   option *count* only, 2..4, never amounts or outcomes).
2. **Validate** the DM's returned ``option_id`` is in the width-capped allowed set,
   BEFORE any resolution.
3. **Clamp** on ANY invalid input (off-menu / hallucinated id, malformed / non-
   ``DMChoice`` payload, ``None`` / timeout) to ``scene.default_option_id`` — a
   deterministic no-op. The DM can never move state off the menu.
4. Length-cap the DM's ``flavor`` to ``FLAVOR_CAP`` and treat it as DISPLAY-ONLY —
   it is NEVER parsed for effects.
5. Apply the selected option's PRE-DEFINED effect deterministically, seeded via the
   shipped ``derive_seed`` (process-stable, no wall-clock / no global RNG).

The worst case a compromised or hallucinating model can produce is a legal,
game-approved, capped outcome — or, off-menu, a deterministic no-op.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from games.exploration.quest import leverage
from games.exploration.quest.models import RewardBundle
from games.exploration.quest.predicates import GameEvent
from games.exploration.quest.rng import derive_seed

from .effects import EFFECTS, EffectOutcome
from .models import FLAVOR_CAP, MAX_MENU_SIZE, DMChoice, MenuOption, Scene

# A story-domain salt folded into every scene seed so the story stream is independent
# of any coincidentally-equal engine seed (mirrors fishing's ``_FISHING_SALT``).
_STORY_SALT = "dnd-story:v1"


@dataclass(frozen=True)
class Resolution:
    """What the resolver returns: the chosen id, the applied effect, display flavour.

    ``clamped`` is True whenever the DM's output was rejected and fell back to the
    scene default (the safety path). ``reward`` / ``event`` are code-owned (``None``
    for a narrate-only outcome); ``flavor`` is display-only, already length-capped.

    ``next_scene_id`` is the chosen option's PRE-DEFINED destination — pure DATA lifted
    straight off the option, NEVER supplied or computed by the DM. On the clamp path it
    is the DEFAULT option's own ``next_scene_id`` (deterministic), so an off-menu /
    hallucinated choice can never steer to an arbitrary scene: the worst case is the
    default's fixed transition (typically ``None`` = stay). ``None`` means stay/end.
    """

    scene_id: str
    chosen_option_id: str
    effect_id: str
    reward: Optional[RewardBundle]
    event: Optional[GameEvent]
    flavor: str
    clamped: bool
    next_scene_id: Optional[str]


def _sanitize_flavor(raw: object) -> str:
    """Coerce DM flavour to a length-capped, display-only string. Never parsed."""
    if not isinstance(raw, str):
        return ""
    # Collapse control characters that could break rendering; then hard length-cap.
    cleaned = "".join(ch for ch in raw if ch == " " or ch >= " ")
    return cleaned[:FLAVOR_CAP]


def _allowed_options(scene: Scene, xp: int) -> tuple[MenuOption, ...]:
    """Return the width-capped surfaced options (count widened by XP only)."""
    width = leverage.menu_width(xp)
    limit = min(len(scene.options), width, MAX_MENU_SIZE)
    return scene.options[:limit]


def resolve(
    scene: Scene,
    dm_choice: object,
    *,
    xp: int = 0,
    seed: object = 0,
    player_id: str = "player",
) -> Resolution:
    """Resolve one DM turn under the bounded-menu law. See module docstring for order.

    ``dm_choice`` is deliberately typed ``object``: a hallucinating model or a timeout
    may hand us anything (a non-``DMChoice``, ``None``, a dict, an off-menu id). All of
    those clamp to the scene's deterministic no-op default.
    """
    allowed = _allowed_options(scene, xp)
    allowed_ids = {o.id for o in allowed}

    # VALIDATE before resolving. Any invalid input -> clamp to the safe default no-op.
    if isinstance(dm_choice, DMChoice) and dm_choice.option_id in allowed_ids:
        chosen = scene.option(dm_choice.option_id)
        clamped = False
    else:
        chosen = scene.option(scene.default_option_id)  # always on the menu (§4.1)
        clamped = True

    # Flavour is DISPLAY-ONLY: length-capped, never inspected for mechanics.
    flavor = _sanitize_flavor(getattr(dm_choice, "flavor", ""))

    # Resolve the PRE-DEFINED effect deterministically — code owns the outcome.
    scene_seed = derive_seed(_STORY_SALT, seed, scene.scene_id)
    outcome: EffectOutcome = EFFECTS[chosen.effect_id].apply(
        seed=scene_seed, player_id=player_id
    )

    return Resolution(
        scene_id=scene.scene_id,
        chosen_option_id=chosen.id,
        effect_id=outcome.effect_id,
        reward=outcome.reward,
        event=outcome.event,
        flavor=flavor,
        clamped=clamped,
        # The destination is DATA on the CHOSEN option — on the clamp path ``chosen`` is
        # the default option, so this is the default's own fixed transition. The DM never
        # supplies it; it can only ever be one of the scene's pre-defined edges.
        next_scene_id=chosen.next_scene_id,
    )


__all__ = ["Resolution", "resolve"]
