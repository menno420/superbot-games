"""D&D WORKFLOW audited seam — the write boundary over the bounded-menu resolver.

The audited **write boundary** for the D&D story game. Below it sits the shipped
PURE CORE (``games/dnd/core/`` — the bounded-menu ``resolve``, the pre-priced
``EFFECTS`` registry, the ``models`` schema) plus its 3-scene data catalog
(``games/dnd/data/scenes.py``); above it (a later rung) a HOST adapter will bind
this seam onto the superbot-next plugin contract. This module is the middle rung:
the one state-changing D&D op is orchestrated here in one place —

    read session state  ->  build the DM's one-id choice  ->  call the PURE CORE
    (``resolve``, which already CLAMPS any off-menu id to the deterministic safe
    default)  ->  fold the code-owned reward into the running totals  ->  advance
    the scene along the chosen option's PRE-DEFINED edge  ->  build an audit
    record  ->  ``sink.record(...)``  ->  return a frozen Result

Design provenance mirrors the fishing seam (``services/fishing_workflow.py``) —
itself mirrored from mining (``docs/design/mining-workflow-seam.md`` §5):

* **D1** — the seam's audit record is the oracle's 11-field structural
  ``audit.action_recorded`` schema (:class:`AuditRecord`), adopted VERBATIM. It
  is GAME-NEUTRAL and lives in ``services/audit.py`` so mining, fishing, and now
  D&D reuse it without welding three games together — this seam
  ``from services.audit import AuditRecord, Sink, InMemorySink`` and NEVER imports
  another game's ``services/*_workflow.py``.
* **D2 (D&D's honest divergence)** — the seam audits **every** ``choose`` routed
  through it, including an off-menu clamp to the safe default. Unlike fishing
  (whose too-tired no-op cast records NOTHING), the audited EVENT here is the DM's
  bounded DECISION itself — an option was picked and RESOLVED (a transition
  and/or a minted reward) even when the input clamps to the deterministic no-op.
  Logging the decision (including a hallucinated / off-menu one that clamped) is
  the point of the bounded-menu law, so a ``choose`` ALWAYS records exactly one.

The bounded-menu law lives entirely in the pure resolver
(:func:`games.dnd.core.resolver.resolve`): it caps the surfaced menu by
``leverage.menu_width`` and clamps any invalid / off-menu / hallucinated id to the
scene's deterministic ``default_option_id``. This seam RELIES on that clamp and
never re-implements it. The HUMAN (or, later, a model) occupies the DM's exact
seat: pick ONE option id from the bounded menu — nothing more.

Balance discipline: every reward / number / noun comes VERBATIM from the pure
core / its data tables (the reward is exactly the engine's tier-capped
``RewardBundle``; the narration is ``data/scenes.py`` copy). Only *structural*
audit fields — the mutation id, timestamp, ids, ``scope`` and ``target`` strings —
are constructed (they carry no balance meaning). This module is stdlib-only apart
from ``games.dnd.*`` (+ the shared pure quest primitives the D&D core itself
reuses) so CI stays hermetic.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from services.audit import AuditRecord, InMemorySink, Sink

from games.dnd.core.models import MAX_MENU_SIZE, DMChoice, MenuOption, Scene
from games.dnd.core.resolver import Resolution, resolve
from games.dnd.data.scenes import get_scene, text_for
from games.exploration.quest import leverage
from games.exploration.quest.models import RewardBundle

# --- structural mutation-type / target tokens ------------------------------
# D&D has NO free-standing economy reason tokens at the seam (the reward is
# minted inside the pure effect, tier-capped by the engine), so the seam
# constructs a stable STRUCTURAL verb for its one action — ``dnd:choose`` (the
# ``dnd:*`` namespace, mirroring fishing's ``fishing:*`` / mining's ``mining:*``
# structural verbs). These carry no balance meaning.
MUTATION_CHOOSE = "dnd:choose"

#: The seam's actor-type token for a human player (the ``actor_type`` field of
#: :class:`AuditRecord`; the oracle's capability-resolver actor-type slot). The
#: human occupies the DM's one-id seat.
ACTOR_PLAYER = "player"

#: The walking-skeleton start scene — the ESCORT ``safe_passage`` fork
#: (``games/dnd/data/scenes.py``). A fresh session begins here.
START_SCENE = "waystation_road"


# ---------------------------------------------------------------------------
# The session state the seam mutates
# ---------------------------------------------------------------------------
@dataclass
class DnDState:
    """A full mutable D&D story session — everything the seam reads and writes.

    Field notes:

    * ``scene_id`` — the scene the next :func:`choose` resolves against; advanced
      along the chosen option's PRE-DEFINED ``next_scene_id`` after each choose
      (``None`` ⇒ the beat concludes / stays, so ``scene_id`` is left unchanged).
    * ``global_xp`` / ``game_xp`` / ``currency`` — the running reward totals
      folded from each minted :class:`~games.exploration.quest.models.RewardBundle`
      (all CODE-OWNED and tier-capped; the DM never sizes them). Start at 0.
    * ``capability`` — the most recent prestige capability a reward granted, if
      any (``None`` in the skeleton — the escort tier mints no capability).
    * ``player_id`` — the player the pure effect seeds its deterministic reward
      for (``derive_seed`` folds it in).
    * ``seed`` — the story-world seed; the resolver derives its process-stable
      per-scene stream from it (``derive_seed(_STORY_SALT, seed, scene_id)``), so
      a fixed seed reproduces every resolution byte-for-byte.
    * ``xp`` — the DM's menu-WIDTH lever (chat-activity XP, read by
      ``leverage.menu_width`` to widen the surfaced option COUNT 2..4 — NEVER
      amounts). Distinct from the reward ``game_xp`` above; the skeleton grows no
      chat activity, so it stays at its floor (width 2).
    * ``bundle_minted`` — the MINT-AT-MOST-ONCE guard (sim-lab VERDICT 044,
      relayed as ORDER 007 in ``control/inbox.md``): the escort ``safe_passage``
      bundle mints at most ONCE per session. The scene catalog wires
      ``escort_step`` to two options on one arc (and the ended beat's stay-loop
      can re-fire it without bound), so an unguarded session re-mints legally —
      the one-shot flag closes both the 2× arc and the unbounded stay-loop
      without inventing any number.
    """

    scene_id: str = START_SCENE
    seed: int = 0
    player_id: str = "player"
    xp: int = 0
    global_xp: int = 0
    game_xp: int = 0
    currency: int = 0
    capability: Optional[str] = None
    bundle_minted: bool = False


# ---------------------------------------------------------------------------
# Result dataclass — the seam's frozen return contract for a choose
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class DnDResult:
    """Outcome of a :func:`choose` op — always ``ok`` (a choose always resolves).

    ``resolution`` is the pure :class:`~games.dnd.core.resolver.Resolution`
    verbatim (carrying ``clamped`` = whether the input was off-menu and fell back
    to the safe default). ``prev_scene`` / ``next_scene`` are the scene chosen
    FROM and the pre-defined scene moved TO (``next_scene`` is ``None`` when the
    beat concludes / stays). ``reward`` is the code-owned bundle minted this
    choose (``None`` for a narrate-only outcome, and ``None`` when the
    MINT-AT-MOST-ONCE guard suppressed a repeat mint — VERDICT 044). ``ended``
    is ``True`` when the
    chosen option has no successor scene. ``message`` is the option's
    player-visible copy, VERBATIM from ``data/scenes.py``.
    """

    ok: bool
    resolution: Resolution
    prev_scene: str
    next_scene: Optional[str]
    reward: Optional[RewardBundle]
    ended: bool
    message: str
    record: AuditRecord


# ---------------------------------------------------------------------------
# Menu surfacing — the bounded set the resolver ACCEPTS (display == acceptance)
# ---------------------------------------------------------------------------
def surfaced_options(scene: Scene, *, xp: int = 0) -> tuple[MenuOption, ...]:
    """Return the width-capped options the resolver would ACCEPT for ``scene``.

    Mirrors the resolver's private ``_allowed_options`` using the SAME public
    primitive it does (:func:`games.exploration.quest.leverage.menu_width`), so a
    CLI can show exactly the menu the resolver accepts — anything beyond it clamps
    to the safe default. Chat-activity ``xp`` widens the option COUNT only (2..4),
    never amounts or outcomes. This is a DISPLAY helper: the clamp law itself
    stays the resolver's sole authority.
    """
    width = leverage.menu_width(xp)
    limit = min(len(scene.options), width, MAX_MENU_SIZE)
    return scene.options[:limit]


# ---------------------------------------------------------------------------
# Injectables — a simple clock + id factory kept deterministic for tests
# ---------------------------------------------------------------------------
def _resolve_now(now: datetime | None) -> datetime:
    """The op's timestamp — the injected *now* or ``datetime.now(timezone.utc)``."""
    return now if now is not None else datetime.now(timezone.utc)


