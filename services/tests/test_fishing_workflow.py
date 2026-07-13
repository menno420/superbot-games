"""Tests for the fishing WORKFLOW audited seam (``services/fishing_workflow.py``).

Covers the two REQUIRED guarantees (mirrored from the mining seam suite) —

1. the one state-changing action (:func:`cast`) emits exactly one well-formed
   11-field :class:`AuditRecord`; a too-tired no-op records NOTHING;
2. the pure fishing core stays importable and pure WITHOUT the seam layer —

plus behavioural tests (bite grant / empty-cast energy leg / haul accumulation /
spot + stat levers), determinism under a seeded ``(seed, spot_id)`` default
stream AND an injected clock + id factory, and the game-neutral
``services/audit.py`` reuse (no mining coupling).
"""

from __future__ import annotations

import importlib
import pkgutil
import random
import sys
from dataclasses import fields
from datetime import datetime, timezone

import pytest

from games.fishing.core import catch
from games.fishing.inventory import adapter
from games.mining.core import energy as energy_model
from games.mining.core.equipment import EffectiveStats
from services import audit, fishing_workflow as fw
from services.audit import AuditRecord, InMemorySink, Sink

FIXED_NOW = datetime(2026, 7, 13, 12, 0, 0, tzinfo=timezone.utc)
FIXED_ID = "deadbeefdeadbeefdeadbeefdeadbeef"

# Deterministic (seed, spot) fixtures — probed from the pure core:
#   seed 0 @ dock -> a BITE (bass);  seed 1 @ dock -> an EMPTY cast (no bite).
SEED_BITE = 0
SEED_EMPTY = 1


def _fixed_id() -> str:
    return FIXED_ID


def _state(**overrides) -> fw.FishingState:
    """A rested angler at the neutral dock; override any field per test."""
    base = dict(seed=SEED_BITE, spot_id="dock", energy=energy_model.MAX_ENERGY, haul={}, stats=None)
    base.update(overrides)
    return fw.FishingState(**base)


# ---------------------------------------------------------------------------
# The 11-field audit-schema well-formedness helper
# ---------------------------------------------------------------------------
_AUDIT_FIELDS = (
    "mutation_id",
    "subsystem",
    "mutation_type",
    "target",
    "scope",
    "guild_id",
    "prev_value",
    "new_value",
    "actor_id",
    "actor_type",
    "occurred_at",
)


def _assert_well_formed(rec: AuditRecord) -> None:
    """Assert an AuditRecord carries all 11 fields, populated to spec."""
    assert [f.name for f in fields(rec)] == list(_AUDIT_FIELDS)
    assert isinstance(rec.mutation_id, str) and rec.mutation_id
    assert rec.subsystem == "fishing"
    assert isinstance(rec.mutation_type, str) and rec.mutation_type
    assert isinstance(rec.target, str) and rec.target
    assert rec.scope == "global"
    assert isinstance(rec.actor_type, str) and rec.actor_type
    assert isinstance(rec.occurred_at, datetime)
    assert rec.prev_value is None or isinstance(rec.prev_value, str)
    assert rec.new_value is None or isinstance(rec.new_value, str)
    assert rec.guild_id is None or isinstance(rec.guild_id, int)
    assert rec.actor_id is None or isinstance(rec.actor_id, int)


# ---------------------------------------------------------------------------
# REQUIRED TEST 1 — audit-per-state-changing-cast
# ---------------------------------------------------------------------------
def _do_bite(state, sink):
    return fw.cast(state, sink=sink, now=FIXED_NOW, mutation_id_factory=_fixed_id)


def _do_empty(state, sink):
    state.seed = SEED_EMPTY
    return fw.cast(state, sink=sink, now=FIXED_NOW, mutation_id_factory=_fixed_id)


_STATE_CHANGING = [
    ("bite", _do_bite, "haul:bass"),
    ("empty_cast", _do_empty, fw.TARGET_ENERGY),
]


