"""Exploration WORKFLOW audited seam — the write boundary over the quest engine.

The audited **write boundary** for the exploration game. Below it sit three
shipped, independently green PURE CORES —

* the deterministic **quest engine** (``games/exploration/quest/`` — the
  bounded-menu ``catalog``, the ``engine`` lifecycle ``offer → accept →
  apply_event → grant_rewards``, the frozen ``models``, the ``predicates``),
* the **survival** energy axis (``games/exploration/survival/`` — ``difficulty``
  ``TUNABLES`` scaling the *shipped* mining energy bar per D-0004),
* the shared **encounter resolver** (``games/shared/encounter/`` — the
  dependency-free ``ReferenceEncounterResolver``) —

but nothing DROVE them: they were three green islands with no seam, driver, or
hub entry. This module is the middle rung that wires them into one audited
lifecycle. Above it (a later rung) a HOST adapter will bind this seam onto the
superbot-next plugin contract.

Each state-changing op is orchestrated here in one place —

    read session state  ->  call the PURE CORE (``engine.offer`` / ``engine.accept``
    / ``engine.apply_event`` / ``engine.grant_rewards``) to decide  ->  mutate the
    state (advance the quest instance, spend survival energy, fold the capped
    reward)  ->  build ONE audit record  ->  ``sink.record(...)``  ->  return a
    frozen Result

Design provenance mirrors the just-landed D&D seam (``services/dnd_workflow.py``)
and, before it, fishing (``services/fishing_workflow.py``) / mining
(``docs/design/mining-workflow-seam.md`` §5):

* **D1** — the seam's audit record is the oracle's 11-field structural
  ``audit.action_recorded`` schema (:class:`AuditRecord`), adopted VERBATIM. It is
  GAME-NEUTRAL and lives in ``services/audit.py`` so mining, fishing, D&D, and now
  exploration reuse it without welding games together — this seam
  ``from services.audit import AuditRecord, Sink, InMemorySink`` and NEVER imports
  another game's ``services/*_workflow.py``.
* **D2 (exploration's honest semantics)** — the seam audits **every**
  state-changing op (a quest offered, accepted, an action that advanced an
  objective + spent energy, a reward banked) with exactly ONE record. An op that
  changes NOTHING records NOTHING and returns ``ok=False``: an ``offer`` of an
  unknown template, an ``accept`` with no offered quest, an ``apply_action`` that
  is off the bounded menu / too-tired (survival energy gate) / on an
  already-complete quest, or a ``grant`` with no COMPLETED quest. This mirrors
  fishing's no-op-skips-audit rule (and diverges from D&D, which audits even a
  clamped decision — exploration has no clamp: an off-menu action is simply a
  no-op, never a silently-substituted one).

The bounded-menu law lives entirely in the pure engine + catalog: the HUMAN picks
a ``(template_id, RewardTier)`` from :func:`catalog.menu` (the fixed 5-template
list) and, once a quest is active, a bounded ACTION from that quest's own pending
objectives (each maps 1:1 to the objective-advancing ``GameEvent`` the engine
already defines). There is NO AI-DM, NO generative narration, NO chat-activity /
message-XP faucet wired here — the ``leverage.menu_width`` lever and the
``CHAT_ACTIVITY`` encounter trigger are deliberately left in the owner queue.

Balance discipline: every reward / cap / number / noun comes VERBATIM from the
engine / catalog / survival modules (the reward is exactly ``engine.grant_rewards``
tier-capped ``RewardBundle``; the energy cap/cost are the difficulty's
``SurvivalTunables``; the encounter kind/intensity are the resolver's). Only
*structural* audit fields — the mutation id, timestamp, ids, ``scope`` and
``target`` strings — are constructed (they carry no balance meaning). This module
is stdlib-only apart from ``games.exploration.*`` / ``games.shared.*`` (+ the
shared mining energy constants the survival axis itself reuses) so CI stays
hermetic.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from services.audit import AuditRecord, InMemorySink, Sink

from games.exploration.quest import catalog
from games.exploration.quest import engine as quest_engine
from games.exploration.quest.models import (
    QuestInstance,
    QuestState,
    RewardBundle,
    RewardTier,
)
from games.exploration.quest.predicates import GameEvent
from games.exploration.survival.difficulty import TUNABLES, Difficulty, SurvivalTunables
from games.shared.encounter.interface import (
    EncounterOutcome,
    EncounterRequest,
    EncounterResolver,
    EncounterTrigger,
)
from games.shared.encounter.reference import ReferenceEncounterResolver

# --- structural mutation-type / target tokens ------------------------------
# Exploration has NO free-standing economy reason tokens at the seam (the reward
# is minted inside the pure engine, tier-capped by ``grant_rewards``), so the seam
# constructs stable STRUCTURAL verbs for its four ops — the ``exploration:*``
# namespace, mirroring D&D's ``dnd:*`` / fishing's ``fishing:*`` structural verbs.
# These carry no balance meaning.
MUTATION_OFFER = "exploration:offer"
MUTATION_ACCEPT = "exploration:accept"
MUTATION_ACTION = "exploration:action"
MUTATION_GRANT = "exploration:grant"

#: The seam's actor-type token for a human player (the ``actor_type`` field of
#: :class:`AuditRecord`; the oracle's capability-resolver actor-type slot). The
#: human occupies the quest-picker's seat — nothing generative.
ACTOR_PLAYER = "player"

#: The shared reference encounter resolver (dependency-free, deterministic). The
#: seam resolves an EXPLORE_ACTION encounter on each bounded action; the
#: CHAT_ACTIVITY trigger is deliberately NOT wired (owner/product queue).
_DEFAULT_RESOLVER: EncounterResolver = ReferenceEncounterResolver()


# ---------------------------------------------------------------------------
# The accumulated reward ledger — code-owned, folded from capped bundles
# ---------------------------------------------------------------------------
@dataclass
class RewardLedger:
    """Running totals folded from each COMPLETED quest's tier-capped bundle.

    Every amount is taken VERBATIM from ``engine.grant_rewards`` — the ledger only
    sums them, it never sizes or re-derives a reward. ``capabilities`` accrues the
    prestige unlocks granted at tier III (play-only, never bought — Q-0039/Q-0190);
    ``quests_completed`` counts banked quests.
    """

    global_xp: int = 0
    game_xp: int = 0
    currency: int = 0
    capabilities: tuple[str, ...] = ()
    quests_completed: int = 0

    def summary(self) -> str:
        """A compact ``g<gx>/x<game_xp>/c<currency>`` render of the totals."""
        return f"g{self.global_xp}/x{self.game_xp}/c{self.currency}"

    def fold(self, bundle: RewardBundle) -> None:
        """Fold a minted, tier-capped :class:`RewardBundle` into the totals."""
        self.global_xp += bundle.global_xp
        self.game_xp += bundle.game_xp
        self.currency += bundle.currency
        if bundle.capability is not None and bundle.capability not in self.capabilities:
            self.capabilities = (*self.capabilities, bundle.capability)
        self.quests_completed += 1


# ---------------------------------------------------------------------------
# The session state the seam mutates
# ---------------------------------------------------------------------------
@dataclass
class ExplorationState:
    """A full mutable exploration session — everything the seam reads and writes.

    Field notes:

    * ``player_id`` — the player the engine seeds its deterministic instance +
      reward for (``engine.offer`` folds it into ``derive_seed``).
    * ``world_seed`` — the exploration world seed; the engine derives every
      instance id / reward stream and the encounter resolver derives every
      outcome from it, so a fixed seed reproduces a session byte-for-byte.
    * ``difficulty`` — the survival Energy-axis tuning (``Difficulty.EASY`` ≡ the
      shipped mining bar, D-0004). Picks the :class:`SurvivalTunables` the energy
      gate reads.
    * ``energy`` — remaining survival energy. Starts at the difficulty's
      ``max_energy`` (VERBATIM from ``TUNABLES``); each bounded action debits the
      difficulty's ``cost``. An action while ``energy < cost`` is a too-tired
      no-op (records nothing) — the survive-the-wild gate.
    * ``quest`` — the single current :class:`QuestInstance`, moving OFFERED →
      ACTIVE → COMPLETED across the seam ops (``None`` between quests). The
      engine returns a NEW instance per transition; the seam replaces this field.
    * ``ledger`` — the accumulated, code-owned :class:`RewardLedger` (folded from
      each banked bundle; never sized here).
    * ``last_encounter`` — the most recent resolved :class:`EncounterOutcome`
      (``None`` until the first bounded action rolls one).
    """

    player_id: str = "player"
    world_seed: int = 0
    difficulty: Difficulty = Difficulty.EASY
    energy: Optional[int] = None
    quest: Optional[QuestInstance] = None
    ledger: RewardLedger = field(default_factory=RewardLedger)
    last_encounter: Optional[EncounterOutcome] = None

    def __post_init__(self) -> None:
        # Seed energy from the difficulty's shipped bar cap (no invented number).
        if self.energy is None:
            self.energy = self.tunables.max_energy

    @property
    def tunables(self) -> SurvivalTunables:
        """The survival energy tuning for the current difficulty (VERBATIM)."""
        return TUNABLES[self.difficulty]


# ---------------------------------------------------------------------------
# Result dataclass — the seam's frozen return contract for every op
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ExplorationResult:
    """Outcome of one seam op.

    ``ok`` is ``True`` when the op changed state and emitted exactly one audit
    record; ``False`` for an honest no-op (nothing changed, nothing recorded).
    ``action`` names which op ran (``"offer"`` / ``"accept"`` / ``"action"`` /
    ``"grant"``). ``quest`` is the resulting instance (VERBATIM from the engine);
    ``encounter`` is the deterministic outcome an action rolled; ``reward`` is the
    tier-capped bundle a grant banked; ``completed`` flags a quest that just
    reached COMPLETED; ``energy_after`` is the survival energy left; ``record`` is
    the emitted :class:`AuditRecord` (``None`` on a no-op).
    """

    ok: bool
    action: str
    message: str
    quest: Optional[QuestInstance] = None
    encounter: Optional[EncounterOutcome] = None
    reward: Optional[RewardBundle] = None
    completed: bool = False
    energy_after: int = 0
    record: Optional[AuditRecord] = None


# ---------------------------------------------------------------------------
# Injectables — a simple clock + id factory kept deterministic for tests
# ---------------------------------------------------------------------------
def _resolve_now(now: datetime | None) -> datetime:
    """The op's timestamp — the injected *now* or ``datetime.now(timezone.utc)``."""
    return now if now is not None else datetime.now(timezone.utc)