def _resolve_id(factory: Callable[[], str] | None) -> str:
    """A fresh mutation id — from the injected *factory* or ``uuid4().hex``."""
    return factory() if factory is not None else uuid4().hex


def _reward_summary(state: DnDState) -> str:
    """A compact ``g<gx>/x<game_xp>/c<currency>`` render of the running totals."""
    return f"g{state.global_xp}/x{state.game_xp}/c{state.currency}"


def _fold_reward(state: DnDState, reward: RewardBundle | None) -> None:
    """Fold a minted :class:`RewardBundle` into the running totals (code-owned).

    Every amount is taken VERBATIM from the engine's tier-capped bundle — the seam
    only sums them, it never sizes or re-derives a reward. A ``None`` reward (a
    narrate-only effect) folds nothing.
    """
    if reward is None:
        return
    state.global_xp += reward.global_xp
    state.game_xp += reward.game_xp
    state.currency += reward.currency
    if reward.capability is not None:
        state.capability = reward.capability


# ---------------------------------------------------------------------------
# The one action — choose
# ---------------------------------------------------------------------------
def choose(
    state: DnDState,
    option_id: object,
    *,
    sink: Sink,
    flavor: str = "",
    guild_id: int | None = None,
    actor_id: int | None = None,
    actor_type: str = ACTOR_PLAYER,
    now: datetime | None = None,
    mutation_id_factory: Callable[[], str] | None = None,
) -> DnDResult:
    """Resolve one DM turn: the pure core decides, the seam folds the reward + audits.

    Wires :func:`games.dnd.core.resolver.resolve` (which caps the menu and CLAMPS
    any off-menu / hallucinated ``option_id`` to the scene's deterministic
    ``default_option_id`` — RELIED on, never re-implemented) → fold the code-owned
    reward (if any) into the running totals → advance ``state.scene_id`` along the
    chosen option's PRE-DEFINED ``next_scene_id`` (``None`` ⇒ the beat concludes /
    stays, so the scene is left unchanged) → build ONE :class:`AuditRecord` and
    ``sink.record(...)`` it as the LAST commit step → return a frozen
    :class:`DnDResult`.

    ``option_id`` is deliberately typed ``object``: a hallucinating model or a
    fat-fingered human may hand us anything (a bad id, ``None``). The resolver
    clamps all of those to the safe default, so a ``choose`` NEVER raises on input
    and ALWAYS resolves. It also ALWAYS records exactly one audit row — the
    audited event is the DM's bounded DECISION (including one that clamped), not a
    state delta (D2, this seam's honest divergence from fishing's no-op-skips-audit
    rule). Determinism: with a fixed ``state.seed`` + ``player_id`` and an injected
    ``now`` / ``mutation_id_factory`` a choose reproduces its resolution AND its
    record byte-for-byte.
    """
    prev_scene = state.scene_id
    scene = get_scene(prev_scene)

    # Coerce the DM's payload to a DMChoice. A non-string id (None, etc.) becomes
    # a DMChoice the resolver will simply find off-menu and clamp — we never guess.
    dm_choice = DMChoice(option_id=option_id, flavor=flavor) if isinstance(option_id, str) else object()

    resolution = resolve(
        scene,
        dm_choice,
        xp=state.xp,
        seed=state.seed,
        player_id=state.player_id,
    )

    # MINT-AT-MOST-ONCE guard (VERDICT 044 / ORDER 007): the escort bundle mints
    # at most once per session — a repeat resolution's reward is suppressed (the
    # choose still resolves + records as a narrate-only transition). The engine's
    # tier-capped bundle itself stays VERBATIM; the guard invents no number.
    reward = resolution.reward
    if reward is not None:
        if state.bundle_minted:
            reward = None
        else:
            state.bundle_minted = True

    # Fold the code-owned reward BEFORE building the record, so the record's
    # before/after reward summary brackets this choose's mint honestly.
    reward_before = _reward_summary(state)
    _fold_reward(state, reward)
    reward_after = _reward_summary(state)

    next_scene = resolution.next_scene_id
    ended = next_scene is None
    if next_scene is not None:
        state.scene_id = next_scene  # advance along the option's PRE-DEFINED edge

    now_dt = _resolve_now(now)
    if reward is not None:
        # A minted reward: the primary mutation is the reward grant (mirrors
        # fishing's bite recording the haul, not the energy side effect).
        target = f"reward:{prev_scene}"
        prev_value: str | None = reward_before
        new_value: str | None = reward_after
    else:
        # A narrate-only choose (or a clamp to the safe rest default): the audited
        # mutation is the scene transition. ``new_value`` is None when the beat
        # concludes / stays (no successor scene) — the field's honest "no next".
        target = f"scene:{prev_scene}"
        prev_value = prev_scene
        new_value = next_scene

    record = AuditRecord(
        mutation_id=_resolve_id(mutation_id_factory),
        subsystem="dnd",
        mutation_type=MUTATION_CHOOSE,
        target=target,
        scope="global",
        guild_id=guild_id,
        prev_value=prev_value,
        new_value=new_value,
        actor_id=actor_id,
        actor_type=actor_type,
        occurred_at=now_dt,
    )
    sink.record(record)

    chosen = scene.option(resolution.chosen_option_id)

    return DnDResult(
        ok=True,
        resolution=resolution,
        prev_scene=prev_scene,
        next_scene=next_scene,
        reward=reward,
        ended=ended,
        message=text_for(chosen.text_key),
        record=record,
    )


__all__ = [
    "AuditRecord",
    "Sink",
    "InMemorySink",
    "DnDState",
    "DnDResult",
    "ACTOR_PLAYER",
    "MUTATION_CHOOSE",
    "START_SCENE",
    "surfaced_options",
    "choose",
]
