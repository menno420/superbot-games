"""Tests for the Exploration WORKFLOW audited seam (``services/exploration_workflow.py``).

Covers the seam's guarantees, mirrored from the D&D / fishing / mining seam suites —

1. each state-changing op (:func:`offer` / :func:`accept` / :func:`apply_action`
   / :func:`grant_rewards`) emits exactly one well-formed 11-field
   :class:`AuditRecord`; an honest no-op (unknown template, no offered/active/
   completed quest, off-menu action, too-tired action) records NOTHING and
   returns ``ok=False``;
2. the full quest lifecycle (offer → accept → advance → complete → grant) folds
   the engine's tier-capped bundle VERBATIM (capped rewards, tier-III capability);
3. encounter resolution is deterministic (seeded from ``world_seed``);
4. determinism under a fixed seed + injected clock + id factory;
5. the game-neutral ``services/audit.py`` reuse (no coupling to another game's
   seam).
"""

from __future__ import annotations

import inspect
from dataclasses import fields
from datetime import datetime, timezone

import pytest

from services import audit, exploration_workflow as ew
from services.audit import AuditRecord, InMemorySink, Sink

from games.exploration.quest import catalog
from games.exploration.quest import engine as quest_engine
from games.exploration.quest.models import QuestState, RewardTier
from games.shared.encounter.interface import EncounterOutcome
from games.shared.encounter.reference import ALLOWED_KINDS

FIXED_NOW = datetime(2026, 7, 13, 12, 0, 0, tzinfo=timezone.utc)
FIXED_ID = "deadbeefdeadbeefdeadbeefdeadbeef"


def _fixed_id() -> str:
    return FIXED_ID


def _state(**overrides) -> ew.ExplorationState:
    """A fresh session; override any field per test."""
    return ew.ExplorationState(**overrides)


def _active(state: ew.ExplorationState, sink: InMemorySink, template_id: str, tier=RewardTier.I):
    """Drive offer + accept so *state* holds an ACTIVE quest; return the instance."""
    ew.offer(state, template_id, tier, sink=sink, now=FIXED_NOW)
    ew.accept(state, sink=sink, now=FIXED_NOW)
    return state.quest


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

_MUTATIONS = {
    ew.MUTATION_OFFER,
    ew.MUTATION_ACCEPT,
    ew.MUTATION_ACTION,
    ew.MUTATION_GRANT,
}


def _assert_well_formed(rec: AuditRecord) -> None:
    """Assert an AuditRecord carries all 11 fields, populated to spec."""
    assert [f.name for f in fields(rec)] == list(_AUDIT_FIELDS)
    assert isinstance(rec.mutation_id, str) and rec.mutation_id
    assert rec.subsystem == "exploration"
    assert rec.mutation_type in _MUTATIONS
    assert isinstance(rec.target, str) and rec.target
    assert rec.scope == "global"
    assert isinstance(rec.actor_type, str) and rec.actor_type
    assert isinstance(rec.occurred_at, datetime)
    assert rec.prev_value is None or isinstance(rec.prev_value, str)
    assert rec.new_value is None or isinstance(rec.new_value, str)
    assert rec.guild_id is None or isinstance(rec.guild_id, int)
    assert rec.actor_id is None or isinstance(rec.actor_id, int)


# ---------------------------------------------------------------------------
# One well-formed record per state-changing op
# ---------------------------------------------------------------------------
def test_offer_records_exactly_one_well_formed_record():
    state, sink = _state(), InMemorySink()
    res = ew.offer(state, "supply_run", sink=sink, now=FIXED_NOW, mutation_id_factory=_fixed_id)
    assert res.ok
    assert len(sink.records) == 1
    rec = sink.records[0]
    _assert_well_formed(rec)
    assert rec.mutation_type == ew.MUTATION_OFFER
    assert rec.target == "quest:supply_run"
    assert rec.prev_value is None  # first offer of the session
    assert rec.new_value == state.quest.instance_id
    assert rec is res.record
    assert rec.mutation_id == FIXED_ID
    assert rec.occurred_at == FIXED_NOW


def test_accept_records_exactly_one_well_formed_record():
    state, sink = _state(), InMemorySink()
    ew.offer(state, "supply_run", sink=sink, now=FIXED_NOW)
    res = ew.accept(state, sink=sink, now=FIXED_NOW, mutation_id_factory=_fixed_id)
    assert res.ok
    assert len(sink.records) == 2  # offer + accept
    rec = sink.records[-1]
    _assert_well_formed(rec)
    assert rec.mutation_type == ew.MUTATION_ACCEPT
    assert rec.prev_value == QuestState.OFFERED.value
    assert rec.new_value == QuestState.ACTIVE.value


