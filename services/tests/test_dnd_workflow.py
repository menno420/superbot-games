"""Tests for the D&D WORKFLOW audited seam (``services/dnd_workflow.py``).

Covers the seam's guarantees, mirrored from the fishing/mining seam suites —

1. the one state-changing action (:func:`choose`) emits exactly one well-formed
   11-field :class:`AuditRecord` per pick; UNLIKE fishing (whose too-tired no-op
   records nothing), a D&D ``choose`` ALWAYS records because the audited EVENT is
   the DM's bounded DECISION itself — an off-menu clamp to the safe default STILL
   records the default resolution (this seam's honest D2 divergence);
2. reward accumulation folds the engine's tier-capped bundle VERBATIM;
3. scene advancement along the option's pre-defined edge + the ``None`` ⇒ ended
   beat;
4. determinism under a fixed seed + injected clock + id factory;
5. the game-neutral ``services/audit.py`` reuse (no coupling to another game's
   seam).
"""

from __future__ import annotations

import inspect
from dataclasses import fields
from datetime import datetime, timezone

import pytest

from services import audit, dnd_workflow as dw
from services.audit import AuditRecord, InMemorySink, Sink

from games.dnd.core.effects import EFFECTS
from games.dnd.core.resolver import Resolution
from games.dnd.data.scenes import get_scene
from games.exploration.quest.rng import derive_seed

FIXED_NOW = datetime(2026, 7, 13, 12, 0, 0, tzinfo=timezone.utc)
FIXED_ID = "deadbeefdeadbeefdeadbeefdeadbeef"


def _fixed_id() -> str:
    return FIXED_ID


def _state(**overrides) -> dw.DnDState:
    """A fresh session at the start scene; override any field per test."""
    base = dict(scene_id=dw.START_SCENE, seed=0, player_id="player")
    base.update(overrides)
    return dw.DnDState(**base)


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
    assert rec.subsystem == "dnd"
    assert rec.mutation_type == dw.MUTATION_CHOOSE
    assert isinstance(rec.target, str) and rec.target
    assert rec.scope == "global"
    assert isinstance(rec.actor_type, str) and rec.actor_type
    assert isinstance(rec.occurred_at, datetime)
    assert rec.prev_value is None or isinstance(rec.prev_value, str)
    assert rec.new_value is None or isinstance(rec.new_value, str)
    assert rec.guild_id is None or isinstance(rec.guild_id, int)
    assert rec.actor_id is None or isinstance(rec.actor_id, int)


# ---------------------------------------------------------------------------
# One well-formed record per choose (reward / narrate / no-op / off-menu clamp)
# ---------------------------------------------------------------------------
# (option_id, expected chosen id, expected target prefix)
_CHOICES = [
    ("advance_escort", "advance_escort", "reward:"),  # mints the escort reward
    ("scout_ahead", "scout_ahead", "scene:"),  # narrate-only, advances
    ("make_camp", "make_camp", "scene:"),  # safe no-op default, off surfaced menu -> clamp
    ("totally_bogus", "make_camp", "scene:"),  # off-menu id -> clamp to default
]


@pytest.mark.parametrize(
    "option_id,expected_chosen,target_prefix",
    _CHOICES,
    ids=[c[0] for c in _CHOICES],
)
def test_every_choose_records_exactly_one_well_formed_record(
    option_id, expected_chosen, target_prefix
):
    """Every choose — reward, narrate, no-op, or off-menu clamp — records one row."""
    state = _state()
    sink = InMemorySink()
    result = dw.choose(state, option_id, sink=sink, now=FIXED_NOW, mutation_id_factory=_fixed_id)
    assert result.ok
    assert len(sink.records) == 1
    rec = sink.records[0]
    _assert_well_formed(rec)
    assert result.resolution.chosen_option_id == expected_chosen
    assert rec.target.startswith(target_prefix)
    assert rec is result.record
    assert rec.mutation_id == FIXED_ID
    assert rec.occurred_at == FIXED_NOW


def test_off_menu_id_clamps_to_default_and_still_records():
    """An off-menu / hallucinated id clamps to the safe default AND records it."""
    state = _state()
    sink = InMemorySink()
    result = dw.choose(state, "not-a-real-option", sink=sink, now=FIXED_NOW)
    assert result.resolution.clamped is True
    assert result.resolution.chosen_option_id == "make_camp"  # scene default
    assert len(sink.records) == 1  # the clamped decision is still audited (D2)