def _resolve_id(factory: Callable[[], str] | None) -> str:
    """A fresh mutation id — from the injected *factory* or ``uuid4().hex``."""
    return factory() if factory is not None else uuid4().hex


def _make_record(
    *,
    mutation_type: str,
    target: str,
    prev_value: str | None,
    new_value: str | None,
    now: datetime,
    mutation_id: str,
    guild_id: int | None,
    actor_id: int | None,
    actor_type: str,
) -> AuditRecord:
    """Build one :class:`AuditRecord` with the seam's fixed structural defaults."""
    return AuditRecord(
        mutation_id=mutation_id,
        subsystem="exploration",
        mutation_type=mutation_type,
        target=target,
        scope="global",
        guild_id=guild_id,
        prev_value=prev_value,
        new_value=new_value,
        actor_id=actor_id,
        actor_type=actor_type,
        occurred_at=now,
    )


# ---------------------------------------------------------------------------
# Bounded-menu helpers — the fixed choices the human picks from (never generative)
# ---------------------------------------------------------------------------
def quest_menu() -> tuple[str, ...]:
    """The bounded quest menu — ``catalog.menu()`` VERBATIM (the fixed 5 ids)."""
    return catalog.menu()


def pending_actions(instance: QuestInstance | None) -> tuple[str, ...]:
    """The bounded ACTION menu for an ACTIVE quest — its not-yet-done objectives.

    Each returned key is one of the active quest template's objective keys, taken
    VERBATIM from the catalog. Each maps 1:1 to the objective-advancing
    ``GameEvent`` :func:`apply_action` fires. Empty unless a quest is ACTIVE with
    unfinished objectives, so the menu is always bounded and never generative.
    """
    if instance is None or instance.state is not QuestState.ACTIVE:
        return ()
    return tuple(p.key for p in instance.progress if not p.done)


