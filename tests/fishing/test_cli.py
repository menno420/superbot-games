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
from games.fishing.core import economy
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
    for verb in ("cast", "sell", "spot", "spots", "status", "help", "quit"):
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


# ---------------------------------------------------------------------------
# The V043 sell command — routes through the seam's audited sell(), no CLI math
# ---------------------------------------------------------------------------
def test_sell_routes_through_seam_and_credits_coins() -> None:
    sink = InMemorySink()
    result = run_commands(
        ["sell bass 1", "quit"],
        sink=sink,
        state=_fresh(haul={"bass": 2}),
        now=FIXED_NOW,
    )
    # The credited amount is the seam's sim-pinned value — the CLI adds no math.
    assert result.state.coins == economy.sell_value("bass")
    assert result.state.haul["bass"] == 1  # the sold fish is CONSUMED (sell-OR-cook)
    assert len(sink.records) == 1
    record = sink.records[0]
    assert record.subsystem == "fishing"
    assert record.mutation_type == fw.MUTATION_SELL
    assert record.target == "coins"


def test_sell_default_qty_sells_all_held() -> None:
    result = run_commands(
        ["sell minnow", "quit"],
        state=_fresh(haul={"minnow": 3}),
        now=FIXED_NOW,
    )
    assert result.state.coins == 3 * economy.sell_value("minnow")
    assert result.state.haul["minnow"] == 0
    assert len(result.sink.records) == 1  # one committed sell → exactly one row


def test_sell_unknown_species_is_honest_noop() -> None:
    sink = InMemorySink()
    result = run_commands(
        ["sell kraken", "quit"],
        sink=sink,
        state=_fresh(haul={"bass": 1}),
        now=FIXED_NOW,
    )
    assert result.state.coins == 0
    assert result.state.haul == {"bass": 1}
    assert len(sink.records) == 0  # a no-op sell records NOTHING (D2)
    assert "cannot be sold" in result.text


def test_sell_more_than_held_records_nothing() -> None:
    sink = InMemorySink()
    result = run_commands(
        ["sell pike 5", "quit"],
        sink=sink,
        state=_fresh(haul={"pike": 1}),
        now=FIXED_NOW,
    )
    assert result.state.coins == 0
    assert result.state.haul == {"pike": 1}
    assert len(sink.records) == 0
    assert "only have" in result.text


def test_sell_without_args_shows_usage() -> None:
    sink = InMemorySink()
    result = run_commands(["sell", "quit"], sink=sink, state=_fresh(), now=FIXED_NOW)
    assert "Usage: sell" in result.text
    assert len(sink.records) == 0


def test_sell_with_non_numeric_qty_is_graceful() -> None:
    sink = InMemorySink()
    result = run_commands(
        ["sell bass lots", "quit"],
        sink=sink,
        state=_fresh(haul={"bass": 2}),
        now=FIXED_NOW,
    )
    assert "Quantity must be a number" in result.text
    assert result.state.haul == {"bass": 2}
    assert len(sink.records) == 0


def test_sell_with_float_qty_is_graceful() -> None:
    # A float-shaped qty fails the CLI-boundary int() parse (int("1.5") raises)
    # exactly like a word — an honest "must be a number" no-op, NOT a truncation
    # to 1: nothing is consumed and no audit row is recorded.
    sink = InMemorySink()
    result = run_commands(
        ["sell bass 1.5", "quit"],
        sink=sink,
        state=_fresh(haul={"bass": 2}),
        now=FIXED_NOW,
    )
    assert "Quantity must be a number" in result.text
    assert "'1.5'" in result.text
    assert result.state.coins == 0
    assert result.state.haul == {"bass": 2}
    assert len(sink.records) == 0


def test_sell_with_negative_qty_is_honest_noop() -> None:
    # A negative qty PARSES as an int at the CLI boundary but is rejected one
    # layer deeper by the audited seam's non-positive guard — a DIFFERENT path
    # from the non-numeric case above (the CLI forwards it; the seam no-ops).
    sink = InMemorySink()
    result = run_commands(
        ["sell bass -2", "quit"],
        sink=sink,
        state=_fresh(haul={"bass": 2}),
        now=FIXED_NOW,
    )
    assert "Quantity must be positive" in result.text
    assert result.state.coins == 0
    assert result.state.haul == {"bass": 2}
    assert len(sink.records) == 0  # a rejected sell records NOTHING (D2)