@pytest.mark.parametrize("name,action,expected_target", _STATE_CHANGING, ids=[c[0] for c in _STATE_CHANGING])
def test_state_changing_cast_records_exactly_one_well_formed_record(name, action, expected_target):
    """Every real cast (bite OR empty) emits exactly one well-formed AuditRecord."""
    state = _state()
    sink = InMemorySink()
    result = action(state, sink)
    assert result.ok, f"{name} should have changed state"
    assert len(sink.records) == 1, f"{name} must record exactly one record"
    rec = sink.records[0]
    _assert_well_formed(rec)
    assert rec.mutation_type == fw.MUTATION_CAST
    assert rec.target == expected_target
    assert rec is result.record
    # the injected id / clock flow straight through to the record
    assert rec.mutation_id == FIXED_ID
    assert rec.occurred_at == FIXED_NOW


def test_too_tired_cast_records_nothing():
    """A too-tired cast changes nothing: ok=False, the honest 😴 message, no record."""
    state = _state(energy=catch.CAST_COST - 1)
    sink = InMemorySink()
    before_energy, before_haul = state.energy, dict(state.haul)
    result = fw.cast(state, sink=sink, now=FIXED_NOW)
    assert result.ok is False
    assert "😴" in result.message
    assert result.record is None
    assert sink.records == []
    # nothing mutated
    assert state.energy == before_energy
    assert state.haul == before_haul


def test_too_tired_boundary_at_cast_cost():
    """Exactly CAST_COST energy casts (and records); one below is the too-tired no-op."""
    exact = _state(energy=catch.CAST_COST)
    assert fw.cast(exact, sink=InMemorySink(), now=FIXED_NOW).ok is True
    short = _state(energy=catch.CAST_COST - 1)
    assert fw.cast(short, sink=InMemorySink(), now=FIXED_NOW).ok is False


# ---------------------------------------------------------------------------
# REQUIRED TEST 2 — core stays importable / pure WITHOUT the seam
# ---------------------------------------------------------------------------
_FORBIDDEN_PREFIXES = ("services", "cogs", "views", "utils.", "disbot")
_FORBIDDEN = ("discord", "asyncpg", "aiohttp", "requests", "sqlalchemy", "psycopg")


def test_core_stays_importable_and_pure_without_the_seam():
    """Importing the pure fishing core pulls in NO services/host modules (seam-side guard)."""
    for mod in list(sys.modules):
        if mod == "services" or mod.startswith("services."):
            del sys.modules[mod]
    for mod in list(sys.modules):
        if mod == "games.fishing.core" or mod.startswith("games.fishing.core."):
            del sys.modules[mod]

    before = set(sys.modules)
    core = importlib.import_module("games.fishing.core")
    modules = [m.name for m in pkgutil.iter_modules(core.__path__)]
    assert len(modules) == 4, "the fishing core must stay exactly 4 modules"
    for m in modules:
        importlib.import_module(f"games.fishing.core.{m}")
    loaded = set(sys.modules) - before

    forbidden = [
        n
        for n in loaded
        if any(n == f or n.startswith(f + ".") for f in _FORBIDDEN)
        or n.startswith(_FORBIDDEN_PREFIXES)
    ]
    assert forbidden == [], f"impure imports leaked into the pure core: {forbidden}"


def test_core_may_reuse_shared_pure_games_primitives():
    """The purity guard ALLOWS games.* (fishing core reuses mining's pure energy/stats)."""
    core = importlib.import_module("games.fishing.core.catch")
    src = importlib.import_module("inspect").getsource(core)
    # it legitimately imports the shared pure primitives — proof the guard must
    # forbid only host/db layers, never all ``games.`` imports.
    assert "games.mining.core" in src


def test_seam_imports_core_but_core_never_imports_seam():
    """The one-way dependency: the seam names the fishing core; core never names services."""
    import inspect

    src = inspect.getsource(fw)
    assert "from games.fishing.core" in src
    core_src = importlib.import_module("games.fishing.core.catch")
    assert "services" not in inspect.getsource(core_src)


