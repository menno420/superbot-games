"""Tests for the cross-game inventory BRIDGE seam (``services/inventory_bridge.py``).

Slice 1 of the shared cross-game inventory (design doc Option B). Covers the four
required guarantees:

1. **Valuation matches V043** — :func:`fish_market_value` reuses the canonical
   ``games.fishing.core.economy`` sell curve (#174's price), never a hard-coded
   number; it multiplies 1:1 by quantity and rejects a non-positive qty / unknown
   species.
2. **Gated-off is a pure no-op** — with the flag OFF (the default),
   :func:`exchange_fish_for_coins` changes NOTHING on either side.
3. **Gated-on exchanges correctly and one-directionally** — fish leave the
   fishing haul, coins land on the mining side at the V043 value, and nothing
   flows the other way (no ore/gear into fishing; no fish into the mining pack).
4. **Error path is non-destructive** — an unsellable species, a non-positive
   quantity, or too few fish held leaves BOTH sides byte-for-byte unchanged
   (all-or-nothing).

Plus a guard that the module reads its flag live from the environment and
defaults OFF.
"""

from __future__ import annotations

import pytest

from games.fishing.core import economy
from services import inventory_bridge as bridge
from services.fishing_workflow import FishingState
from services.mining_workflow import MiningState


@pytest.fixture(autouse=True)
def _clear_flag(monkeypatch):
    """Every test starts from the DEFAULT-OFF state (env var unset)."""
    monkeypatch.delenv(bridge.BRIDGE_ENABLED_ENV, raising=False)
    yield


def _fishing(haul=None, coins=0) -> FishingState:
    return FishingState(haul=dict(haul or {}), coins=coins)


def _mining(inventory=None, coins=0) -> MiningState:
    return MiningState(inventory=dict(inventory or {}), coins=coins)


# ---------------------------------------------------------------------------
# 1. Valuation matches the canonical V043 curve
# ---------------------------------------------------------------------------
def test_fish_market_value_matches_v043_curve():
    """Each species is worth exactly its V043 sell value — reused, not re-derived."""
    for species_id in economy.SELL_VALUES:
        assert bridge.fish_market_value(species_id) == economy.sell_value(species_id)
    # spot-check the sim-pinned constants so a curve change is caught here too
    assert bridge.fish_market_value("minnow") == 8
    assert bridge.fish_market_value("bass") == 13
    assert bridge.fish_market_value("pike") == 27
    assert bridge.fish_market_value("legend_carp") == 80


def test_fish_market_value_scales_1_to_1_by_qty():
    """Value scales linearly with quantity (1:1 parity, no rate conversion)."""
    assert bridge.fish_market_value("legend_carp", 3) == 80 * 3
    assert bridge.fish_market_value("bass", 5) == economy.sell_value("bass") * 5


def test_fish_market_value_rejects_bad_inputs():
    """A non-positive qty raises; an unknown species raises KeyError (off the curve)."""
    with pytest.raises(ValueError):
        bridge.fish_market_value("bass", 0)
    with pytest.raises(ValueError):
        bridge.fish_market_value("bass", -2)
    with pytest.raises(KeyError):
        bridge.fish_market_value("kraken")


# ---------------------------------------------------------------------------
# The config flag — default OFF, read live from the env
# ---------------------------------------------------------------------------
def test_bridge_disabled_by_default(monkeypatch):
    monkeypatch.delenv(bridge.BRIDGE_ENABLED_ENV, raising=False)
    assert bridge.bridge_enabled() is False


@pytest.mark.parametrize("value", ["1", "true", "TRUE", "yes", "on", " On "])
def test_bridge_enabled_truthy_values(monkeypatch, value):
    monkeypatch.setenv(bridge.BRIDGE_ENABLED_ENV, value)
    assert bridge.bridge_enabled() is True


@pytest.mark.parametrize("value", ["", "0", "false", "no", "off", "nope"])
def test_bridge_disabled_falsey_values(monkeypatch, value):
    monkeypatch.setenv(bridge.BRIDGE_ENABLED_ENV, value)
    assert bridge.bridge_enabled() is False


