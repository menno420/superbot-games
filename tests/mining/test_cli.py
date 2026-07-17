"""Tests for the standalone mining CLI (``games/mining/cli.py``).

Drives scripted, TTY-free sessions through :func:`games.mining.cli.run_commands`
with an injected :class:`~services.audit.InMemorySink`, asserting that the loop
drives the REAL audited seam: state-changing actions record exactly one audit
row each, blocked actions (unaffordable / torch-less descend) yield the seam's
honest message without crashing or recording anything, and coins/inventory move
exactly as the seam's verbatim economy dictates.
"""

from __future__ import annotations

import random
from datetime import datetime, timezone

import pytest

from games.mining.cli import (
    help_lines,
    new_state,
    run_commands,
    status_lines,
    step,
)
from games.mining.core import energy, equipment, market
from services import mining_workflow as mw
from services.audit import InMemorySink

FIXED_NOW = datetime(2026, 7, 13, 12, 0, 0, tzinfo=timezone.utc)


def _fresh(**overrides) -> mw.MiningState:
    """A CLI fresh-player state with optional field overrides for a test."""
    state = new_state(now=FIXED_NOW)
    for key, value in overrides.items():
        setattr(state, key, value)
    return state


# ---------------------------------------------------------------------------
# The example scripted session (task spec) — runs clean, records what it should
# ---------------------------------------------------------------------------
def test_scripted_session_runs_without_raising() -> None:
    sink = InMemorySink()
    result = run_commands(
        ["status", "mine", "mine", "mine", "sell iron", "repair iron pickaxe", "descend", "help", "quit"],
        sink=sink,
        state=_fresh(),
        now=FIXED_NOW,
        rng=random.Random(1),
    )
    # Three mines commit; sell iron (none held), repair (no iron pickaxe) and the
    # torch-less descend are all honest blocks that record nothing.
    assert result.ok_actions == 3
    assert len(sink.records) == 3


def test_sink_records_equal_committed_actions() -> None:
    """The seam records exactly one row per committed action — the CLI must not
    double-count or drop any."""
    result = run_commands(
        ["mine", "mine", "skill mining", "vault", "quit"],
        state=_fresh(),
        now=FIXED_NOW,
        rng=random.Random(4),
    )
    # 2 mines + 1 skill commit; vault is unaffordable (0 coins) and records nothing.
    assert result.ok_actions == 3
    assert len(result.sink.records) == result.ok_actions


# ---------------------------------------------------------------------------
# Economy legs move exactly as the REAL seam dictates
# ---------------------------------------------------------------------------
def test_sell_credits_coins_at_the_core_price() -> None:
    unit = market.sell_price("iron")
    assert unit is not None
    result = run_commands(
        ["sell iron 3", "quit"],
        state=_fresh(inventory={"iron": 5}),
        now=FIXED_NOW,
    )
    assert result.state.coins == unit * 3
    assert result.state.inventory["iron"] == 2
    assert len(result.sink.records) == 1


def test_sell_default_quantity_sells_everything_held() -> None:
    unit = market.sell_price("iron")
    result = run_commands(
        ["sell iron", "quit"],
        state=_fresh(inventory={"iron": 4}),
        now=FIXED_NOW,
    )
    assert result.state.inventory["iron"] == 0
    assert result.state.coins == unit * 4


def test_buy_debits_coins_and_grants_the_item() -> None:
    price = market.buy_price("torch")
    assert price is not None
    result = run_commands(
        ["buy torch", "quit"],
        state=_fresh(coins=price + 5),
        now=FIXED_NOW,
    )
    assert result.state.coins == 5
    assert result.state.inventory.get("torch") == 1


def test_mine_grows_pack_and_wears_the_tool() -> None:
    result = run_commands(
        ["mine", "mine", "quit"],
        state=_fresh(),
        now=FIXED_NOW,
        rng=random.Random(7),
    )
    assert sum(result.state.inventory.values()) > 0
    # Starter pickaxe wears one durability per dig (two digs → 60 - 2).
    assert result.state.durability["pickaxe"] == equipment.max_durability("pickaxe") - 2


# ---------------------------------------------------------------------------
# Blocked actions — honest message, no crash, no audit row
# ---------------------------------------------------------------------------
def test_blocked_descend_yields_the_hint_not_a_crash() -> None:
    sink = InMemorySink()
    result = run_commands(["descend", "quit"], sink=sink, state=_fresh(), now=FIXED_NOW)
    assert "Equip a brighter light" in result.text
    assert result.ok_actions == 0
    assert len(sink.records) == 0


def test_unaffordable_buy_records_nothing() -> None:
    sink = InMemorySink()
    result = run_commands(["buy torch", "quit"], sink=sink, state=_fresh(coins=0), now=FIXED_NOW)
    assert "Not enough coins" in result.text
    assert len(sink.records) == 0
    assert result.state.inventory.get("torch", 0) == 0