def test_apply_action_records_exactly_one_well_formed_record():
    state, sink = _state(), InMemorySink()
    _active(state, sink, "supply_run")
    before = len(sink.records)
    res = ew.apply_action(state, "deliver_crates", sink=sink, now=FIXED_NOW, mutation_id_factory=_fixed_id)
    assert res.ok
    assert len(sink.records) == before + 1
    rec = sink.records[-1]
    _assert_well_formed(rec)
    assert rec.mutation_type == ew.MUTATION_ACTION
    assert rec.target == "objective:supply_run:deliver_crates"
    assert rec.prev_value == "0/3"
    assert rec.new_value == "1/3"


def test_grant_records_exactly_one_well_formed_record():
    state, sink = _state(), InMemorySink()
    _active(state, sink, "safe_passage")
    ew.apply_action(state, "escort_traveler", sink=sink, now=FIXED_NOW)
    before = len(sink.records)
    res = ew.grant_rewards(state, sink=sink, now=FIXED_NOW, mutation_id_factory=_fixed_id)
    assert res.ok
    assert len(sink.records) == before + 1
    rec = sink.records[-1]
    _assert_well_formed(rec)
    assert rec.mutation_type == ew.MUTATION_GRANT
    assert rec.target.startswith("reward:")
    assert rec.prev_value == "g0/x0/c0"


# ---------------------------------------------------------------------------
# No-ops record NOTHING (honest semantics — no clamp, no silent write)
# ---------------------------------------------------------------------------
def test_offer_unknown_template_is_a_noop_and_records_nothing():
    state, sink = _state(), InMemorySink()
    res = ew.offer(state, "not_a_quest", sink=sink, now=FIXED_NOW)
    assert res.ok is False
    assert sink.records == []
    assert state.quest is None


def test_accept_with_no_offered_quest_is_a_noop():
    state, sink = _state(), InMemorySink()
    res = ew.accept(state, sink=sink, now=FIXED_NOW)
    assert res.ok is False
    assert sink.records == []


def test_apply_action_with_no_active_quest_is_a_noop():
    state, sink = _state(), InMemorySink()
    res = ew.apply_action(state, "deliver_crates", sink=sink, now=FIXED_NOW)
    assert res.ok is False
    assert sink.records == []


def test_apply_action_off_the_bounded_menu_is_a_noop_no_clamp():
    """An off-menu action records nothing and never silently substitutes another."""
    state, sink = _state(), InMemorySink()
    _active(state, sink, "supply_run")
    before = len(sink.records)
    res = ew.apply_action(state, "defeat_wolves", sink=sink, now=FIXED_NOW)  # wrong quest's objective
    assert res.ok is False
    assert len(sink.records) == before  # nothing recorded
    # progress untouched
    assert state.quest.progress[0].current == 0


def test_too_tired_action_is_a_noop_and_records_nothing():
    """The survival energy gate: energy < cost is a no-op (mirrors fishing)."""
    state, sink = _state(energy=0), InMemorySink()
    _active(state, sink, "supply_run")
    before = len(sink.records)
    res = ew.apply_action(state, "deliver_crates", sink=sink, now=FIXED_NOW)
    assert res.ok is False
    assert "too tired" in res.message
    assert len(sink.records) == before
    assert state.energy == 0


def test_grant_with_no_completed_quest_is_a_noop():
    state, sink = _state(), InMemorySink()
    _active(state, sink, "supply_run")  # active, not completed
    before = len(sink.records)
    res = ew.grant_rewards(state, sink=sink, now=FIXED_NOW)
    assert res.ok is False
    assert len(sink.records) == before


# ---------------------------------------------------------------------------
# Full lifecycle — offer → accept → advance → complete → grant, capped rewards
# ---------------------------------------------------------------------------
def test_full_lifecycle_completes_and_banks_capped_reward():
    state, sink = _state(world_seed=7), InMemorySink()
    instance = _active(state, sink, "cull_the_pack", RewardTier.II)
    required = instance.progress[0].required
    for _ in range(required):
        res = ew.apply_action(state, "defeat_wolves", sink=sink, now=FIXED_NOW)
        assert res.ok
    assert state.quest.state is QuestState.COMPLETED
    grant = ew.grant_rewards(state, sink=sink, now=FIXED_NOW)
    assert grant.ok
    # The banked bundle is EXACTLY the engine's tier cap — no re-derivation.
    assert grant.reward == catalog.TIER_CAPS[RewardTier.II]
    assert state.ledger.currency == catalog.TIER_CAPS[RewardTier.II].currency
    assert state.ledger.quests_completed == 1
    assert state.quest is None  # retired so a fresh quest can be offered