def _objective_event(instance: QuestInstance, action: str) -> GameEvent | None:
    """Build the objective-advancing :class:`GameEvent` for a bounded *action*.

    Reads the template objective whose ``key == action`` and constructs the event
    the engine's predicate already matches: ``type`` is the objective's predicate
    alias (which IS the event type for the v1 catalog's five predicates) and the
    payload is that objective's ``match`` params — both VERBATIM from the catalog.
    Returns ``None`` when *action* is not one of the template's objective keys.
    """
    template = catalog.get(instance.template_id)
    for objective in template.objectives:
        if objective.key == action:
            params = objective.params_dict()
            match = params.get("match")
            payload: Mapping[str, object] = dict(match) if isinstance(match, Mapping) else {}
            return GameEvent(type=objective.predicate, payload=payload)
    return None


def _progress_render(instance: QuestInstance, key: str) -> str:
    """A ``current/required`` render of one objective's progress (for the record)."""
    for prog in instance.progress:
        if prog.key == key:
            return f"{prog.current}/{prog.required}"
    return "?"


# ---------------------------------------------------------------------------
# Op 1 — offer
# ---------------------------------------------------------------------------
def offer(
    state: ExplorationState,
    template_id: str,
    tier: RewardTier = RewardTier.I,
    *,
    sink: Sink,
    guild_id: int | None = None,
    actor_id: int | None = None,
    actor_type: str = ACTOR_PLAYER,
    now: datetime | None = None,
    mutation_id_factory: Callable[[], str] | None = None,
) -> ExplorationResult:
    """Offer a bounded quest: the engine mints the OFFERED instance, the seam audits.

    Wires :func:`games.exploration.quest.engine.offer` for the human-picked
    ``(template_id, tier)`` → set ``state.quest`` to the OFFERED instance → emit
    ONE :class:`AuditRecord` and ``sink.record(...)`` it → return a frozen
    :class:`ExplorationResult`. An UNKNOWN ``template_id`` (off the bounded
    ``catalog.menu()``) is an honest no-op: nothing changes, nothing records,
    ``ok=False``.
    """
    if template_id not in catalog.menu():
        return ExplorationResult(
            ok=False,
            action="offer",
            message=f"unknown quest {template_id!r} — pick one of {', '.join(catalog.menu())}",
            quest=state.quest,
            energy_after=state.energy or 0,
        )

    prev_instance = state.quest
    instance = quest_engine.offer(template_id, state.player_id, tier, state.world_seed)
    state.quest = instance

    record = _make_record(
        mutation_type=MUTATION_OFFER,
        target=f"quest:{template_id}",
        prev_value=prev_instance.instance_id if prev_instance is not None else None,
        new_value=instance.instance_id,
        now=_resolve_now(now),
        mutation_id=_resolve_id(mutation_id_factory),
        guild_id=guild_id,
        actor_id=actor_id,
        actor_type=actor_type,
    )
    sink.record(record)

    template = catalog.get(template_id)
    return ExplorationResult(
        ok=True,
        action="offer",
        message=f"Offered {template.title} ({template.kind.value}, tier {tier.value}): {template.summary}",
        quest=instance,
        energy_after=state.energy or 0,
        record=record,
    )