# ---------------------------------------------------------------------------
# 2. Gated-off is a pure no-op
# ---------------------------------------------------------------------------
def test_exchange_gated_off_is_noop():
    """With the flag OFF (default), nothing changes on either side."""
    fishing = _fishing(haul={"legend_carp": 2}, coins=5)
    mining = _mining(inventory={"iron": 1}, coins=100)

    result = bridge.exchange_fish_for_coins(fishing, mining, "legend_carp", 1)

    assert result.ok is False
    assert result.gated is True
    assert result.coins_delta == 0
    # both sides untouched
    assert fishing.haul == {"legend_carp": 2}
    assert fishing.coins == 5
    assert mining.coins == 100
    assert mining.inventory == {"iron": 1}


def test_exchange_gated_off_via_explicit_enabled_false():
    """Passing enabled=False forces the gated no-op regardless of the env."""
    fishing = _fishing(haul={"bass": 3})
    mining = _mining(coins=10)

    result = bridge.exchange_fish_for_coins(fishing, mining, "bass", 2, enabled=False)

    assert result.ok is False and result.gated is True
    assert fishing.haul == {"bass": 3}
    assert mining.coins == 10


# ---------------------------------------------------------------------------
# 3. Gated-on exchanges correctly and one-directionally
# ---------------------------------------------------------------------------
def test_exchange_gated_on_moves_fish_to_coins():
    """Enabled: fish leave the haul; coins land on the mining side at V043 value."""
    fishing = _fishing(haul={"legend_carp": 2}, coins=0)
    mining = _mining(coins=100)

    result = bridge.exchange_fish_for_coins(fishing, mining, "legend_carp", 1, enabled=True)

    assert result.ok is True and result.gated is False
    assert result.coins_delta == 80  # V043 legend_carp
    assert result.new_mining_balance == 180
    # fishing side: one fish consumed
    assert fishing.haul == {"legend_carp": 1}
    # mining side: coins credited, pack (inventory) UNTOUCHED — no fish deposited
    assert mining.coins == 180
    assert mining.inventory == {}


def test_exchange_via_env_flag(monkeypatch):
    """The exchange also fires when driven purely by the env flag."""
    monkeypatch.setenv(bridge.BRIDGE_ENABLED_ENV, "1")
    fishing = _fishing(haul={"pike": 4})
    mining = _mining(coins=0)

    result = bridge.exchange_fish_for_coins(fishing, mining, "pike", 3)

    assert result.ok is True
    assert mining.coins == 27 * 3
    assert fishing.haul == {"pike": 1}


def test_exchange_is_one_directional():
    """Nothing flows mining → fishing: fishing coins and mining inventory are inert."""
    fishing = _fishing(haul={"bass": 1}, coins=7)
    mining = _mining(inventory={"gold": 2}, coins=50)

    bridge.exchange_fish_for_coins(fishing, mining, "bass", 1, enabled=True)

    # fishing coins never touched by the bridge (coins only credited mining-side)
    assert fishing.coins == 7
    # no ore/gear crossed into fishing; no fish crossed into the mining pack
    assert mining.inventory == {"gold": 2}
    assert "bass" not in mining.inventory


def test_exchange_full_haul_leaves_zero_count():
    """Selling the whole held quantity leaves a zeroed count (species key retained)."""
    fishing = _fishing(haul={"minnow": 2})
    mining = _mining()

    result = bridge.exchange_fish_for_coins(fishing, mining, "minnow", 2, enabled=True)

    assert result.ok is True
    assert result.coins_delta == 8 * 2
    assert fishing.haul == {"minnow": 0}
    assert mining.coins == 16


# ---------------------------------------------------------------------------
# 4. Error path is non-destructive (all-or-nothing)
# ---------------------------------------------------------------------------
def test_exchange_unsellable_species_is_nondestructive():
    fishing = _fishing(haul={"bass": 1}, coins=3)
    mining = _mining(coins=40)

    result = bridge.exchange_fish_for_coins(fishing, mining, "kraken", 1, enabled=True)

    assert result.ok is False and result.gated is False
    assert fishing.haul == {"bass": 1}
    assert mining.coins == 40


def test_exchange_nonpositive_qty_is_nondestructive():
    fishing = _fishing(haul={"bass": 2})
    mining = _mining(coins=40)

    for bad_qty in (0, -1):
        result = bridge.exchange_fish_for_coins(fishing, mining, "bass", bad_qty, enabled=True)
        assert result.ok is False
        assert fishing.haul == {"bass": 2}
        assert mining.coins == 40