# ---------------------------------------------------------------------------
# Behavioural — a bite
# ---------------------------------------------------------------------------
def test_bite_grants_catch_to_haul_and_spends_energy():
    state = _state()
    sink = InMemorySink()
    start_energy = state.energy
    r = fw.cast(state, sink=sink, now=FIXED_NOW)
    assert r.ok and r.bit
    assert r.species == "bass"  # deterministic (seed 0 @ dock)
    assert state.haul["bass"] == 1
    assert state.energy == start_energy - catch.CAST_COST
    assert r.energy_after == state.energy
    assert r.record.target == "haul:bass"
    assert r.record.prev_value == "0" and r.record.new_value == "1"


def test_bite_carries_outcome_and_size_verbatim():
    state = _state()
    r = fw.cast(state, sink=InMemorySink(), now=FIXED_NOW)
    # the frozen CastOutcome is relayed verbatim (no re-derivation in the seam)
    assert r.outcome is not None and r.outcome.bit is True
    assert r.outcome.catch is not None
    assert r.species == r.outcome.catch.species_id
    assert r.size == r.outcome.catch.size
    assert r.message == r.outcome.narration


# ---------------------------------------------------------------------------
# Behavioural — an empty cast (energy leg)
# ---------------------------------------------------------------------------
def test_empty_cast_debits_energy_records_energy_leg_and_leaves_haul_empty():
    state = _state(seed=SEED_EMPTY)
    sink = InMemorySink()
    start_energy = state.energy
    r = fw.cast(state, sink=sink, now=FIXED_NOW)
    assert r.ok and r.bit is False
    assert r.species is None and r.size is None
    assert state.haul == {}  # nothing landed
    assert state.energy == start_energy - catch.CAST_COST
    rec = sink.records[0]
    assert rec.target == fw.TARGET_ENERGY
    assert rec.prev_value == str(start_energy)
    assert rec.new_value == str(start_energy - catch.CAST_COST)


# ---------------------------------------------------------------------------
# Behavioural — haul accumulation across casts
# ---------------------------------------------------------------------------
def test_haul_accumulates_across_repeated_casts_via_the_shared_grant():
    """Repeated bites fold through the adapter Grant and accumulate species counts."""
    # inject an rng that always bites the SAME species so the count climbs
    state = _state()
    sink = InMemorySink()
    for _ in range(3):
        fw.cast(state, sink=sink, rng=random.Random(1), now=FIXED_NOW)  # rng(1) -> pike
    assert state.haul == {"pike": 3}
    # three records, each keyed to the running haul count
    assert [r.new_value for r in sink.records] == ["1", "2", "3"]
    assert [r.prev_value for r in sink.records] == ["0", "1", "2"]


def test_haul_fold_matches_the_adapter_grant_species():
    """The haul is keyed by the adapter's neutral species_id (the Grant shape, honestly)."""
    state = _state()
    r = fw.cast(state, sink=InMemorySink(), rng=random.Random(1), now=FIXED_NOW)
    grant = adapter.cast_to_grant(r.outcome)
    species = adapter.species_id_for_item(grant.items[0].item)
    assert species in state.haul
    assert state.haul[species] == grant.items[0].qty


# ---------------------------------------------------------------------------
# Behavioural — spot + stat levers
# ---------------------------------------------------------------------------
def test_cast_spot_id_param_overrides_state_spot():
    """A per-call spot_id overrides state.spot_id and feeds the core resolver."""
    state = _state(spot_id="dock")
    r = fw.cast(state, sink=InMemorySink(), spot_id="deep_water", rng=random.Random(1), now=FIXED_NOW)
    expected = catch.resolve_cast(state.seed, "deep_water", None, energy=state.energy, rng=random.Random(1))
    assert (r.bit, r.species) == (expected.bit, expected.catch.species_id if expected.catch else None)


