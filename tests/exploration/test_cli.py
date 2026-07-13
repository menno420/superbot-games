"""Tests for the standalone Exploration CLI (``games/exploration/cli.py``).

Drives scripted, TTY-free sessions through
:func:`games.exploration.cli.run_commands` with an injected
:class:`~services.audit.InMemorySink`, asserting the loop drives the REAL audited
seam (``services/exploration_workflow.py``): ``offer`` + ``accept`` take a bounded
quest, ``act`` advances an objective and records one audit row (and banks the
reward automatically on completion), an off-menu quest / action is surfaced
gracefully by the seam (no crash, nothing recorded), and the read-only verbs
(``quests`` / ``status`` / ``help``) plus the quit summary work. No balance number
is asserted here (those live in the seam/core tests) — only the CLI's
orchestration over the seam. Everything is deterministic (the engine + resolver
seed from the state's ``world_seed``), so the record counts are exact.
"""

from __future__ import annotations

from datetime import datetime, timezone

from games.exploration.cli import (
    help_lines,
    new_state,
    quests_lines,
    run_commands,
    status_lines,
    step,
)
from services import exploration_workflow as ew
from services.audit import InMemorySink

FIXED_NOW = datetime(2026, 7, 13, 12, 0, 0, tzinfo=timezone.utc)


def _fresh(**overrides) -> ew.ExplorationState:
    """A CLI fresh-player state with optional field overrides for a test."""
    state = new_state()
    for key, value in overrides.items():
        setattr(state, key, value)
    return state


# ---------------------------------------------------------------------------
# A full scripted arc — offer → accept → act → complete, one row per op
# ---------------------------------------------------------------------------
def test_scripted_arc_completes_a_quest_and_records_each_op() -> None:
    sink = InMemorySink()
    result = run_commands(
        ["quests", "offer supply_run", "accept", "act deliver_crates",
         "act deliver_crates", "act deliver_crates", "status", "quit"],
        sink=sink,
        state=_fresh(),
        now=FIXED_NOW,
    )
    assert result.actions_taken == 3
    assert result.quests_completed == 1
    # offer + accept + 3 actions + 1 auto-grant = 6 audit rows.
    assert len(sink.records) == 6
    assert result.state.ledger.quests_completed == 1


def test_every_op_emits_an_exploration_subsystem_record() -> None:
    sink = InMemorySink()
    run_commands(
        ["offer safe_passage", "accept", "act escort_traveler", "quit"],
        sink=sink,
        state=_fresh(),
        now=FIXED_NOW,
    )
    assert all(r.subsystem == "exploration" for r in sink.records)
    mutations = {r.mutation_type for r in sink.records}
    assert ew.MUTATION_OFFER in mutations
    assert ew.MUTATION_ACCEPT in mutations
    assert ew.MUTATION_ACTION in mutations
    assert ew.MUTATION_GRANT in mutations  # auto-banked on completion


# ---------------------------------------------------------------------------
# Reward accumulates + shows in the summary
# ---------------------------------------------------------------------------
def test_completed_quest_banks_reward_shown_in_summary() -> None:
    result = run_commands(
        ["offer whispering_ruins III", "accept",
         "act find_clues", "act find_clues", "act find_clues", "act find_clues", "quit"],
        state=_fresh(),
        now=FIXED_NOW,
    )
    assert result.state.ledger.currency > 0
    assert "rewards banked:" in result.text
    assert "🏁" in result.text  # the completion / bank line


# ---------------------------------------------------------------------------
# Off-menu quest / action handled gracefully (no crash, nothing recorded)
# ---------------------------------------------------------------------------
def test_offer_unknown_quest_is_graceful_and_records_nothing() -> None:
    sink = InMemorySink()
    result = run_commands(["offer zorp", "quit"], sink=sink, state=_fresh(), now=FIXED_NOW)
    assert "unknown quest" in result.text
    assert len(sink.records) == 0


def test_off_menu_action_is_graceful_and_records_nothing() -> None:
    sink = InMemorySink()
    result = run_commands(
        ["offer supply_run", "accept", "act defeat_wolves", "quit"],  # wrong quest's objective
        sink=sink,
        state=_fresh(),
        now=FIXED_NOW,
    )
    assert "not a valid action" in result.text
    assert result.actions_taken == 0
    # offer + accept recorded; the invalid act recorded nothing.
    assert len(sink.records) == 2


def test_too_tired_action_is_graceful() -> None:
    sink = InMemorySink()
    result = run_commands(
        ["offer supply_run", "accept", "act deliver_crates", "quit"],
        sink=sink,
        state=_fresh(energy=0),
        now=FIXED_NOW,
    )
    assert "too tired" in result.text
    assert result.actions_taken == 0


def test_act_before_accept_is_graceful() -> None:
    result = run_commands(["act deliver_crates", "quit"], state=_fresh(), now=FIXED_NOW)
    assert "no active quest" in result.text
    assert result.actions_taken == 0


def test_unknown_command_shows_help_and_changes_nothing() -> None:
    sink = InMemorySink()
    result = run_commands(["flibbertigibbet", "quit"], sink=sink, state=_fresh(), now=FIXED_NOW)
    assert "Unknown command" in result.text
    assert len(sink.records) == 0


# ---------------------------------------------------------------------------
# Read-only verbs — quests, status, help
# ---------------------------------------------------------------------------
def test_quests_lists_the_bounded_catalog_menu() -> None:
    text = "\n".join(quests_lines())
    for template_id in ("supply_run", "safe_passage", "cull_the_pack", "missing_scout", "whispering_ruins"):
        assert template_id in text


def test_status_shows_quest_energy_and_reward_totals() -> None:
    text = "\n".join(status_lines(_fresh(), InMemorySink()))
    assert "difficulty:" in text
    assert "energy:" in text
    assert "banked:" in text
    assert "audited:" in text


def test_status_shows_active_quest_progress_and_actions() -> None:
    sink = InMemorySink()
    state = _fresh()
    run_commands(["offer supply_run", "accept"], sink=sink, state=state, now=FIXED_NOW)
    text = "\n".join(status_lines(state, sink))
    assert "supply_run" in text
    assert "deliver_crates" in text
    assert "actions:" in text


def test_help_lists_every_command() -> None:
    text = "\n".join(help_lines())
    for verb in ("quests", "offer", "accept", "act", "status", "help", "quit"):
        assert verb in text


def test_empty_line_is_a_noop() -> None:
    out = step(_fresh(), InMemorySink(), "   ", now=FIXED_NOW)
    assert out.lines == []
    assert not out.acted and not out.quit


def test_quit_prints_summary_and_stops_early() -> None:
    sink = InMemorySink()
    result = run_commands(["quit", "offer supply_run"], sink=sink, state=_fresh(), now=FIXED_NOW)
    assert "Session summary" in result.text
    assert len(sink.records) == 0  # the offer after quit never ran


# ---------------------------------------------------------------------------
# Tier parsing on offer
# ---------------------------------------------------------------------------
def test_offer_rejects_an_unknown_tier_gracefully() -> None:
    sink = InMemorySink()
    result = run_commands(["offer supply_run IV", "quit"], sink=sink, state=_fresh(), now=FIXED_NOW)
    assert "Unknown tier" in result.text
    assert len(sink.records) == 0
