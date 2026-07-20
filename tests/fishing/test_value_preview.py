"""Tests for the read-only ``value`` market-value preview verb (slice 3).

The ``value`` verb surfaces :func:`services.inventory_bridge.fish_market_value` —
the canonical V043 price a catch would fetch at the mining market — as a PURE,
read-only affordance in the fishing CLI. Unlike the mutating ``exchange`` verb
(slice 2), a price quote is not a transfer, so this suite pins that it:

* reports the CORRECT V043 coins for a species+qty (minnow 8 · bass 13 · pike 27
  · legend_carp 80), scaling 1:1 with quantity;
* is available and byte-identical whether the bridge flag is ON or OFF, and is
  listed in help in BOTH states (it never depends on ``GAMES_INVENTORY_BRIDGE_ENABLED``);
* MUTATES NOTHING and RECORDS NOTHING — the haul, the fishing coins, the mining
  wallet, and the audit sink are all untouched, flag on or off;
* handles the grammar (default = all held / else 1, trailing-int quantity,
  multi-word display name) and the unsellable-species / bad-quantity no-ops
  gracefully (an honest message, never a raise).

The bridge flag is driven purely via ``monkeypatch`` so nothing here leaks the
enabled state into the rest of the suite.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from games.fishing import cli
from games.fishing.cli import help_lines, new_state, run_commands
from services import inventory_bridge as bridge
from services import mining_workflow as mw
from services.audit import InMemorySink

FIXED_NOW = datetime(2026, 7, 20, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def _clear_flag(monkeypatch):
    """Every test starts from the DEFAULT-OFF bridge state (env var unset)."""
    monkeypatch.delenv(bridge.BRIDGE_ENABLED_ENV, raising=False)
    yield


def _fresh(**overrides):
    state = new_state()
    for key, value in overrides.items():
        setattr(state, key, value)
    return state


# ---------------------------------------------------------------------------
# Correct V043 values — a pure quote, scaling 1:1 with quantity
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "species, qty, coins, label",
    [
        ("minnow", 1, 8, "Minnow"),
        ("bass", 1, 13, "Bass"),
        ("pike", 3, 81, "Pike"),  # 27 × 3
        ("legend_carp", 2, 160, "Legendary Carp"),  # 80 × 2
    ],
)
def test_value_reports_correct_v043_price(species, qty, coins, label):
    state = _fresh()
    res = cli.step(state, InMemorySink(), f"value {species} {qty}")
    assert res.lines == [f"{qty}× {label} is worth {coins} coins at the mining market (V043)."]
    # The quote matches the pure service function exactly (never re-derived).
    assert coins == bridge.fish_market_value(species, qty)


def test_value_matches_service_for_every_species():
    """The verb's quote equals fish_market_value for every sellable species."""
    state = _fresh()
    for species in ("minnow", "bass", "pike", "legend_carp"):
        res = cli.step(state, InMemorySink(), f"value {species} 4")
        assert str(bridge.fish_market_value(species, 4)) in res.lines[0]


# ---------------------------------------------------------------------------
# Available + IDENTICAL regardless of the flag; never mutates, never records
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("flag", [None, "1"])
def test_value_available_and_identical_flag_on_or_off(monkeypatch, flag):
    if flag is not None:
        monkeypatch.setenv(bridge.BRIDGE_ENABLED_ENV, flag)
    state = _fresh(haul={"pike": 2})
    res = cli.step(state, InMemorySink(), "value pike 2")
    assert res.lines == ["2× Pike is worth 54 coins at the mining market (V043)."]


@pytest.mark.parametrize("flag", [None, "1"])
def test_value_mutates_nothing_and_records_nothing(monkeypatch, flag):
    """A quote is not a transfer: haul, fishing coins, mining wallet, sink untouched."""
    if flag is not None:
        monkeypatch.setenv(bridge.BRIDGE_ENABLED_ENV, flag)
    sink = InMemorySink()
    mining = mw.MiningState(coins=100)
    state = _fresh(haul={"legend_carp": 3}, coins=5)

    result = run_commands(
        ["value legend_carp 2", "value legend_carp", "quit"],
        sink=sink,
        state=state,
        mining=mining,
        now=FIXED_NOW,
    )

    assert "160 coins" in result.text  # 80 × 2
    assert "240 coins" in result.text  # default = all 3 held, 80 × 3
    # Nothing moved on any side, nothing recorded.
    assert state.haul == {"legend_carp": 3}
    assert state.coins == 5
    assert mining.coins == 100
    assert sink.records == []


# ---------------------------------------------------------------------------
# Discoverability — help lists ``value`` in BOTH flag states
# ---------------------------------------------------------------------------
def test_value_in_help_when_gated_off(extract_help_verbs):
    verbs = extract_help_verbs(help_lines())
    assert "value" in verbs
    assert "exchange" not in verbs  # the mutating verb stays hidden when off


def test_value_in_help_when_enabled(monkeypatch, extract_help_verbs):
    monkeypatch.setenv(bridge.BRIDGE_ENABLED_ENV, "1")
    verbs = extract_help_verbs(help_lines())
    assert "value" in verbs
    assert "exchange" in verbs


def test_value_help_line_is_flag_independent(monkeypatch):
    """The read-only value line is byte-identical whether the flag is on or off."""
    off = help_lines()
    monkeypatch.setenv(bridge.BRIDGE_ENABLED_ENV, "1")
    on = help_lines()
    value_line = "  value <species> [qty] preview mining-market coins for landed fish (read-only, V043)"
    assert value_line in off
    assert value_line in on


# ---------------------------------------------------------------------------
# Grammar — default (all held / else 1), multi-word name, no-ops
# ---------------------------------------------------------------------------
def test_value_defaults_to_all_held():
    state = _fresh(haul={"bass": 4})
    res = cli.step(state, InMemorySink(), "value bass")
    assert res.lines == ["4× Bass is worth 52 coins at the mining market (V043)."]  # 13 × 4


def test_value_defaults_to_one_when_none_held():
    state = _fresh(haul={})
    res = cli.step(state, InMemorySink(), "value bass")
    assert res.lines == ["1× Bass is worth 13 coins at the mining market (V043)."]


def test_value_resolves_multiword_display_name():
    state = _fresh()
    res = cli.step(state, InMemorySink(), "value Legendary Carp 1")
    assert res.lines == ["1× Legendary Carp is worth 80 coins at the mining market (V043)."]


def test_value_unsellable_species_is_a_graceful_noop():
    state = _fresh(haul={"bass": 1})
    res = cli.step(state, InMemorySink(), "value kraken 2")
    assert res.lines == ["kraken cannot be sold at the mining market."]
    assert state.haul == {"bass": 1}


def test_value_nonpositive_quantity_is_rejected():
    state = _fresh()
    res = cli.step(state, InMemorySink(), "value pike 0")
    assert res.lines == ["Quantity must be positive."]


def test_value_bare_verb_prints_usage():
    state = _fresh()
    res = cli.step(state, InMemorySink(), "value")
    assert res.lines and "Usage: value" in res.lines[0]
    # A read-only info verb: no mutation flags set.
    assert res.is_cast is False and res.is_sell is False and res.is_exchange is False
