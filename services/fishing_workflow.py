"""Fishing WORKFLOW audited seam — rung 2 of the fishing ladder.

The audited **write boundary** for fishing. Below it sits the shipped PURE CORE
(``games/fishing/core/``, four stdlib-only modules of a stateless catch
resolver); above it (rung 3) a HOST adapter will bind this seam onto the
superbot-next plugin contract. This module is the middle rung: the one
state-changing fishing op is orchestrated here in one place —

    read session state  ->  call PURE CORE (``resolve_cast``) to decide  ->
    mutate the state  ->  build an audit record  ->  ``sink.record(...)``  ->
    return a frozen Result

Design provenance mirrors the just-landed mining seam
(``services/mining_workflow.py`` — ``docs/design/mining-workflow-seam.md`` §5):

* **D1** — the seam's audit record is the oracle's 11-field structural
  ``audit.action_recorded`` schema (:class:`AuditRecord`), adopted VERBATIM.
  It is GAME-NEUTRAL and lives in ``services/audit.py`` so mining and fishing
  reuse it without welding two games together — this seam
  ``from services.audit import AuditRecord, Sink, InMemorySink`` and NEVER
  imports ``services/mining_workflow.py``.
* **D2** — the seam audits **every** state-changing action routed through it,
  including a catch grant. A cast that changes nothing (too tired to cast —
  ``resolve_cast`` returns its honest 😴 no-bite with ``energy_cost == 0``)
  records NOTHING.

Fishing has ONE decide-fn (:func:`games.fishing.core.catch.resolve_cast`), so
the seam has ONE state-changing action — :func:`cast`. There is no sell / buy /
move leg because no fishing economy exists yet (the shared inventory ``Grant``
carries an EMPTY ``ProgressionDelta`` for a catch); those future actions are
gated on that economy gap and filed as SIM-REQUESTs in ``control/outbox.md``,
not built here.

Balance discipline: every number/noun (bite chance, size, species, narration)
comes VERBATIM from the pure core / its data tables (never re-derived here).
Only *structural* audit fields — the mutation id, timestamps, ids, ``scope`` and
``target`` strings — are constructed (they carry no balance meaning). Fishing has
no economy reason tokens, so the ``mutation_type`` / ``target`` verbs are purely
structural (``fishing:cast`` / ``haul:<species>`` / ``energy``). This module is
stdlib-only apart from ``games.fishing.*`` (+ the shared ``games.mining.core``
energy/stat types the fishing core itself reuses) so CI stays hermetic.
"""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from services.audit import AuditRecord, InMemorySink, Sink

from games.fishing.core import catch as catch_core
from games.fishing.core.catch import CastOutcome
from games.fishing.inventory import adapter
from games.mining.core import energy as energy_model
from games.mining.core.equipment import EffectiveStats

# --- structural mutation-type / target tokens ------------------------------
# Fishing has NO economy reason tokens (no sell/buy/reward curve exists yet), so
# the seam constructs stable STRUCTURAL tokens for its one action — a
# ``fishing:cast`` verb (the ``fishing:*`` namespace, mirroring mining's
# ``mining:*`` structural verbs) and a ``haul:<species>`` / ``energy`` target.
# These carry no balance meaning.
MUTATION_CAST = "fishing:cast"

#: Target string for the energy leg of an empty cast (a real cast that spent
#: energy but landed nothing) — mirrors mining's bare ``depth`` / ``vault``.
TARGET_ENERGY = "energy"

#: The seam's actor-type token for a human player (the ``actor_type`` field of
#: :class:`AuditRecord`; the oracle's capability-resolver actor-type slot).
ACTOR_PLAYER = "player"


# ---------------------------------------------------------------------------
# The audit record (D1) + the sink port (D3/D4) are GAME-NEUTRAL and live in
# ``services/audit.py`` so every game's seam reuses them without coupling; the
# fishing seam re-exports them for callers that import off this module.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# The session state the seam mutates
# ---------------------------------------------------------------------------
@dataclass
class FishingState:
    """A full mutable fishing session — everything the seam reads and writes.

    Field notes:

    * ``energy`` — remaining energy (a plain int, the unit
      :func:`games.fishing.core.catch.resolve_cast` reads); a cast debits
      :data:`games.fishing.core.catch.CAST_COST`.
    * ``spot_id`` — the fishing spot a cast defaults to (a cast may override it
      per call). An unknown / ``None`` id resolves to the core's neutral default
      profile — the resolver never raises.
    * ``haul`` — the accumulated catch, ``{species_id: count}``. A landed fish is
      folded in through the shared inventory adapter
      (:func:`games.fishing.inventory.adapter.cast_to_grant`): the returned
      ``Grant``'s stacks are keyed back to their neutral ``species_id`` and
      counted, so the haul honestly mirrors the shared ``Grant`` shape.
    * ``seed`` — the fishing world seed; combined with the spot id it derives the
      resolver's deterministic-default RNG (``(seed, spot_id)`` → the same cast).
    * ``stats`` — the player's :class:`EffectiveStats` (``None`` = a bare
      baseline angler); only ``fishing_power`` / ``bite_luck`` are read.
    """

    seed: int = 0
    spot_id: str = "dock"
    energy: int = field(default_factory=lambda: energy_model.MAX_ENERGY)
    haul: dict[str, int] = field(default_factory=dict)
    stats: EffectiveStats | None = None