def test_sell_multiword_display_name_resolves_to_id_and_commits() -> None:
    # Decision #5 owner-default: a multi-word DISPLAY name ("Legendary Carp")
    # now resolves to its neutral id ``legend_carp`` (games/fishing/core/species.py)
    # via ``species.resolve`` and commits, instead of tokenising to species
    # ``legendary`` + a bad qty ``Carp`` and no-oping. The trailing integer is the
    # quantity; the words before it are the (multi-word) species name.
    sink = InMemorySink()
    result = run_commands(
        ["sell Legendary Carp 2", "quit"],
        sink=sink,
        state=_fresh(haul={"legend_carp": 3}),
        now=FIXED_NOW,
    )
    assert result.state.coins == 2 * economy.sell_value("legend_carp")
    assert result.state.haul["legend_carp"] == 1  # 2 of 3 consumed
    assert len(sink.records) == 1  # one committed sell → exactly one row


def test_sell_multiword_display_name_is_case_insensitive() -> None:
    # The display-name resolver is case-insensitive: the fully lower-cased
    # display name resolves to the same id as the canonical-cased form.
    result = run_commands(
        ["sell legendary carp", "quit"],  # no qty → sell all held
        state=_fresh(haul={"legend_carp": 2}),
        now=FIXED_NOW,
    )
    assert result.state.coins == 2 * economy.sell_value("legend_carp")
    assert result.state.haul["legend_carp"] == 0
    assert len(result.sink.records) == 1


def test_sell_legend_carp_by_neutral_id_still_commits() -> None:
    # Id-based resolution is preserved unchanged: the SAME species still sells
    # correctly when addressed by its neutral single-token id (id match wins in
    # ``resolve``, so the id path is never shadowed by display-name matching).
    result = run_commands(
        ["sell legend_carp 2", "quit"],
        state=_fresh(haul={"legend_carp": 3}),
        now=FIXED_NOW,
    )
    assert result.state.coins == 2 * economy.sell_value("legend_carp")
    assert result.state.haul["legend_carp"] == 1  # 2 of 3 consumed
    assert len(result.sink.records) == 1  # one committed sell → exactly one row


def test_sell_unknown_multiword_name_is_honest_noop() -> None:
    # A multi-word phrase that matches no id AND no display name still honestly
    # no-ops (unknown species), NOT a false "Quantity must be a number" — the
    # trailing token is only flagged as a bad quantity when the prefix already
    # names a species (mirrors the mining CLI's catalog-aware disambiguation).
    sink = InMemorySink()
    result = run_commands(
        ["sell Giant Kraken", "quit"],
        sink=sink,
        state=_fresh(haul={"bass": 1}),
        now=FIXED_NOW,
    )
    assert "Quantity must be a number" not in result.text
    assert "cannot be sold" in result.text
    assert result.state.coins == 0
    assert result.state.haul == {"bass": 1}  # nothing consumed
    assert len(sink.records) == 0


# ---------------------------------------------------------------------------
# V043 display — coins / level in the status header + summary, milestones on cast
# ---------------------------------------------------------------------------
def test_status_shows_coins_and_level_readout() -> None:
    # cumulative_xp_for(2) xp puts the STAT-NEUTRAL readout exactly at L2.
    state = _fresh(coins=42, game_xp=economy.cumulative_xp_for(2))
    text = "\n".join(status_lines(state))
    assert "coins:  42" in text
    assert "L2" in text
    assert f"{economy.cumulative_xp_for(2)} xp" in text


def test_summary_shows_coins_and_level() -> None:
    result = run_commands(
        ["sell bass", "quit"],
        state=_fresh(haul={"bass": 1}),
        now=FIXED_NOW,
    )
    assert f"coins:           {economy.sell_value('bass')}" in result.text
    assert "fishing level:   L1" in result.text


def test_milestone_announced_when_cast_crosses_it() -> None:
    # One xp short of the L10 milestone: the next landed fish (size_rank >= 1)
    # crosses it, and the CLI must announce the seam-surfaced milestone.
    state = _fresh(game_xp=economy.cumulative_xp_for(10) - 1, energy=200)
    result = run_commands(
        ["spot deep_water"] + ["cast"] * 20 + ["quit"],
        state=state,
        now=FIXED_NOW,
        rng=random.Random(1),
    )
    assert result.state.game_xp >= economy.cumulative_xp_for(10)  # a fish landed
    assert "milestone — fishing level 10 reached!" in result.text


def test_xp_line_surfaces_only_on_a_bite() -> None:
    # A bite gains size_rank xp and the cast output shows the +xp readout.
    state = _fresh(game_xp=0, energy=200)
    result = run_commands(
        ["spot deep_water"] + ["cast"] * 20 + ["quit"],
        state=state,
        now=FIXED_NOW,
        rng=random.Random(1),
    )
    assert result.state.game_xp > 0
    assert "xp:     +" in result.text