# ---------------------------------------------------------------------------
# Op 2 — accept
# ---------------------------------------------------------------------------
def accept(
    state: ExplorationState,
    *,
    sink: Sink,
    guild_id: int | None = None,
    actor_id: int | None = None,
    actor_type: str = ACTOR_PLAYER,
    now: datetime | None = None,
    mutation_id_factory: Callable[[], str] | None = None,
) -> ExplorationResult:
    """Accept the offered quest: OFFERED → ACTIVE via the engine, then audit.

    Wires :func:`games.exploration.quest.engine.accept` → replace ``state.quest``
    with the ACTIVE instance → emit ONE audit record. With NO offered quest (none
    offered, or already active/completed) this is an honest no-op: nothing
    changes, nothing records, ``ok=False`` (the engine's own state guard is never
    tripped — the seam checks first).
    """
    instance = state.quest
    if instance is None or instance.state is not QuestState.OFFERED:
        return ExplorationResult(
            ok=False,
            action="accept",
            message="no offered quest to accept — offer one first",
            quest=instance,
            energy_after=state.energy or 0,
        )

    accepted = quest_engine.accept(instance)
    state.quest = accepted

    record = _make_record(
        mutation_type=MUTATION_ACCEPT,
        target=f"quest:{accepted.instance_id}",
        prev_value=QuestState.OFFERED.value,
        new_value=QuestState.ACTIVE.value,
        now=_resolve_now(now),
        mutation_id=_resolve_id(mutation_id_factory),
        guild_id=guild_id,
        actor_id=actor_id,
        actor_type=actor_type,
    )
    sink.record(record)

    return ExplorationResult(
        ok=True,
        action="accept",
        message=f"Accepted {accepted.template_id} — the quest is now active.",
        quest=accepted,
        energy_after=state.energy or 0,
        record=record,
    )


