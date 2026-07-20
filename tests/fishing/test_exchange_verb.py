"""Tests for the gated cross-game ``exchange`` verb in the fishing CLI (slice 2).

The ``exchange`` verb wires the config-gated ``services/inventory_bridge`` exchange
onto a live command ("walk your catch to the mining market"). This suite pins the
gate and the audit routing at the CLI level:

* **Gated OFF (the default)** — with ``GAMES_INVENTORY_BRIDGE_ENABLED`` unset the
  verb is unavailable: it prints a clear "bridge is disabled" line, changes
  NOTHING, records NOTHING, and is absent from the help surface — so the CLI is
  byte-unchanged from before the bridge existed.
* **Gated ON** — the verb sells landed fish at the mining market, crediting the
  session's mining-coin wallet and routing BOTH legs (haul debit + coin credit)
  through the session's audit sink.
* **Error path** — an unsellable species / too few held is a non-destructive
  no-op that emits no partial audit.
* **One-directional** — the fishing coins are never credited by the bridge.

The bridge flag is driven purely via ``monkeypatch`` on the env var, so nothing
here leaks the enabled state into the rest of the suite.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from games.fishing import cli
from games.fishing.cli import help_lines, new_state, run_commands
from games.fishing.core import spots as spot_table
from services import inventory_bridge as bridge
from services import mining_workflow as mw
from services.audit import InMemorySink

FIXED_NOW = datetime(2026, 7, 20, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def _clear_flag(monkeypatch):
    """Every test starts from the DEFAULT-OFF bridge state (env var unset)."""
    monkeypatch.delenv(bridge.BRIDGE_ENABLED_ENV, raising=False)
    yield


def _fresh(**overrides) -> object:
    state = new_state()
    for key, value in overrides.items():
        setattr(state, key, value)
    return state


# ---------------------------------------------------------------------------
# Gated OFF (the default) — unavailable, no-op, nothing recorded, not in help
# ---------------------------------------------------------------------------
def test_exchange_verb_gated_off_is_a_clean_noop():
    """Flag OFF: a clear disabled response that changes nothing and records nothing."""
    sink = InMemorySink()
    mining = mw.MiningState(coins=0)
    state = _fresh(haul={"legend_carp": 2})

    result = run_commands(
        ["exchange legend_carp 1", "quit"],
        sink=sink,
        state=state,
        mining=mining,
        now=FIXED_NOW,
    )

    assert "bridge is disabled" in result.text.lower()
    # nothing moved on either side, nothing recorded
    assert state.haul == {"legend_carp": 2}
    assert mining.coins == 0
    assert sink.records == []


def test_exchange_verb_absent_from_help_when_gated_off():
    """Flag OFF: help does not list exchange — the surface is unchanged."""
    text = "\n".join(help_lines())
    assert "exchange" not in text


def test_help_surface_is_byte_identical_when_gated_off():
    """The MUTATION help surface is unchanged when gated off — the only bridge line
    is the read-only ``value`` preview (slice 3, always available); the mutating
    ``exchange`` verb stays absent until the flag flips."""
    assert help_lines() == [
        "Commands:",
        "  cast                 cast once at your current spot — spend energy, maybe land a fish",
        "  sell <species> [qty] sell landed fish at the sim-pinned value (default: all you hold)",
        "  value <species> [qty] preview mining-market coins for landed fish (read-only, V043)",
        "  spot <id>            move to a fishing spot (valid: "
        + ", ".join(spot_table.spot_ids())
        + ")",
        "  spots                list every spot + its vibe",
        "  status / haul        show energy, current spot, and your running haul",
        "  help                 show this list",
        "  quit / exit          end the session (prints a summary)",
    ]


# ---------------------------------------------------------------------------
# Gated ON — sells fish at the mining market, routes both legs to the sink
# ---------------------------------------------------------------------------
def test_exchange_verb_gated_on_exchanges_and_audits_both_legs(monkeypatch):
    monkeypatch.setenv(bridge.BRIDGE_ENABLED_ENV, "1")
    sink = InMemorySink()
    mining = mw.MiningState(coins=100)
    state = _fresh(haul={"legend_carp": 2})

    result = run_commands(
        ["exchange legend_carp 1", "quit"],
        sink=sink,
        state=state,
        mining=mining,
        now=FIXED_NOW,
    )

    # state moved: fish debited, mining coins credited at V043 (legend_carp = 80)
    assert state.haul == {"legend_carp": 1}
    assert mining.coins == 180
    assert "mining coins: 180 (+80)" in result.text

    # BOTH legs routed through the CLI's own sink, in commit order
    assert len(sink.records) == 2
    fish_leg, coins_leg = sink.records
    assert fish_leg.subsystem == "fishing" and fish_leg.target == "haul:legend_carp"
    assert (fish_leg.prev_value, fish_leg.new_value) == ("2", "1")
    assert coins_leg.subsystem == "mining" and coins_leg.target == "coins"
    assert (coins_leg.prev_value, coins_leg.new_value) == ("100", "180")
    assert {r.mutation_type for r in sink.records} == {bridge.MUTATION_EXCHANGE}


def test_exchange_verb_defaults_to_all_held(monkeypatch):
    """No quantity given sells the whole held stack (mirrors the sell default)."""
    monkeypatch.setenv(bridge.BRIDGE_ENABLED_ENV, "on")
    sink = InMemorySink()
    mining = mw.MiningState(coins=0)
    state = _fresh(haul={"pike": 3})

    run_commands(["exchange pike", "quit"], sink=sink, state=state, mining=mining, now=FIXED_NOW)

    assert state.haul == {"pike": 0}
    assert mining.coins == 27 * 3  # V043 pike = 27
    assert len(sink.records) == 2


def test_exchange_verb_appears_in_help_when_enabled(monkeypatch, extract_help_verbs):
    """Flag ON: help lists exchange as an available verb."""
    monkeypatch.setenv(bridge.BRIDGE_ENABLED_ENV, "1")
    verbs = extract_help_verbs(help_lines())
    assert "exchange" in verbs


# ---------------------------------------------------------------------------
# Error path (enabled) — non-destructive, no partial audit
# ---------------------------------------------------------------------------
def test_exchange_verb_insufficient_fish_is_nondestructive(monkeypatch):
    monkeypatch.setenv(bridge.BRIDGE_ENABLED_ENV, "1")
    sink = InMemorySink()
    mining = mw.MiningState(coins=10)
    state = _fresh(haul={"pike": 1})

    result = run_commands(
        ["exchange pike 5", "quit"], sink=sink, state=state, mining=mining, now=FIXED_NOW
    )

    assert "only have 1" in result.text
    assert state.haul == {"pike": 1}  # not removed
    assert mining.coins == 10  # not credited
    assert sink.records == []  # no partial audit


def test_exchange_verb_unsellable_species_is_nondestructive(monkeypatch):
    monkeypatch.setenv(bridge.BRIDGE_ENABLED_ENV, "1")
    sink = InMemorySink()
    mining = mw.MiningState(coins=40)
    state = _fresh(haul={"bass": 1})

    run_commands(
        ["exchange kraken 1", "quit"], sink=sink, state=state, mining=mining, now=FIXED_NOW
    )

    assert state.haul == {"bass": 1}
    assert mining.coins == 40
    assert sink.records == []


def test_exchange_verb_usage_hint_on_missing_args(monkeypatch):
    """A bare `exchange` (enabled) prints a usage hint and records nothing."""
    monkeypatch.setenv(bridge.BRIDGE_ENABLED_ENV, "1")
    sink = InMemorySink()
    mining = mw.MiningState()
    state = _fresh(haul={"bass": 1})

    result = run_commands(
        ["exchange", "quit"], sink=sink, state=state, mining=mining, now=FIXED_NOW
    )

    assert "Usage: exchange" in result.text
    assert state.haul == {"bass": 1}
    assert sink.records == []


# ---------------------------------------------------------------------------
# One-directional — the bridge never credits the FISHING coins
# ---------------------------------------------------------------------------
def test_exchange_verb_is_one_directional(monkeypatch):
    monkeypatch.setenv(bridge.BRIDGE_ENABLED_ENV, "1")
    sink = InMemorySink()
    mining = mw.MiningState(coins=0)
    state = _fresh(haul={"bass": 1}, coins=7)

    run_commands(
        ["exchange bass 1", "quit"], sink=sink, state=state, mining=mining, now=FIXED_NOW
    )

    # fishing-side coins are inert; only the mining wallet grows
    assert state.coins == 7
    assert mining.coins == 13  # V043 bass = 13
    coin_rows = [r for r in sink.records if r.target == "coins"]
    assert len(coin_rows) == 1 and coin_rows[0].subsystem == "mining"


def test_exchange_step_flag_routes_through_is_exchange(monkeypatch):
    """The verb is routed as an exchange (StepResult.is_exchange), enabled or not."""
    monkeypatch.setenv(bridge.BRIDGE_ENABLED_ENV, "1")
    sink = InMemorySink()
    mining = mw.MiningState()
    state = _fresh(haul={"bass": 1})
    res = cli.step(state, sink, "exchange bass 1", now=FIXED_NOW, mining=mining)
    assert res.is_exchange is True and res.ok is True

    # gated-off is still routed as an exchange (not an unknown command)
    monkeypatch.delenv(bridge.BRIDGE_ENABLED_ENV, raising=False)
    res_off = cli.step(state, sink, "exchange bass 1", now=FIXED_NOW, mining=mining)
    assert res_off.is_exchange is True and res_off.ok is False
