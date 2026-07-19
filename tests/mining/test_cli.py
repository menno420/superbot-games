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
from games.mining.core import energy, equipment, market, structures
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
# explore — drives the (previously dead) exploration engine on a live verb
# ---------------------------------------------------------------------------
def test_explore_grows_pack_and_records_the_find() -> None:
    # seed 3 resolves the surface "secret chest" (wood +3): the CLI drives the
    # engine through the seam, grows the pack, and records exactly one audit row.
    sink = InMemorySink()
    result = run_commands(
        ["explore", "quit"],
        sink=sink,
        state=_fresh(),
        now=FIXED_NOW,
        rng=random.Random(3),
    )
    assert "found a secret chest with 3 wood" in result.text
    assert result.state.inventory.get("wood") == 3
    assert result.ok_actions == 1
    assert len(sink.records) == 1
    assert sink.records[0].mutation_type == mw.MUTATION_EXPLORE


def test_explore_found_nothing_is_an_honest_noop() -> None:
    # seed 5 resolves the "got lost" outcome: the CLI prints the engine narration
    # but commits nothing and records no audit row (D2).
    sink = InMemorySink()
    result = run_commands(
        ["explore", "quit"],
        sink=sink,
        state=_fresh(),
        now=FIXED_NOW,
        rng=random.Random(5),
    )
    assert "found nothing" in result.text
    assert result.ok_actions == 0
    assert len(sink.records) == 0


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
# Negative / non-integer quantity — the CLI→seam rejection interaction
#
# The qty-taking verbs (``sell`` / ``build`` / ``skill``) split a trailing
# quantity token off the args with ``_split_item_qty``, whose test is
# ``args[-1].lstrip("-").isdigit()``. That test SPLITS TWO WAYS, and each edge
# must reject honestly (no crash, no state change, no audit row):
#
#  * A leading-minus token (``-3`` / ``-1`` / ``-2``) PASSES the isdigit test
#    (the ``lstrip("-")`` strips the sign), so it parses as a NEGATIVE int and is
#    forwarded to the seam. For ``sell`` / ``skill`` the seam's own non-positive
#    guard rejects it one layer deeper (the CLI→seam interaction the fishing
#    slice, PR #161, pinned for ``sell bass -2``). ``build`` is DIFFERENT: its
#    seam now treats the trailing level as advisory and derives the authoritative
#    current level from state (so a typed level can never force a downgrade,
#    tier-skip, or invalid-level no-op), so ``build forge -1`` simply ignores the
#    ``-1`` and builds the forge honestly from its real state level.
#  * A non-numeric token (``abc`` / ``xyz`` / ``foo``) FAILS the isdigit test, so
#    ``_split_item_qty`` folds it into the (multi-word) NAME and returns qty
#    ``None``. Decision #6 added a `sell`-path diagnostic (PR #172): when the
#    tokens BEFORE the trailing non-int token already name a known catalogued item
#    (``items.lookup``) and the whole phrase does not, the CLI now flags the bad
#    quantity ("Quantity must be a number, got X") — mirroring the fishing CLI —
#    rather than folding it into the name. A genuine multi-word item name (e.g.
#    ``iron pickaxe``) still resolves as the item (no false quantity error), and a
#    truly unknown name still reports "cannot be sold". The ``build`` / ``skill``
#    verbs are unchanged — their non-numeric token still folds into the
#    structure / branch name and the seam rejects the unknown name.
#
# Every path remains an honest no-op — no crash, no state change, no audit row.
# ---------------------------------------------------------------------------
def test_sell_negative_qty_is_honest_noop() -> None:
    # `sell iron -3` PARSES as qty -3 (the sign survives lstrip("-")), forwarded
    # to the seam whose non-positive guard no-ops with "must be positive".
    sink = InMemorySink()
    result = run_commands(
        ["sell iron -3", "quit"],
        sink=sink,
        state=_fresh(inventory={"iron": 5}),
        now=FIXED_NOW,
    )
    assert "must be positive" in result.text.lower()
    assert result.state.inventory == {"iron": 5}  # nothing consumed
    assert result.state.coins == 0
    assert result.ok_actions == 0
    assert len(sink.records) == 0  # a rejected sell records NOTHING (D2)


def test_sell_non_integer_qty_with_known_item_flags_bad_quantity() -> None:
    # Decision #6 (PR #172): `sell iron abc` — "abc" fails the isdigit test, but
    # the tokens before it ("iron") name a known resource and the whole phrase
    # ("iron abc") does not, so the CLI now flags the botched quantity instead of
    # folding it into the name. Mirrors the fishing CLI's boundary diagnostic:
    # an honest no-op (nothing sold, no audit row), not an "unknown item".
    sink = InMemorySink()
    result = run_commands(
        ["sell iron abc", "quit"],
        sink=sink,
        state=_fresh(inventory={"iron": 5}),
        now=FIXED_NOW,
    )
    assert "Quantity must be a number" in result.text
    assert "'abc'" in result.text
    assert "cannot be sold" not in result.text  # NOT the old unknown-item message
    assert result.state.inventory == {"iron": 5}
    assert result.state.coins == 0
    assert result.ok_actions == 0
    assert len(sink.records) == 0