# ---------------------------------------------------------------------------
# Op 3 — apply_action (a bounded action advances an objective + spends energy)
# ---------------------------------------------------------------------------
def apply_action(
    state: ExplorationState,
    action: str,
    *,
    sink: Sink,
    resolver: EncounterResolver | None = None,
    guild_id: int | None = None,
    actor_id: int | None = None,
    actor_type: str = ACTOR_PLAYER,
    now: datetime | None = None,
    mutation_id_factory: Callable[[], str] | None = None,
) -> ExplorationResult:
    """Take one bounded action: resolve an encounter, advance the objective, audit.

    Maps a BOUNDED *action* (one of the active quest's pending objective keys) to
    the objective-advancing :class:`GameEvent` the engine already defines, then:
    resolve an ``EXPLORE_ACTION`` encounter via the shared
    :class:`ReferenceEncounterResolver` (deterministic, seeded from
    ``world_seed``) → debit the difficulty's survival ``cost`` from ``energy`` →
    call :func:`games.exploration.quest.engine.apply_event` (which advances the
    matching objective and flips the instance to COMPLETED when all are done) →
    emit ONE audit record → return a frozen :class:`ExplorationResult`.

    Honest no-ops that change nothing and record nothing (``ok=False``):

    * no ACTIVE quest (offer + accept first),
    * *action* is off the bounded pending-objective menu (never a silent clamp —
      exploration surfaces the valid menu instead),
    * too tired — ``energy < cost`` (the survive-the-wild gate; mirrors fishing's
      too-tired cast).

    Determinism: with a fixed ``world_seed`` + ``player_id`` and an injected
    ``now`` / ``mutation_id_factory`` the encounter AND the record reproduce
    byte-for-byte.
    """
    instance = state.quest
    if instance is None or instance.state is not QuestState.ACTIVE:
        return ExplorationResult(
            ok=False,
            action="action",
            message="no active quest — offer and accept one first",
            quest=instance,
            energy_after=state.energy or 0,
        )

    if action not in pending_actions(instance):
        valid = ", ".join(pending_actions(instance)) or "(none)"
        return ExplorationResult(
            ok=False,
            action="action",
            message=f"{action!r} is not a valid action — pick one of: {valid}",
            quest=instance,
            energy_after=state.energy or 0,
        )

    cost = state.tunables.cost
    energy_before = state.energy or 0
    if energy_before < cost:
        return ExplorationResult(
            ok=False,
            action="action",
            message=f"too tired to press on (energy {energy_before} < cost {cost}) — rest and try again",
            quest=instance,
            energy_after=energy_before,
        )

    # Resolve an EXPLORE_ACTION encounter (deterministic; never CHAT_ACTIVITY).
    active_resolver = resolver if resolver is not None else _DEFAULT_RESOLVER
    encounter = active_resolver.resolve(
        EncounterRequest(
            trigger=EncounterTrigger.EXPLORE_ACTION,
            player_id=state.player_id,
            world_seed=state.world_seed,
            context={
                "quest": instance.instance_id,
                "action": action,
                "step": instance.step,
            },
        )
    )
    state.last_encounter = encounter

    # Spend survival energy (cost VERBATIM from the difficulty tunables).
    state.energy = energy_before - cost

    prev_render = _progress_render(instance, action)
    event = _objective_event(instance, action)
    assert event is not None  # guaranteed by the pending_actions membership check
    advanced = quest_engine.apply_event(instance, event)
    state.quest = advanced
    new_render = _progress_render(advanced, action)

    completed = advanced.state is QuestState.COMPLETED

    record = _make_record(
        mutation_type=MUTATION_ACTION,
        target=f"objective:{advanced.template_id}:{action}",
        prev_value=prev_render,
        new_value=new_render,
        now=_resolve_now(now),
        mutation_id=_resolve_id(mutation_id_factory),
        guild_id=guild_id,
        actor_id=actor_id,
        actor_type=actor_type,
    )
    sink.record(record)

    detail = f"{action}: {new_render}"
    enc = f"encounter {encounter.kind} (intensity {encounter.payload['intensity']})"
    message = f"{detail} · {enc}"
    if completed:
        message += " · quest COMPLETE — bank the reward"

    return ExplorationResult(
        ok=True,
        action="action",
        message=message,
        quest=advanced,
        encounter=encounter,
        completed=completed,
        energy_after=state.energy,
        record=record,
    )