def test_non_string_option_id_clamps_without_raising():
    """A non-string payload (None) clamps to the default — the seam never raises."""
    state = _state()
    sink = InMemorySink()
    result = dw.choose(state, None, sink=sink, now=FIXED_NOW)
    assert result.resolution.clamped is True
    assert result.resolution.chosen_option_id == "make_camp"
    assert len(sink.records) == 1


def test_valid_on_menu_choice_is_not_clamped():
    state = _state()
    result = dw.choose(state, "advance_escort", sink=InMemorySink(), now=FIXED_NOW)
    assert result.resolution.clamped is False


# ---------------------------------------------------------------------------
# Reward folds the engine's tier-capped bundle VERBATIM + accumulates
# ---------------------------------------------------------------------------
def test_reward_folds_engine_bundle_verbatim():
    """A minted reward matches the pure effect's bundle exactly (no re-derivation)."""
    state = _state()
    result = dw.choose(state, "advance_escort", sink=InMemorySink(), now=FIXED_NOW)
    # The effect mints for a seed derived exactly as the resolver derives it.
    scene = get_scene(dw.START_SCENE)
    scene_seed = derive_seed("dnd-story:v1", state.seed, scene.scene_id)
    expected = EFFECTS["escort_step"].apply(seed=scene_seed, player_id="player").reward
    assert result.reward == expected
    assert state.global_xp == expected.global_xp
    assert state.game_xp == expected.game_xp
    assert state.currency == expected.currency


def test_reward_accumulates_across_the_escort_double_mint_arc():
    """The one arc that fires escort_step twice mints the reward 2x (the SIM-REQUEST)."""
    state = _state()
    sink = InMemorySink()
    r1 = dw.choose(state, "advance_escort", sink=sink, now=FIXED_NOW)  # mint #1 -> gate
    dw.choose(state, "circle_to_treeline", sink=sink, now=FIXED_NOW)  # narrate -> treeline
    r3 = dw.choose(state, "signal_escort", sink=sink, now=FIXED_NOW)  # mint #2 -> ended
    unit = r1.reward
    assert state.currency == unit.currency * 2
    assert state.game_xp == unit.game_xp * 2
    assert state.global_xp == unit.global_xp * 2
    assert r3.reward == unit  # each mint is the same tier-capped bundle


def test_narrate_only_choice_mints_no_reward():
    state = _state()
    result = dw.choose(state, "scout_ahead", sink=InMemorySink(), now=FIXED_NOW)
    assert result.reward is None
    assert (state.global_xp, state.game_xp, state.currency) == (0, 0, 0)


def test_reward_record_brackets_the_mint_in_its_summary():
    """A minted choose records a before/after reward summary bracketing the fold."""
    state = _state()
    sink = InMemorySink()
    dw.choose(state, "advance_escort", sink=sink, now=FIXED_NOW)
    rec = sink.records[0]
    assert rec.target == "reward:waystation_road"
    assert rec.prev_value == "g0/x0/c0"
    assert rec.new_value == "g5/x25/c10"  # verbatim from the tier-capped bundle


# ---------------------------------------------------------------------------
# Scene advancement + ended state
# ---------------------------------------------------------------------------
def test_choice_advances_scene_along_the_predefined_edge():
    state = _state()
    result = dw.choose(state, "advance_escort", sink=InMemorySink(), now=FIXED_NOW)
    assert result.prev_scene == "waystation_road"
    assert result.next_scene == "waystation_gate"
    assert state.scene_id == "waystation_gate"  # state advanced
    assert result.ended is False


def test_none_transition_ends_the_beat_and_leaves_scene_unchanged():
    """An option with no successor scene concludes the beat; scene_id is unchanged."""
    state = _state(scene_id="treeline_watch")
    result = dw.choose(state, "signal_escort", sink=InMemorySink(), now=FIXED_NOW)
    assert result.next_scene is None
    assert result.ended is True
    assert state.scene_id == "treeline_watch"  # stays put (no successor)


def test_scene_transition_record_carries_prev_and_next():
    state = _state()
    sink = InMemorySink()
    dw.choose(state, "scout_ahead", sink=sink, now=FIXED_NOW)  # -> treeline_watch
    rec = sink.records[0]
    assert rec.target == "scene:waystation_road"
    assert rec.prev_value == "waystation_road"
    assert rec.new_value == "treeline_watch"