def test_reward_never_exceeds_global_max():
    state, sink = _state(), InMemorySink()
    _active(state, sink, "cull_the_pack", RewardTier.III)
    for _ in range(5):
        ew.apply_action(state, "defeat_wolves", sink=sink, now=FIXED_NOW)
    grant = ew.grant_rewards(state, sink=sink, now=FIXED_NOW)
    gm = catalog.GLOBAL_MAX
    assert grant.reward.global_xp <= gm.global_xp
    assert grant.reward.game_xp <= gm.game_xp
    assert grant.reward.currency <= gm.currency


def test_tier_three_grants_the_prestige_capability_play_only():
    state, sink = _state(), InMemorySink()
    _active(state, sink, "whispering_ruins", RewardTier.III)
    for _ in range(4):
        ew.apply_action(state, "find_clues", sink=sink, now=FIXED_NOW)
    grant = ew.grant_rewards(state, sink=sink, now=FIXED_NOW)
    template = catalog.get("whispering_ruins")
    assert grant.reward.capability == template.prestige_capability
    assert state.ledger.capabilities == (template.prestige_capability,)


def test_tier_one_and_two_grant_no_capability():
    for tier in (RewardTier.I, RewardTier.II):
        state, sink = _state(), InMemorySink()
        _active(state, sink, "supply_run", tier)
        for _ in range(3):
            ew.apply_action(state, "deliver_crates", sink=sink, now=FIXED_NOW)
        grant = ew.grant_rewards(state, sink=sink, now=FIXED_NOW)
        assert grant.reward.capability is None


def test_two_objective_quest_needs_both_actions_to_complete():
    """missing_scout has two objectives; the quest completes only after both."""
    state, sink = _state(), InMemorySink()
    _active(state, sink, "missing_scout")
    r1 = ew.apply_action(state, "reach_cavern", sink=sink, now=FIXED_NOW)
    assert r1.ok and not r1.completed  # one objective done, quest not yet complete
    r2 = ew.apply_action(state, "free_captive", sink=sink, now=FIXED_NOW)
    assert r2.completed
    assert state.quest.state is QuestState.COMPLETED


def test_ledger_accumulates_across_multiple_quests():
    state, sink = _state(), InMemorySink()
    for template, action, n in (("supply_run", "deliver_crates", 3), ("whispering_ruins", "find_clues", 4)):
        _active(state, sink, template, RewardTier.I)
        for _ in range(n):
            ew.apply_action(state, action, sink=sink, now=FIXED_NOW)
        ew.grant_rewards(state, sink=sink, now=FIXED_NOW)
    cap = catalog.TIER_CAPS[RewardTier.I]
    assert state.ledger.quests_completed == 2
    assert state.ledger.currency == cap.currency * 2


# ---------------------------------------------------------------------------
# Survival energy axis — cost is spent per action, VERBATIM from the tunables
# ---------------------------------------------------------------------------
def test_energy_starts_at_difficulty_cap_and_debits_the_tunable_cost():
    from games.exploration.survival.difficulty import Difficulty, TUNABLES

    state, sink = _state(difficulty=Difficulty.MEDIUM), InMemorySink()
    tun = TUNABLES[Difficulty.MEDIUM]
    assert state.energy == tun.max_energy  # seeded from the shipped bar cap
    _active(state, sink, "supply_run")
    ew.apply_action(state, "deliver_crates", sink=sink, now=FIXED_NOW)
    assert state.energy == tun.max_energy - tun.cost


# ---------------------------------------------------------------------------
# Encounter resolution — deterministic, an allowed kind, surfaced on the result
# ---------------------------------------------------------------------------
def test_action_resolves_an_encounter_of_an_allowed_kind():
    state, sink = _state(world_seed=3), InMemorySink()
    _active(state, sink, "supply_run")
    res = ew.apply_action(state, "deliver_crates", sink=sink, now=FIXED_NOW)
    assert isinstance(res.encounter, EncounterOutcome)
    assert res.encounter.kind in ALLOWED_KINDS
    assert state.last_encounter is res.encounter


def test_encounter_resolution_is_deterministic_across_identical_sessions():
    def run_first_action_encounter(seed: int) -> EncounterOutcome:
        state, sink = _state(world_seed=seed), InMemorySink()
        _active(state, sink, "supply_run")
        return ew.apply_action(state, "deliver_crates", sink=sink, now=FIXED_NOW).encounter

    a = run_first_action_encounter(99)
    b = run_first_action_encounter(99)
    assert a == b
    # A different world seed yields a (generally) different, still-deterministic id.
    c = run_first_action_encounter(100)
    assert isinstance(c, EncounterOutcome)