def test_sell_more_than_held_is_blocked_and_records_nothing() -> None:
    sink = InMemorySink()
    result = run_commands(["sell iron 99", "quit"], sink=sink, state=_fresh(inventory={"iron": 2}), now=FIXED_NOW)
    assert "only have 2" in result.text
    assert len(sink.records) == 0
    assert result.state.coins == 0


# ---------------------------------------------------------------------------
# A free (no-cost) state-changing action still audits
# ---------------------------------------------------------------------------
def test_skill_allocation_is_a_recorded_action() -> None:
    result = run_commands(["skill mining 2", "quit"], state=_fresh(), now=FIXED_NOW)
    assert result.state.skills.get("mining") == 2
    assert result.ok_actions == 1
    assert len(result.sink.records) == 1


# ---------------------------------------------------------------------------
# Case-insensitive item / branch / structure tokens (regression)
#
# The catalog, inventory, skill-branch and structure keys are all lowercase, so
# a capitalised token a player naturally types must resolve the same as its
# lowercase form — the CLI normalises case at its boundary (mirroring the fishing
# CLI's ``args[0].lower()``). Before the fix, ``sell Iron`` falsely reported
# "0 held", ``buy Torch`` stored a mismatched ``"Torch"`` key, and
# ``skill Mining`` was rejected as "not a skill branch".
# ---------------------------------------------------------------------------
def test_sell_is_case_insensitive_for_the_item_name() -> None:
    unit = market.sell_price("iron")
    assert unit is not None
    result = run_commands(
        ["sell Iron 2", "quit"],
        state=_fresh(inventory={"iron": 5}),
        now=FIXED_NOW,
    )
    # Capitalised name still finds the held iron, sells it and credits coins.
    assert result.state.inventory["iron"] == 3
    assert result.state.coins == unit * 2
    assert len(result.sink.records) == 1


def test_sell_default_quantity_is_case_insensitive() -> None:
    unit = market.sell_price("iron")
    result = run_commands(
        ["sell IRON", "quit"],
        state=_fresh(inventory={"iron": 4}),
        now=FIXED_NOW,
    )
    # The default-qty path also keys on the lowercased name (else it read 0 held).
    assert result.state.inventory["iron"] == 0
    assert result.state.coins == unit * 4


def test_buy_is_case_insensitive_and_stores_the_canonical_key() -> None:
    price = market.buy_price("torch")
    assert price is not None
    result = run_commands(
        ["buy Torch", "quit"],
        state=_fresh(coins=price + 5),
        now=FIXED_NOW,
    )
    assert result.state.coins == 5
    # The bought item lands under the canonical lowercase key, not "Torch".
    assert result.state.inventory.get("torch") == 1
    assert "Torch" not in result.state.inventory


def test_skill_allocation_is_case_insensitive_for_the_branch() -> None:
    result = run_commands(["skill Mining 2", "quit"], state=_fresh(), now=FIXED_NOW)
    assert result.state.skills.get("mining") == 2
    assert result.ok_actions == 1


def test_repair_is_case_insensitive_for_the_item_name() -> None:
    # A worn starter pickaxe repaired via a capitalised name still resolves.
    state = _fresh(coins=1_000)
    state.durability["pickaxe"] = 5
    result = run_commands(["repair Pickaxe", "quit"], state=state, now=FIXED_NOW)
    assert result.state.durability["pickaxe"] == equipment.max_durability("pickaxe")
    assert result.ok_actions == 1


# ---------------------------------------------------------------------------
# REPL ergonomics — help, unknown, empty, quit summary
# ---------------------------------------------------------------------------
def test_help_lists_every_command() -> None:
    text = "\n".join(help_lines())
    for verb in ("mine", "harvest", "sell", "buy", "repair", "descend", "ascend", "build", "vault", "skill"):
        assert verb in text


def test_unknown_command_shows_help_and_does_not_crash() -> None:
    result = run_commands(["frobnicate", "quit"], state=_fresh(), now=FIXED_NOW)
    assert "Unknown command" in result.text
    assert result.ok_actions == 0


def test_empty_line_is_a_noop() -> None:
    out = step(_fresh(), InMemorySink(), "   ", now=FIXED_NOW)
    assert out.lines == []
    assert not out.is_action and not out.quit


def test_quit_prints_session_summary_and_stops_early() -> None:
    result = run_commands(["quit", "mine"], state=_fresh(), now=FIXED_NOW, rng=random.Random(1))
    assert "Session summary" in result.text
    # The 'mine' after 'quit' must never run.
    assert result.ok_actions == 0
    assert len(result.sink.records) == 0


# ---------------------------------------------------------------------------
# The fresh-player status header reflects REAL core defaults (no invented nums)
# ---------------------------------------------------------------------------
def test_status_header_reflects_core_defaults() -> None:
    text = "\n".join(status_lines(_fresh(), now=FIXED_NOW))
    assert "coins:  0" in text
    assert f"{energy.MAX_ENERGY}/{energy.MAX_ENERGY}" in text
    assert "pickaxe" in text
    assert "Surface" in text