def test_sell_genuine_multiword_item_name_still_resolves_no_false_quantity_error() -> None:
    # The disambiguation guard: `sell iron pickaxe` names a REAL multi-word item
    # (the "iron pickaxe" TOOL is in the catalog), so the whole phrase resolves as
    # the item and must NOT be mistaken for "iron" + a bad qty "pickaxe". The tool
    # simply isn't a sellable resource, so the honest seam message is "cannot be
    # sold" — never a false "Quantity must be a number".
    sink = InMemorySink()
    result = run_commands(
        ["sell iron pickaxe", "quit"],
        sink=sink,
        state=_fresh(inventory={"iron": 5}),
        now=FIXED_NOW,
    )
    assert "cannot be sold" in result.text
    assert "Quantity must be a number" not in result.text  # no false quantity flag
    assert result.state.inventory == {"iron": 5}
    assert result.ok_actions == 0
    assert len(sink.records) == 0


def test_sell_unknown_single_token_item_still_reports_unknown_item() -> None:
    # An unknown single-token name has no tokens before it to stand as a known
    # item, so the quantity diagnostic never triggers: `sell foobar` still folds
    # to the (unknown) name and the seam reports the honest "cannot be sold".
    sink = InMemorySink()
    result = run_commands(
        ["sell foobar", "quit"],
        sink=sink,
        state=_fresh(inventory={"iron": 5}),
        now=FIXED_NOW,
    )
    assert "cannot be sold" in result.text
    assert "Quantity must be a number" not in result.text
    assert result.ok_actions == 0
    assert len(sink.records) == 0


def test_build_negative_level_is_ignored_and_builds_from_state() -> None:
    # `build forge -1` PARSES as level -1 and forwards it, but the build seam now
    # treats the caller-claimed level as advisory and derives the authoritative
    # current level from state (a fresh forge = 0). The typed -1 therefore cannot
    # force an invalid-level no-op: the forge builds honestly from level 0 to 1,
    # paying the real level-0 cost and recording the true prior level.
    cost = structures.forge_build_cost(0)  # verbatim level-0 cost
    sink = InMemorySink()
    result = run_commands(
        ["build forge -1", "quit"],
        sink=sink,
        state=_fresh(coins=100_000, materials={"wood": 999, "stone": 999, "iron": 999}),
        now=FIXED_NOW,
    )
    assert result.state.structures == {"forge": 1}  # built from real state level 0
    assert result.state.coins == 100_000 - cost.coins  # real level-0 cost charged
    assert result.ok_actions == 1
    # Decision #8: a build now emits a structure-LEVEL row AND a target="coins"
    # ledger row, so a committed build records two rows.
    assert len(sink.records) == 2
    level_row = next(r for r in sink.records if r.target == "structure:forge")
    assert level_row.prev_value == "0"  # true prior level, not the typed -1
    assert level_row.new_value == "1"


def test_build_non_integer_level_folds_into_name_and_no_ops() -> None:
    # `build forge xyz` folds "xyz" into the structure name ("forge xyz"), which
    # is not a buildable structure → honest no-op.
    sink = InMemorySink()
    result = run_commands(
        ["build forge xyz", "quit"],
        sink=sink,
        state=_fresh(coins=100_000, materials={"wood": 999, "stone": 999, "iron": 999}),
        now=FIXED_NOW,
    )
    assert "not buildable" in result.text
    assert result.state.structures == {}
    assert result.state.coins == 100_000
    assert result.ok_actions == 0
    assert len(sink.records) == 0


def test_skill_negative_points_is_honest_noop() -> None:
    # `skill mining -2` PARSES as points -2, forwarded to the seam whose
    # non-positive guard no-ops with "must be positive".
    sink = InMemorySink()
    result = run_commands(
        ["skill mining -2", "quit"],
        sink=sink,
        state=_fresh(),
        now=FIXED_NOW,
    )
    assert "must be positive" in result.text.lower()
    assert result.state.skills == {}  # no points allocated
    assert result.ok_actions == 0
    assert len(sink.records) == 0


def test_skill_non_integer_points_folds_into_name_and_no_ops() -> None:
    # `skill mining foo` folds "foo" into the branch name ("mining foo"), which
    # is not a skill branch → honest no-op (no silent zero-point allocation).
    sink = InMemorySink()
    result = run_commands(
        ["skill mining foo", "quit"],
        sink=sink,
        state=_fresh(),
        now=FIXED_NOW,
    )
    assert "not a skill branch" in result.text
    assert result.state.skills == {}
    assert result.ok_actions == 0
    assert len(sink.records) == 0


# ---------------------------------------------------------------------------
# REPL ergonomics — help, unknown, empty, quit summary
# ---------------------------------------------------------------------------
def test_help_lists_every_command() -> None:
    text = "\n".join(help_lines())
    for verb in ("mine", "explore", "harvest", "sell", "buy", "repair", "descend", "ascend", "build", "vault", "skill"):
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