# ---------------------------------------------------------------------------
# Determinism of the seam itself (records + rewards)
# ---------------------------------------------------------------------------
def test_seam_is_deterministic_with_injected_clock_and_id():
    def run() -> tuple[list[AuditRecord], object]:
        state, sink = _state(world_seed=11), InMemorySink()
        ew.offer(state, "cull_the_pack", RewardTier.III, sink=sink, now=FIXED_NOW, mutation_id_factory=_fixed_id)
        ew.accept(state, sink=sink, now=FIXED_NOW, mutation_id_factory=_fixed_id)
        for _ in range(5):
            ew.apply_action(state, "defeat_wolves", sink=sink, now=FIXED_NOW, mutation_id_factory=_fixed_id)
        grant = ew.grant_rewards(state, sink=sink, now=FIXED_NOW, mutation_id_factory=_fixed_id)
        return sink.records, grant.reward

    ra, reward_a = run()
    rb, reward_b = run()
    assert reward_a == reward_b
    assert ra == rb  # byte-identical audit trail


def test_default_clock_and_id_are_used_when_not_injected():
    state, sink = _state(), InMemorySink()
    before = datetime.now(timezone.utc)
    res = ew.offer(state, "supply_run", sink=sink)
    after = datetime.now(timezone.utc)
    assert before <= res.record.occurred_at <= after
    assert len(res.record.mutation_id) == 32  # uuid4().hex default


def test_distinct_mutation_ids_across_ops_by_default():
    state, sink = _state(), InMemorySink()
    ew.offer(state, "supply_run", sink=sink)
    ew.accept(state, sink=sink)
    assert sink.records[0].mutation_id != sink.records[1].mutation_id


# ---------------------------------------------------------------------------
# Result / bounded-menu shape
# ---------------------------------------------------------------------------
def test_result_is_frozen():
    res = ew.offer(_state(), "supply_run", sink=InMemorySink(), now=FIXED_NOW)
    with pytest.raises(Exception):
        res.ok = False  # frozen


def test_quest_menu_is_the_catalog_menu_verbatim():
    assert ew.quest_menu() == catalog.menu()


def test_pending_actions_are_the_active_quests_objective_keys():
    state, sink = _state(), InMemorySink()
    instance = _active(state, sink, "missing_scout")
    assert ew.pending_actions(instance) == ("reach_cavern", "free_captive")
    # After completing one objective it drops off the bounded menu.
    ew.apply_action(state, "reach_cavern", sink=sink, now=FIXED_NOW)
    assert ew.pending_actions(state.quest) == ("free_captive",)


def test_pending_actions_empty_when_no_active_quest():
    assert ew.pending_actions(None) == ()
    state, sink = _state(), InMemorySink()
    ew.offer(state, "supply_run", sink=sink)  # only OFFERED, not ACTIVE
    assert ew.pending_actions(state.quest) == ()


# ---------------------------------------------------------------------------
# The game-neutral services/audit.py reuse (no cross-game coupling)
# ---------------------------------------------------------------------------
def test_audit_module_exposes_neutral_types_and_seam_reexports_them():
    assert set(audit.__all__) == {"AuditRecord", "Sink", "InMemorySink"}
    assert ew.AuditRecord is AuditRecord
    assert ew.Sink is Sink
    assert ew.InMemorySink is InMemorySink


def test_seam_does_not_import_another_games_workflow():
    """Reuse is via the neutral audit types — never another game's seam."""
    src = inspect.getsource(ew)
    assert "from services.audit import" in src
    for other in ("mining_workflow", "fishing_workflow", "dnd_workflow"):
        assert f"import {other}" not in src
        assert f"from services.{other}" not in src
        assert f"services.{other}" not in ew.__dict__


def test_inmemory_sink_satisfies_the_sink_protocol():
    sink = InMemorySink()
    assert isinstance(sink, Sink)  # runtime_checkable Protocol
    assert sink.records == []


def test_engine_grant_rewards_raises_on_incomplete_but_seam_guards_it():
    """The engine RAISES on an incomplete grant; the seam guards so it never does."""
    from games.exploration.quest.models import QuestStateError

    state, sink = _state(), InMemorySink()
    instance = _active(state, sink, "supply_run")
    with pytest.raises(QuestStateError):
        quest_engine.grant_rewards(instance)  # engine's own guard
    # The seam turns that into an honest no-op instead of raising.
    res = ew.grant_rewards(state, sink=sink, now=FIXED_NOW)
    assert res.ok is False
