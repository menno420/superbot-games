"""Tests for the standalone D&D CLI (``games/dnd/cli.py``).

Drives scripted, TTY-free sessions through :func:`games.dnd.cli.run_commands`
with an injected :class:`~services.audit.InMemorySink`, asserting that the loop
drives the REAL audited seam (``services/dnd_workflow.py``): a numbered pick
advances the scene and records one audit row, an off-menu pick is clamped by the
resolver to the safe default and handled gracefully (a friendly hint, no crash),
the reward totals accumulate as the escort effect mints, and the read-only verbs
(``look`` / ``status`` / ``help``) plus the quit summary work. No balance number
is asserted here (those live in the seam/core tests) — only the CLI's
orchestration over the seam. Everything is deterministic (the resolver seeds
itself from the state seed), so the records/scene counts are exact.
"""

from __future__ import annotations

from datetime import datetime, timezone

from games.dnd.cli import (
    help_lines,
    new_state,
    run_commands,
    scene_lines,
    status_lines,
    step,
)
from services import dnd_workflow as dw
from services.audit import InMemorySink

FIXED_NOW = datetime(2026, 7, 13, 12, 0, 0, tzinfo=timezone.utc)


def _fresh(**overrides) -> dw.DnDState:
    """A CLI fresh-player state with optional field overrides for a test."""
    state = new_state()
    for key, value in overrides.items():
        setattr(state, key, value)
    return state


# ---------------------------------------------------------------------------
# A full scripted arc — advance through the scenes, one row per choice
# ---------------------------------------------------------------------------
def test_scripted_arc_advances_scenes_and_records_each_choice() -> None:
    sink = InMemorySink()
    # 1 = advance_escort (mint -> gate); 2 = circle_to_treeline (narrate -> watch);
    # 1 = signal_escort (mint -> ended).
    result = run_commands(
        ["look", "1", "2", "1", "status", "quit"],
        sink=sink,
        state=_fresh(),
        now=FIXED_NOW,
    )
    assert result.choices_made == 3
    assert len(sink.records) == 3  # one audit row per choose
    assert result.scenes_visited == ["waystation_road", "waystation_gate", "treeline_watch"]


def test_every_choice_emits_a_dnd_subsystem_record() -> None:
    result = run_commands(["1", "quit"], state=_fresh(), now=FIXED_NOW)
    assert result.choices_made == 1
    rec = result.sink.records[0]
    assert rec.subsystem == "dnd"
    assert rec.mutation_type == dw.MUTATION_CHOOSE


# ---------------------------------------------------------------------------
# Reward accumulates as the escort effect mints
# ---------------------------------------------------------------------------
def test_reward_accumulates_and_shows_in_summary() -> None:
    result = run_commands(
        ["1", "2", "1", "quit"],  # the double-mint arc
        state=_fresh(),
        now=FIXED_NOW,
    )
    # Two escort mints landed, so the totals are non-zero and the summary shows them.
    assert result.state.currency > 0
    assert "total reward:" in result.text
    assert "coins" in result.text


# ---------------------------------------------------------------------------
# Off-menu picks are clamped and handled gracefully (no crash)
# ---------------------------------------------------------------------------
def test_off_menu_pick_is_clamped_with_a_friendly_hint() -> None:
    sink = InMemorySink()
    result = run_commands(
        ["zorp", "quit"],
        sink=sink,
        state=_fresh(),
        now=FIXED_NOW,
    )
    # The resolver clamps to the safe default; the CLI surfaces a hint and the seam
    # still records the clamped decision (the seam's D2 semantics).
    assert "off-menu" in result.text
    assert result.choices_made == 1
    assert len(sink.records) == 1


def test_out_of_range_number_is_treated_as_off_menu() -> None:
    result = run_commands(["9", "quit"], state=_fresh(), now=FIXED_NOW)
    # Only two options surface at the floor width; 9 is off-menu -> clamp, no crash.
    assert "off-menu" in result.text
    assert result.choices_made == 1


def test_concluded_beat_refuses_further_picks_without_farming() -> None:
    """Once a beat ends (a None transition), a further pick is gently refused."""
    sink = InMemorySink()
    # At treeline_watch, signal_escort mints and ends; a second pick must NOT mint.
    result = run_commands(
        ["1", "1", "quit"],
        sink=sink,
        state=_fresh(scene_id="treeline_watch"),
        now=FIXED_NOW,
    )
    assert "concluded" in result.text
    assert len(sink.records) == 1  # only the first (ending) pick recorded


# ---------------------------------------------------------------------------
# Read-only verbs — look, status, help
# ---------------------------------------------------------------------------
def test_look_shows_scene_prose_and_menu() -> None:
    text = "\n".join(scene_lines(_fresh()))
    assert "waystation road" in text
    assert "Press on toward the waystation" in text  # option 1 copy, verbatim


def test_status_shows_scene_and_reward_totals() -> None:
    text = "\n".join(status_lines(_fresh(), InMemorySink()))
    assert "scene:" in text
    assert "reward:" in text
    assert "audited:" in text


def test_help_lists_every_command() -> None:
    text = "\n".join(help_lines())
    for verb in ("look", "status", "help", "quit"):
        assert verb in text


def test_empty_line_is_a_noop() -> None:
    out = step(_fresh(), InMemorySink(), "   ", now=FIXED_NOW)
    assert out.lines == []
    assert not out.is_choice and not out.quit


def test_quit_prints_summary_and_stops_early() -> None:
    result = run_commands(["quit", "1"], state=_fresh(), now=FIXED_NOW)
    assert "Session summary" in result.text
    # The '1' after quit must never run.
    assert result.choices_made == 0
    assert len(result.sink.records) == 0


# ---------------------------------------------------------------------------
# The fresh session opens at the skeleton start scene
# ---------------------------------------------------------------------------
def test_fresh_session_opens_at_the_start_scene() -> None:
    state = _fresh()
    assert state.scene_id == dw.START_SCENE
    text = "\n".join(scene_lines(state))
    assert "1." in text and "2." in text  # exactly the two floor-width options