def test_exchange_insufficient_fish_is_nondestructive():
    """Asking for more fish than held leaves BOTH sides byte-for-byte unchanged."""
    fishing = _fishing(haul={"pike": 1})
    mining = _mining(coins=10)

    result = bridge.exchange_fish_for_coins(fishing, mining, "pike", 5, enabled=True)

    assert result.ok is False
    assert "only have 1" in result.message
    assert fishing.haul == {"pike": 1}  # not removed
    assert mining.coins == 10  # not credited


def test_exchange_missing_species_treated_as_zero_held():
    """A species not in the haul at all is 'too few held' — a clean no-op."""
    fishing = _fishing(haul={})
    mining = _mining(coins=10)

    result = bridge.exchange_fish_for_coins(fishing, mining, "bass", 1, enabled=True)

    assert result.ok is False
    assert fishing.haul == {}
    assert mining.coins == 10


# ===========================================================================
# Slice 2 — the AUDITED exchange (exchange_fish_for_coins_audited)
#
# Routes BOTH legs of a committed bridge sale (the fishing-haul debit + the
# mining-coin credit) through the SAME injected audit sink the sibling
# fishing/mining ``sell`` legs use, stays config-gated DEFAULT OFF, and is
# non-destructive on error (no partial audit is ever left behind).
# ===========================================================================
from datetime import datetime, timezone

from services.audit import AuditRecord, InMemorySink

_FIXED_NOW = datetime(2026, 7, 20, 12, 0, 0, tzinfo=timezone.utc)


def _ids():
    """A deterministic mutation-id factory yielding m0, m1, m2, … in order."""
    counter = {"n": 0}

    def _factory() -> str:
        i = counter["n"]
        counter["n"] += 1
        return f"m{i}"

    return _factory


def test_audited_exchange_gated_off_is_noop_and_records_nothing():
    """Flag OFF (default): nothing mutates AND nothing is recorded."""
    fishing = _fishing(haul={"legend_carp": 2}, coins=5)
    mining = _mining(inventory={"iron": 1}, coins=100)
    sink = InMemorySink()

    result = bridge.exchange_fish_for_coins_audited(
        fishing, mining, "legend_carp", 1, sink=sink
    )

    assert result.ok is False and result.gated is True
    assert result.records == ()
    assert sink.records == []  # no partial / gated audit row
    # both sides untouched
    assert fishing.haul == {"legend_carp": 2}
    assert fishing.coins == 5
    assert mining.coins == 100
    assert mining.inventory == {"iron": 1}


def test_audited_exchange_gated_on_moves_fish_and_emits_both_legs():
    """Enabled: fish → mining coins AND exactly two audit rows through the sink."""
    fishing = _fishing(haul={"legend_carp": 2})
    mining = _mining(coins=100)
    sink = InMemorySink()

    result = bridge.exchange_fish_for_coins_audited(
        fishing,
        mining,
        "legend_carp",
        1,
        sink=sink,
        enabled=True,
        now=_FIXED_NOW,
        mutation_id_factory=_ids(),
        guild_id=42,
        actor_id=7,
    )

    # state moved correctly (V043 legend_carp = 80, 1:1)
    assert result.ok is True and result.gated is False
    assert result.coins_delta == 80
    assert result.new_mining_balance == 180
    assert fishing.haul == {"legend_carp": 1}
    assert mining.coins == 180
    assert mining.inventory == {}  # no fish deposited into the mining pack

    # BOTH legs routed through the SAME sink, in commit order (fish debit first)
    assert len(sink.records) == 2
    assert result.records == tuple(sink.records)
    fish_leg, coins_leg = sink.records
    assert all(isinstance(r, AuditRecord) for r in sink.records)

    # leg 1 — the fishing-haul debit
    assert fish_leg.subsystem == "fishing"
    assert fish_leg.mutation_type == bridge.MUTATION_EXCHANGE
    assert fish_leg.target == "haul:legend_carp"
    assert (fish_leg.prev_value, fish_leg.new_value) == ("2", "1")

    # leg 2 — the mining-coin credit
    assert coins_leg.subsystem == "mining"
    assert coins_leg.mutation_type == bridge.MUTATION_EXCHANGE
    assert coins_leg.target == "coins"
    assert (coins_leg.prev_value, coins_leg.new_value) == ("100", "180")

    # shared structural fields threaded onto both rows
    for r in sink.records:
        assert r.scope == "global"
        assert r.guild_id == 42
        assert r.actor_id == 7
        assert r.actor_type == bridge.ACTOR_PLAYER
        assert r.occurred_at == _FIXED_NOW
    # distinct mutation ids (one row per leg)
    assert fish_leg.mutation_id != coins_leg.mutation_id
    assert {fish_leg.mutation_id, coins_leg.mutation_id} == {"m0", "m1"}


