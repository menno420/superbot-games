"""Tests for the standalone fishing CLI (``games/fishing/cli.py``).

Drives scripted, TTY-free sessions through :func:`games.fishing.cli.run_commands`
with an injected :class:`~services.audit.InMemorySink`, asserting that the loop
drives the REAL audited seam (``services/fishing_workflow.py``): every real cast
records exactly one audit row, a too-tired cast is an honest no-op that records
nothing and never crashes, the haul accumulates as fish are landed, and the
navigation verbs (``spot`` / ``spots``) are discoverable and fail gracefully on a
bad id. Casts are made deterministic with an injected ``random.Random`` so the
records/haul counts are exact — no balance number is asserted here (those live in
the core/seam tests), only the CLI's orchestration over the seam.
"""

from __future__ import annotations

import random
from datetime import datetime, timezone

from games.fishing.cli import (
    help_lines,
    new_state,
    run_commands,
    spots_lines,
    status_lines,
    step,
)
from games.fishing.core import spots as spot_table
from games.mining.core import energy
from services import fishing_workflow as fw
from services.audit import InMemorySink

FIXED_NOW = datetime(2026, 7, 13, 12, 0, 0, tzinfo=timezone.utc)


def _fresh(**overrides) -> fw.FishingState:
    """A CLI fresh-player state with optional field overrides for a test."""
    state = new_state()
    for key, value in overrides.items():
        setattr(state, key, value)
    return state


# ---------------------------------------------------------------------------
# The example scripted session (task spec) — runs clean, records what it should
# ---------------------------------------------------------------------------
def test_scripted_session_runs_without_raising() -> None:
    sink = InMemorySink()
    result = run_commands(
        ["status", "spots", "spot deep_water", "cast", "cast", "cast", "haul", "help", "quit"],
        sink=sink,
        state=_fresh(),
        now=FIXED_NOW,
        rng=random.Random(1),
    )
    # Three real casts commit; each records exactly one audit row.
    assert result.casts_made == 3
    assert result.ok_casts == 3
    assert len(sink.records) == 3


def test_sink_records_one_row_per_committed_cast() -> None:
    """The seam records exactly one row per committed cast — the CLI must not
    double-count or drop any."""
    result = run_commands(
        ["cast", "cast", "cast", "quit"],
        state=_fresh(),
        now=FIXED_NOW,
        rng=random.Random(4),
    )
    assert result.ok_casts == 3
    assert len(result.sink.records) == result.ok_casts


# ---------------------------------------------------------------------------
# The too-tired cast — honest no-op, no crash, no audit row
# ---------------------------------------------------------------------------
def test_too_tired_cast_records_nothing() -> None:
    sink = InMemorySink()
    # Energy below the seam's CAST_COST → the core returns its honest 😴 no-bite,
    # the seam records nothing, and the CLI must not crash.
    result = run_commands(
        ["cast", "quit"],
        sink=sink,
        state=_fresh(energy=1),
        now=FIXED_NOW,
        rng=random.Random(1),
    )
    assert result.casts_made == 1  # the player DID issue a cast
    assert result.ok_casts == 0  # but nothing committed
    assert len(sink.records) == 0
    assert "Too tired" in result.text
    assert result.state.energy == 1  # energy untouched


# ---------------------------------------------------------------------------
# Haul accumulates as fish are landed
# ---------------------------------------------------------------------------
def test_haul_accumulates_across_casts() -> None:
    result = run_commands(
        ["spot deep_water", "cast", "cast", "cast", "cast", "quit"],
        state=_fresh(),
        now=FIXED_NOW,
        rng=random.Random(1),
    )
    # At least one of the four casts lands a fish, so the haul is non-empty and
    # the summary reflects it.
    assert sum(result.state.haul.values()) > 0
    assert "fish caught:" in result.text


def test_energy_debits_only_on_real_casts() -> None:
    result = run_commands(
        ["cast", "cast", "quit"],
        state=_fresh(),
        now=FIXED_NOW,
        rng=random.Random(2),
    )
    # Two real casts each spend the seam's CAST_COST verbatim (from the outcome).
    spent = energy.MAX_ENERGY - result.state.energy
    assert spent == result.ok_casts * fw.catch_core.CAST_COST


# ---------------------------------------------------------------------------
# Spot navigation — switch, list, and graceful handling of a bad id
# ---------------------------------------------------------------------------
def test_spot_switch_changes_current_spot() -> None:
    result = run_commands(["spot deep_water", "quit"], state=_fresh(), now=FIXED_NOW)
    assert result.state.spot_id == "deep_water"
    assert "Deep Water" in result.text


def test_invalid_spot_is_handled_gracefully() -> None:
    sink = InMemorySink()
    result = run_commands(
        ["spot nonexistent", "quit"],
        sink=sink,
        state=_fresh(),
        now=FIXED_NOW,
    )
    # No crash, no switch (stays at the starter spot), and the valid ids are hinted.
    assert result.state.spot_id == "dock"
    assert "Unknown spot" in result.text
    assert len(sink.records) == 0


def test_spots_lists_every_valid_id() -> None:
    text = "\n".join(spots_lines())
    for spot_id in spot_table.spot_ids():
        assert spot_id in text


# ---------------------------------------------------------------------------
# REPL ergonomics — help, unknown, empty, quit summary
# ---------------------------------------------------------------------------
def test_help_lists_every_command() -> None:
    text = "\n".join(help_lines())
    for verb in ("cast", "spot", "spots", "status", "help", "quit"):
        assert verb in text


def test_unknown_command_shows_help_and_does_not_crash() -> None:
    result = run_commands(["frobnicate", "quit"], state=_fresh(), now=FIXED_NOW)
    assert "Unknown command" in result.text
    assert result.ok_casts == 0


def test_empty_line_is_a_noop() -> None:
    out = step(_fresh(), InMemorySink(), "   ", now=FIXED_NOW)
    assert out.lines == []
    assert not out.is_cast and not out.quit


def test_quit_prints_session_summary_and_stops_early() -> None:
    result = run_commands(["quit", "cast"], state=_fresh(), now=FIXED_NOW, rng=random.Random(1))
    assert "Session summary" in result.text
    # The 'cast' after 'quit' must never run.
    assert result.casts_made == 0
    assert len(result.sink.records) == 0


# ---------------------------------------------------------------------------
# The fresh-player status header + the seam audit record reflect REAL defaults
# ---------------------------------------------------------------------------
def test_status_header_reflects_core_defaults() -> None:
    text = "\n".join(status_lines(_fresh()))
    assert f"{energy.MAX_ENERGY}/{energy.MAX_ENERGY}" in text
    assert "The Old Dock" in text
    assert "nothing yet" in text


def test_cast_emits_a_fishing_subsystem_audit_record() -> None:
    result = run_commands(["cast", "quit"], state=_fresh(), now=FIXED_NOW, rng=random.Random(1))
    assert result.ok_casts == 1
    record = result.sink.records[0]
    assert record.subsystem == "fishing"
    assert record.mutation_type == fw.MUTATION_CAST