def test_ended_transition_record_has_none_new_value():
    state = _state(scene_id="treeline_watch")
    sink = InMemorySink()
    dw.choose(state, "hold_position", sink=sink, now=FIXED_NOW)  # narrate, next None
    rec = sink.records[0]
    assert rec.new_value is None  # no successor scene -> honest "no next"


# ---------------------------------------------------------------------------
# Menu surfacing mirrors the resolver's accepted set
# ---------------------------------------------------------------------------
def test_surfaced_options_match_the_resolver_accepted_width():
    """At the skeleton floor (xp 0) exactly two options surface; a third clamps."""
    scene = get_scene(dw.START_SCENE)
    ids = [o.id for o in dw.surfaced_options(scene, xp=0)]
    assert ids == ["advance_escort", "scout_ahead"]
    # make_camp is the default (clamp target) but NOT surfaced at the floor width.
    assert scene.default_option_id == "make_camp"
    assert "make_camp" not in ids


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------
def test_choose_is_deterministic_with_injected_clock_and_id():
    """A fixed seed + player + injected clock/id → byte-identical records."""
    a, b = _state(), _state()
    sink_a, sink_b = InMemorySink(), InMemorySink()
    ra = dw.choose(a, "advance_escort", sink=sink_a, now=FIXED_NOW, mutation_id_factory=_fixed_id)
    rb = dw.choose(b, "advance_escort", sink=sink_b, now=FIXED_NOW, mutation_id_factory=_fixed_id)
    assert ra.reward == rb.reward
    assert sink_a.records[0] == sink_b.records[0]


def test_default_clock_and_id_are_used_when_not_injected():
    state = _state()
    before = datetime.now(timezone.utc)
    r = dw.choose(state, "advance_escort", sink=InMemorySink())
    after = datetime.now(timezone.utc)
    assert before <= r.record.occurred_at <= after
    assert len(r.record.mutation_id) == 32  # uuid4().hex default


def test_distinct_mutation_ids_across_chooses_by_default():
    state = _state()
    sink = InMemorySink()
    dw.choose(state, "advance_escort", sink=sink)  # -> gate
    dw.choose(state, "rest_at_gate", sink=sink)  # -> stays (default), still records
    assert sink.records[0].mutation_id != sink.records[1].mutation_id


# ---------------------------------------------------------------------------
# Result / resolution shape
# ---------------------------------------------------------------------------
def test_result_carries_the_pure_resolution_verbatim():
    state = _state()
    result = dw.choose(state, "advance_escort", sink=InMemorySink(), now=FIXED_NOW)
    assert isinstance(result.resolution, Resolution)
    assert result.resolution.scene_id == "waystation_road"
    assert result.resolution.next_scene_id == result.next_scene


def test_dnd_result_is_frozen():
    r = dw.choose(_state(), "scout_ahead", sink=InMemorySink(), now=FIXED_NOW)
    with pytest.raises(Exception):
        r.ok = False  # frozen


def test_message_is_verbatim_scene_copy():
    from games.dnd.data.scenes import text_for

    state = _state()
    r = dw.choose(state, "advance_escort", sink=InMemorySink(), now=FIXED_NOW)
    assert r.message == text_for("opt.advance_escort")


# ---------------------------------------------------------------------------
# The game-neutral services/audit.py reuse (no cross-game coupling)
# ---------------------------------------------------------------------------
def test_audit_module_exposes_neutral_types_and_seam_reexports_them():
    assert set(audit.__all__) == {"AuditRecord", "Sink", "InMemorySink"}
    assert dw.AuditRecord is AuditRecord
    assert dw.Sink is Sink
    assert dw.InMemorySink is InMemorySink


def test_seam_does_not_import_another_games_workflow():
    """Reuse is via the neutral audit types — never another game's seam.

    A docstring may CITE the fishing/mining seams as design provenance, but there
    is no code coupling: the seam imports the neutral audit types and never another
    game's ``*_workflow`` module.
    """
    src = inspect.getsource(dw)
    assert "from services.audit import" in src
    assert "import mining_workflow" not in src
    assert "from services.mining_workflow" not in src
    assert "import fishing_workflow" not in src
    assert "from services.fishing_workflow" not in src
    assert "services.mining_workflow" not in dw.__dict__
    assert "services.fishing_workflow" not in dw.__dict__


def test_inmemory_sink_satisfies_the_sink_protocol():
    sink = InMemorySink()
    assert isinstance(sink, Sink)  # runtime_checkable Protocol
    assert sink.records == []