# ---------------------------------------------------------------------------
# Op 4 — grant_rewards (bank the capped bundle on COMPLETED)
# ---------------------------------------------------------------------------
def grant_rewards(
    state: ExplorationState,
    *,
    sink: Sink,
    guild_id: int | None = None,
    actor_id: int | None = None,
    actor_type: str = ACTOR_PLAYER,
    now: datetime | None = None,
    mutation_id_factory: Callable[[], str] | None = None,
) -> ExplorationResult:
    """Bank a COMPLETED quest's tier-capped reward: fold it into the ledger, audit.

    Wires :func:`games.exploration.quest.engine.grant_rewards` (which returns the
    tier-capped :class:`RewardBundle` and RAISES unless the instance is COMPLETED)
    → fold the bundle into ``state.ledger`` (code-owned; never re-sized) → retire
    the quest (``state.quest = None`` so a fresh quest can be offered) → emit ONE
    audit record. With NO COMPLETED quest this is an honest no-op: nothing
    changes, nothing records, ``ok=False`` (the seam checks the state itself, so
    the engine's raise is never reached).
    """
    instance = state.quest
    if instance is None or instance.state is not QuestState.COMPLETED:
        return ExplorationResult(
            ok=False,
            action="grant",
            message="no completed quest to bank — finish an active quest's objectives first",
            quest=instance,
            energy_after=state.energy or 0,
        )

    bundle = quest_engine.grant_rewards(instance)
    prev_summary = state.ledger.summary()
    state.ledger.fold(bundle)
    new_summary = state.ledger.summary()
    banked = instance
    state.quest = None

    record = _make_record(
        mutation_type=MUTATION_GRANT,
        target=f"reward:{banked.instance_id}",
        prev_value=prev_summary,
        new_value=new_summary,
        now=_resolve_now(now),
        mutation_id=_resolve_id(mutation_id_factory),
        guild_id=guild_id,
        actor_id=actor_id,
        actor_type=actor_type,
    )
    sink.record(record)

    reward_line = f"xp {bundle.global_xp} · game-xp {bundle.game_xp} · coins {bundle.currency}"
    if bundle.capability is not None:
        reward_line += f" · capability {bundle.capability}"
    return ExplorationResult(
        ok=True,
        action="grant",
        message=f"Banked {banked.template_id} (tier {banked.tier.value}): {reward_line}",
        quest=banked,
        reward=bundle,
        completed=True,
        energy_after=state.energy or 0,
        record=record,
    )


__all__ = [
    "AuditRecord",
    "Sink",
    "InMemorySink",
    "ExplorationState",
    "ExplorationResult",
    "RewardLedger",
    "ACTOR_PLAYER",
    "MUTATION_OFFER",
    "MUTATION_ACCEPT",
    "MUTATION_ACTION",
    "MUTATION_GRANT",
    "quest_menu",
    "pending_actions",
    "offer",
    "accept",
    "apply_action",
    "grant_rewards",
]