# ---------------------------------------------------------------------------
# Result dataclass — the seam's frozen return contract for a cast
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class FishingResult:
    """Outcome of a :func:`cast` op.

    ``ok`` is ``True`` when the cast changed state (a real cast — energy was
    debited, and on a bite a catch was folded into the haul) and an audit record
    was emitted; ``False`` for the honest too-tired no-op (nothing changed,
    nothing recorded). ``outcome`` is the pure :class:`CastOutcome` verbatim.
    """

    ok: bool
    message: str
    outcome: CastOutcome | None = None
    bit: bool = False
    species: str | None = None
    size: int | None = None
    energy_after: int = 0
    record: AuditRecord | None = None


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
        subsystem="fishing",
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


def _fold_catch(state: FishingState, outcome: CastOutcome) -> tuple[str, int, int] | None:
    """Fold a bite's :class:`Grant` into ``state.haul``; return ``(species, prev, new)``.

    Runs the landed catch through the shared inventory adapter
    (:func:`games.fishing.inventory.adapter.cast_to_grant`) and counts each
    resulting stack under its neutral ``species_id`` — so the haul is folded from
    the SAME ``Grant`` shape the shared contract uses, never a bespoke tally.
    Returns ``None`` for a no-bite outcome (an EMPTY grant folds nothing).
    """
    grant = adapter.cast_to_grant(outcome)
    folded: tuple[str, int, int] | None = None
    for stack in grant.items:
        species = adapter.species_id_for_item(stack.item)
        prev = state.haul.get(species, 0)
        new_total = prev + stack.qty
        state.haul[species] = new_total
        folded = (species, prev, new_total)
    return folded


# ---------------------------------------------------------------------------
# The one action — cast
# ---------------------------------------------------------------------------
def cast(
    state: FishingState,
    *,
    sink: Sink,
    spot_id: str | None = None,
    stats: EffectiveStats | None = None,
    guild_id: int | None = None,
    actor_id: int | None = None,
    actor_type: str = ACTOR_PLAYER,
    rng: random.Random | None = None,
    now: datetime | None = None,
    mutation_id_factory: Callable[[], str] | None = None,
) -> FishingResult:
    """Cast once: the pure core decides, the seam applies the debit + grant and audits.

    Wires :func:`games.fishing.core.catch.resolve_cast` (which reads
    ``state.energy`` and the spot/stat levers) → on any real cast, debit
    :data:`~games.fishing.core.catch.CAST_COST` from ``state.energy`` and, on a
    bite, fold the catch into ``state.haul`` via the shared inventory adapter →
    build ONE :class:`AuditRecord` and ``sink.record(...)`` it as the last commit
    step → return a frozen :class:`FishingResult`.

    Determinism: with ``rng=None`` the core derives its stream from
    ``(state.seed, spot_id)``, so a fixed seed + spot + injected ``now`` /
    ``mutation_id_factory`` reproduces the cast AND its record byte-for-byte. A
    host wanting live variance injects its own ``random.Random``.

    A **too-tired** cast (``state.energy < CAST_COST``) changes nothing: the core
    returns its honest 😴 no-bite (``energy_cost == 0``), and the seam records
    NOTHING and returns ``ok=False``. Every real cast — a bite OR an empty
    cast that still spent energy — records exactly one record and returns
    ``ok=True``.
    """
    spot = spot_id if spot_id is not None else state.spot_id
    effective_stats = stats if stats is not None else state.stats

    outcome = catch_core.resolve_cast(
        state.seed,
        spot,
        effective_stats,
        energy=state.energy,
        rng=rng,
    )

    # Too tired to cast: the core spent nothing and caught nothing — an honest
    # no-op that mutates no state, so the seam records NOTHING (D2).
    if outcome.energy_cost == 0:
        return FishingResult(
            ok=False,
            message=outcome.narration,
            outcome=outcome,
            bit=False,
            energy_after=state.energy,
        )

    # A real cast — debit energy first (the cost is VERBATIM from the outcome).
    energy_before = state.energy
    state.energy = energy_before - outcome.energy_cost

    now_dt = _resolve_now(now)
    folded = _fold_catch(state, outcome)

    if folded is not None:
        # A bite: the primary mutation is the catch grant (mirrors mining's
        # ``mine``, which records the grant target, not the energy side effect).
        species, prev_count, new_count = folded
        record = _make_record(
            mutation_type=MUTATION_CAST,
            target=f"haul:{species}",
            prev_value=str(prev_count),
            new_value=str(new_count),
            now=now_dt,
            mutation_id=_resolve_id(mutation_id_factory),
            guild_id=guild_id,
            actor_id=actor_id,
            actor_type=actor_type,
        )
    else:
        # An empty cast: no fish, but energy WAS spent — the audited mutation is
        # the energy leg (prev/new energy).
        record = _make_record(
            mutation_type=MUTATION_CAST,
            target=TARGET_ENERGY,
            prev_value=str(energy_before),
            new_value=str(state.energy),
            now=now_dt,
            mutation_id=_resolve_id(mutation_id_factory),
            guild_id=guild_id,
            actor_id=actor_id,
            actor_type=actor_type,
        )

    sink.record(record)

    catch = outcome.catch
    return FishingResult(
        ok=True,
        message=outcome.narration,
        outcome=outcome,
        bit=outcome.bit,
        species=catch.species_id if catch is not None else None,
        size=catch.size if catch is not None else None,
        energy_after=state.energy,
        record=record,
    )


__all__ = [
    "AuditRecord",
    "Sink",
    "InMemorySink",
    "FishingState",
    "FishingResult",
    "ACTOR_PLAYER",
    "MUTATION_CAST",
    "TARGET_ENERGY",
    "cast",
]