def test_audited_exchange_via_env_flag_emits_both_legs(monkeypatch):
    """Driven purely by the env flag, the audited exchange still emits both legs."""
    monkeypatch.setenv(bridge.BRIDGE_ENABLED_ENV, "1")
    fishing = _fishing(haul={"pike": 4})
    mining = _mining(coins=0)
    sink = InMemorySink()

    result = bridge.exchange_fish_for_coins_audited(fishing, mining, "pike", 3, sink=sink)

    assert result.ok is True
    assert mining.coins == 27 * 3  # V043 pike = 27
    assert fishing.haul == {"pike": 1}
    assert len(sink.records) == 2
    assert sink.records[0].target == "haul:pike"
    assert sink.records[1].target == "coins"
    assert sink.records[1].new_value == str(27 * 3)


def test_audited_exchange_is_one_directional_in_the_ledger():
    """Nothing flows mining → fishing; no ledger row credits fishing coins."""
    fishing = _fishing(haul={"bass": 1}, coins=7)
    mining = _mining(inventory={"gold": 2}, coins=50)
    sink = InMemorySink()

    bridge.exchange_fish_for_coins_audited(
        fishing, mining, "bass", 1, sink=sink, enabled=True
    )

    # fishing coins never touched; no fish crossed into the mining pack
    assert fishing.coins == 7
    assert mining.inventory == {"gold": 2}
    # the ONLY coin-credit row targets the MINING side
    coin_rows = [r for r in sink.records if r.target == "coins"]
    assert len(coin_rows) == 1
    assert coin_rows[0].subsystem == "mining"


def test_audited_exchange_unsellable_species_is_nondestructive_no_audit():
    """An unsellable species: both sides unchanged AND no audit row (no partial)."""
    fishing = _fishing(haul={"bass": 1}, coins=3)
    mining = _mining(coins=40)
    sink = InMemorySink()

    result = bridge.exchange_fish_for_coins_audited(
        fishing, mining, "kraken", 1, sink=sink, enabled=True
    )

    assert result.ok is False and result.gated is False
    assert result.records == ()
    assert sink.records == []
    assert fishing.haul == {"bass": 1}
    assert mining.coins == 40


def test_audited_exchange_insufficient_fish_is_nondestructive_no_audit():
    """Too few fish held: nothing moves and NEITHER leg is audited (all-or-nothing)."""
    fishing = _fishing(haul={"pike": 1})
    mining = _mining(coins=10)
    sink = InMemorySink()

    result = bridge.exchange_fish_for_coins_audited(
        fishing, mining, "pike", 5, sink=sink, enabled=True
    )

    assert result.ok is False
    assert sink.records == []  # no partial audit — never one leg without the other
    assert fishing.haul == {"pike": 1}
    assert mining.coins == 10


def test_audited_exchange_nonpositive_qty_is_nondestructive_no_audit():
    """A non-positive quantity: no mutation, no audit row."""
    fishing = _fishing(haul={"bass": 2})
    mining = _mining(coins=40)
    sink = InMemorySink()

    for bad_qty in (0, -1):
        result = bridge.exchange_fish_for_coins_audited(
            fishing, mining, "bass", bad_qty, sink=sink, enabled=True
        )
        assert result.ok is False
        assert sink.records == []
        assert fishing.haul == {"bass": 2}
        assert mining.coins == 40


def test_audited_exchange_full_haul_emits_zeroed_debit_leg():
    """Selling the whole held quantity records a haul-debit leg down to zero."""
    fishing = _fishing(haul={"minnow": 2})
    mining = _mining()
    sink = InMemorySink()

    result = bridge.exchange_fish_for_coins_audited(
        fishing, mining, "minnow", 2, sink=sink, enabled=True
    )

    assert result.ok is True
    assert result.coins_delta == 8 * 2  # V043 minnow = 8
    assert fishing.haul == {"minnow": 0}
    assert mining.coins == 16
    fish_leg, coins_leg = sink.records
    assert (fish_leg.prev_value, fish_leg.new_value) == ("2", "0")
    assert (coins_leg.prev_value, coins_leg.new_value) == ("0", "16")