def test_cast_reads_stats_from_state_and_param():
    """fishing_power/bite_luck stats flow through (state default + per-call override)."""
    charm = EffectiveStats(fishing_power=catch.MAX_FISHING_POWER, bite_luck=catch.MAX_BITE_LUCK)
    on_state = _state(stats=charm)
    r_state = fw.cast(on_state, sink=InMemorySink(), rng=random.Random(1), now=FIXED_NOW)
    expected = catch.resolve_cast(SEED_BITE, "dock", charm, energy=energy_model.MAX_ENERGY, rng=random.Random(1))
    assert r_state.species == (expected.catch.species_id if expected.catch else None)
    # per-call stats override the state's None
    param = fw.cast(_state(), sink=InMemorySink(), stats=charm, rng=random.Random(1), now=FIXED_NOW)
    assert param.species == r_state.species


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------
def test_cast_deterministic_from_seed_and_spot_with_injected_clock_and_id():
    """rng=None derives from (seed, spot); a fixed seed+clock+id → byte-identical records."""
    a, b = _state(), _state()
    sink_a, sink_b = InMemorySink(), InMemorySink()
    ra = fw.cast(a, sink=sink_a, now=FIXED_NOW, mutation_id_factory=_fixed_id)
    rb = fw.cast(b, sink=sink_b, now=FIXED_NOW, mutation_id_factory=_fixed_id)
    assert (ra.species, ra.size) == (rb.species, rb.size)
    assert sink_a.records[0] == sink_b.records[0]


def test_injected_rng_gives_live_variance():
    """A host-injected rng drives the roll instead of the (seed, spot) default stream."""
    biter = fw.cast(_state(), sink=InMemorySink(), rng=random.Random(1), now=FIXED_NOW)
    misser = fw.cast(_state(), sink=InMemorySink(), rng=random.Random(0), now=FIXED_NOW)
    assert biter.bit is True and misser.bit is False


def test_default_clock_and_id_are_used_when_not_injected():
    state = _state()
    before = datetime.now(timezone.utc)
    r = fw.cast(state, sink=InMemorySink())
    after = datetime.now(timezone.utc)
    rec = r.record
    assert before <= rec.occurred_at <= after
    assert len(rec.mutation_id) == 32  # uuid4().hex default


def test_distinct_mutation_ids_across_casts_by_default():
    state = _state(energy=energy_model.MAX_ENERGY)
    sink = InMemorySink()
    fw.cast(state, sink=sink, rng=random.Random(1))
    fw.cast(state, sink=sink, rng=random.Random(1))
    assert sink.records[0].mutation_id != sink.records[1].mutation_id


def test_energy_drains_to_the_too_tired_floor_over_many_casts():
    """Casting past the energy floor eventually stops recording (honest exhaustion)."""
    state = _state(energy=catch.CAST_COST * 2)  # exactly two casts of headroom
    sink = InMemorySink()
    assert fw.cast(state, sink=sink, rng=random.Random(1)).ok is True
    assert fw.cast(state, sink=sink, rng=random.Random(1)).ok is True
    tired = fw.cast(state, sink=sink, rng=random.Random(1))  # now below CAST_COST
    assert tired.ok is False
    assert len(sink.records) == 2  # the exhausted cast recorded nothing


# ---------------------------------------------------------------------------
# The game-neutral services/audit.py reuse (no mining coupling)
# ---------------------------------------------------------------------------
def test_audit_module_exposes_neutral_types():
    assert set(audit.__all__) == {"AuditRecord", "Sink", "InMemorySink"}
    # the fishing seam re-exports the SAME neutral objects (no divergent copy)
    assert fw.AuditRecord is AuditRecord
    assert fw.Sink is Sink
    assert fw.InMemorySink is InMemorySink


def test_seam_does_not_import_the_mining_workflow():
    """Reuse is via the neutral audit types — the fishing seam never welds to mining's seam."""
    import inspect

    src = inspect.getsource(fw)
    # never IMPORTS the mining seam (a docstring may cite it as design provenance,
    # but there is no code coupling — reuse is via the neutral audit types).
    assert "import mining_workflow" not in src
    assert "from services.mining_workflow" not in src
    assert "services.mining_workflow" not in fw.__dict__
    assert "from services.audit import" in src


def test_inmemory_sink_satisfies_the_sink_protocol():
    sink = InMemorySink()
    assert isinstance(sink, Sink)  # runtime_checkable Protocol
    assert sink.records == []


def test_fishing_result_is_frozen():
    r = fw.cast(_state(), sink=InMemorySink(), now=FIXED_NOW)
    with pytest.raises(Exception):
        r.ok = False  # frozen
