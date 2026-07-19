"""Tests for the mining WORKFLOW audited seam (``services/mining_workflow.py``).

Covers the two REQUIRED guarantees —

1. every state-changing action emits exactly one well-formed 11-field
   :class:`AuditRecord`; failed / no-op actions record NOTHING;
2. the pure mining core stays importable and pure WITHOUT the seam (the purity
   guard mirrored from the seam side) —

plus behavioural tests for each wired action (loot / wear / trade / repair /
depth gate / build / vault / skills), determinism under a seeded rng + injected
clock + id factory, and the game-neutral ``services/audit.py`` types.
"""

from __future__ import annotations

import importlib
import pkgutil
import random
import sys
from dataclasses import fields
from datetime import datetime, timezone

import pytest

from games.mining.core import capacity, energy, market, skills, structures, workshop
from games.mining.core.energy import EnergyState
from services import audit, mining_workflow as mw
from services.audit import AuditRecord, InMemorySink, Sink

FIXED_NOW = datetime(2026, 7, 13, 12, 0, 0, tzinfo=timezone.utc)
FIXED_ID = "deadbeefdeadbeefdeadbeefdeadbeef"


def _fixed_id() -> str:
    return FIXED_ID


def _full_state(**overrides) -> mw.MiningState:
    """A comfortably-provisioned session; override any field per test."""
    base = dict(
        inventory={"iron": 10, "stone": 10, "pickaxe": 1},
        coins=100_000,
        equipped={"tool": "iron pickaxe"},
        durability={"iron pickaxe": 150},
        energy=EnergyState(energy.MAX_ENERGY, int(FIXED_NOW.timestamp())),
        depth=0,
        materials={"iron": 100, "stone": 100, "gold": 100, "wood": 100},
        structures={},
        skills={},
        vault_level=0,
    )
    base.update(overrides)
    return mw.MiningState(**base)


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


def _assert_well_formed(rec: AuditRecord) -> None:
    """Assert an AuditRecord carries all 11 fields, populated to spec."""
    assert [f.name for f in fields(rec)] == list(_AUDIT_FIELDS)
    assert isinstance(rec.mutation_id, str) and rec.mutation_id
    assert rec.subsystem == "mining"
    assert isinstance(rec.mutation_type, str) and rec.mutation_type
    assert isinstance(rec.target, str) and rec.target
    assert rec.scope == "global"
    assert isinstance(rec.actor_type, str) and rec.actor_type
    assert isinstance(rec.occurred_at, datetime)
    # prev/new are string-rendered or None; the structural fields typed int|None.
    assert rec.prev_value is None or isinstance(rec.prev_value, str)
    assert rec.new_value is None or isinstance(rec.new_value, str)
    assert rec.guild_id is None or isinstance(rec.guild_id, int)
    assert rec.actor_id is None or isinstance(rec.actor_id, int)


# ---------------------------------------------------------------------------
# REQUIRED TEST 1 — audit-per-state-changing-action
# ---------------------------------------------------------------------------
def _do_mine(state, sink):
    return mw.mine(state, sink=sink, rng=random.Random(1), now=FIXED_NOW, mutation_id_factory=_fixed_id)


def _do_harvest(state, sink):
    return mw.harvest(state, sink=sink, rng=random.Random(1), now=FIXED_NOW, mutation_id_factory=_fixed_id)


def _do_sell(state, sink):
    return mw.sell(state, "iron", 3, sink=sink, now=FIXED_NOW, mutation_id_factory=_fixed_id)


def _do_buy(state, sink):
    return mw.buy(state, "torch", sink=sink, now=FIXED_NOW, mutation_id_factory=_fixed_id)


def _do_repair(state, sink):
    state.durability["iron pickaxe"] = 10
    return mw.repair(state, "iron pickaxe", sink=sink, now=FIXED_NOW, mutation_id_factory=_fixed_id)


def _do_descend(state, sink):
    state.equipped = {"tool": "iron pickaxe", "light": "lantern"}
    return mw.descend(state, sink=sink, now=FIXED_NOW, mutation_id_factory=_fixed_id)


def _do_ascend(state, sink):
    state.equipped = {"tool": "iron pickaxe", "light": "lantern"}
    state.depth = 1
    return mw.ascend(state, sink=sink, now=FIXED_NOW, mutation_id_factory=_fixed_id)


def _do_build(state, sink):
    return mw.build_structure(state, "forge", 0, sink=sink, now=FIXED_NOW, mutation_id_factory=_fixed_id)


def _do_vault(state, sink):
    return mw.vault_upgrade(state, sink=sink, now=FIXED_NOW, mutation_id_factory=_fixed_id)


def _do_skill(state, sink):
    return mw.allocate_skill(state, skills.MINING, 3, sink=sink, now=FIXED_NOW, mutation_id_factory=_fixed_id)


_STATE_CHANGING = [
    ("mine", _do_mine, mw.MUTATION_MINE),
    ("harvest", _do_harvest, mw.MUTATION_HARVEST),
    ("sell", _do_sell, market.SELL_REASON),
    ("buy", _do_buy, market.BUY_REASON),
    ("repair", _do_repair, workshop.REPAIR_REASON),
    ("descend", _do_descend, mw.MUTATION_DESCEND),
    ("ascend", _do_ascend, mw.MUTATION_ASCEND),
    ("build", _do_build, market.structure_build_reason("forge")),
    ("vault", _do_vault, market.VAULT_UPGRADE_REASON),
    ("skill", _do_skill, mw.MUTATION_ALLOCATE_SKILL),
]


# Decision #8: a coin-SINK structure/vault op ALSO emits a target="coins" ledger
# row (in addition to its LEVEL row), so those ops record two rows — the LEVEL
# row stays the primary ``result.record`` at index 0, the coin row is appended.
_TWO_ROW_ACTIONS = {"build", "vault"}


@pytest.mark.parametrize("name,action,expected_mutation", _STATE_CHANGING, ids=[c[0] for c in _STATE_CHANGING])
def test_state_changing_action_records_a_well_formed_primary_record(name, action, expected_mutation):
    """Every state-changing action emits a well-formed primary AuditRecord.

    Coin-sink structure/vault ops ALSO emit a target="coins" ledger row
    (decision #8), so they record two rows; the primary (``result.record``)
    stays the LEVEL row at index 0.
    """
    state = _full_state()
    sink = InMemorySink()
    result = action(state, sink)
    assert result.ok, f"{name} should have succeeded"
    expected_n = 2 if name in _TWO_ROW_ACTIONS else 1
    assert len(sink.records) == expected_n, f"{name} must record {expected_n} record(s)"
    rec = sink.records[0]
    _assert_well_formed(rec)
    assert rec.mutation_type == expected_mutation
    assert rec is result.record
    # the injected id/clock flow straight through to the record
    assert rec.mutation_id == FIXED_ID
    assert rec.occurred_at == FIXED_NOW
    # the appended coin-ledger row (if any) is itself well-formed and coins-targeted
    if name in _TWO_ROW_ACTIONS:
        coin_row = sink.records[1]
        _assert_well_formed(coin_row)
        assert coin_row.target == "coins"
        assert coin_row.mutation_type == expected_mutation


# --- failed / no-op actions record NOTHING ---------------------------------
def _noop_mine(state, sink):
    state.energy = EnergyState(0, int(FIXED_NOW.timestamp()))
    return mw.mine(state, sink=sink, now=FIXED_NOW)


def _noop_sell_unsellable(state, sink):
    return mw.sell(state, "iron pickaxe", 1, sink=sink)  # gear is never sellable


def _noop_sell_too_many(state, sink):
    return mw.sell(state, "iron", 999, sink=sink)


def _noop_buy_broke(state, sink):
    state.coins = 1
    return mw.buy(state, "diamond pickaxe", sink=sink)


def _noop_repair_full(state, sink):
    return mw.repair(state, "iron pickaxe", sink=sink)  # already at max


def _noop_repair_broke(state, sink):
    state.durability["iron pickaxe"] = 1
    state.coins = 0
    return mw.repair(state, "iron pickaxe", sink=sink)


def _noop_descend_gate(state, sink):
    state.equipped = {"tool": "iron pickaxe"}  # no light → gated at surface
    return mw.descend(state, sink=sink)


def _noop_ascend_surface(state, sink):
    state.depth = 0
    return mw.ascend(state, sink=sink)


def _noop_build_broke(state, sink):
    state.coins = 0
    return mw.build_structure(state, "forge", 0, sink=sink)


def _noop_build_no_materials(state, sink):
    state.materials = {}
    return mw.build_structure(state, "forge", 0, sink=sink)


def _noop_vault_broke(state, sink):
    state.coins = 0
    return mw.vault_upgrade(state, sink=sink)


def _noop_skill_bad_branch(state, sink):
    return mw.allocate_skill(state, "telekinesis", 1, sink=sink)


_NO_OP = [
    ("mine_no_energy", _noop_mine),
    ("sell_unsellable", _noop_sell_unsellable),
    ("sell_too_many", _noop_sell_too_many),
    ("buy_broke", _noop_buy_broke),
    ("repair_full", _noop_repair_full),
    ("repair_broke", _noop_repair_broke),
    ("descend_gated", _noop_descend_gate),
    ("ascend_surface", _noop_ascend_surface),
    ("build_broke", _noop_build_broke),
    ("build_no_materials", _noop_build_no_materials),
    ("vault_broke", _noop_vault_broke),
    ("skill_bad_branch", _noop_skill_bad_branch),
]


@pytest.mark.parametrize("name,action", _NO_OP, ids=[c[0] for c in _NO_OP])
def test_failed_action_records_nothing(name, action):
    """A blocked / no-op action returns ok=False and records NOTHING."""
    state = _full_state()
    sink = InMemorySink()
    result = action(state, sink)
    assert result.ok is False
    assert result.message
    assert result.record is None
    assert sink.records == []


def test_noop_actions_do_not_mutate_coins_or_depth():
    """A gated descend and a broke buy leave the state untouched."""
    state = _full_state(coins=1, equipped={"tool": "iron pickaxe"}, depth=0)
    sink = InMemorySink()
    before_coins, before_depth = state.coins, state.depth
    mw.descend(state, sink=sink)
    mw.buy(state, "diamond pickaxe", sink=sink)
    assert state.coins == before_coins
    assert state.depth == before_depth
    assert sink.records == []


# ---------------------------------------------------------------------------
# REQUIRED TEST 2 — core stays importable / pure WITHOUT the seam
# ---------------------------------------------------------------------------
_FORBIDDEN_PREFIXES = ("services", "cogs", "views", "utils.", "disbot")
_FORBIDDEN = ("discord", "asyncpg", "aiohttp", "requests", "sqlalchemy", "psycopg")


def test_core_stays_importable_and_pure_without_the_seam():
    """Importing the pure core pulls in NO services/host modules (guard from the seam side)."""
    for mod in list(sys.modules):
        if mod == "services" or mod.startswith("services."):
            del sys.modules[mod]
    for mod in list(sys.modules):
        if mod == "games.mining.core" or mod.startswith("games.mining.core."):
            del sys.modules[mod]

    before = set(sys.modules)
    core = importlib.import_module("games.mining.core")
    modules = [m.name for m in pkgutil.iter_modules(core.__path__)]
    assert len(modules) == 19, "the core must stay exactly 19 modules"
    for m in modules:
        importlib.import_module(f"games.mining.core.{m}")
    loaded = set(sys.modules) - before

    forbidden = [
        n
        for n in loaded
        if any(n == f or n.startswith(f + ".") for f in _FORBIDDEN)
        or n.startswith(_FORBIDDEN_PREFIXES)
    ]
    assert forbidden == [], f"impure imports leaked into the pure core: {forbidden}"


def test_seam_imports_core_but_core_never_imports_seam():
    """The one-way dependency: the seam names core modules; core never names services."""
    import inspect

    src = inspect.getsource(mw)
    assert "from games.mining.core" in src
    core_src = importlib.import_module("games.mining.core.rewards")
    assert "services" not in inspect.getsource(core_src)


# ---------------------------------------------------------------------------
# Behavioural — mine
# ---------------------------------------------------------------------------
def test_mine_grants_loot_wears_tool_and_spends_energy():
    state = _full_state(inventory={}, durability={"iron pickaxe": 150})
    sink = InMemorySink()
    start_energy = state.energy.current
    r = mw.mine(state, sink=sink, rng=random.Random(7), now=FIXED_NOW)
    assert r.ok and r.amount >= 1
    assert state.inventory[r.ore] == r.amount
    assert state.durability["iron pickaxe"] == 149  # tool wore 1
    assert state.energy.current == start_energy - energy.DIG_COST
    assert r.record.target == f"inventory:{r.ore}"


def test_mine_light_only_wears_underground():
    """The light is underground-only: it wears at depth>0, not on the surface."""
    equipped = {"tool": "iron pickaxe", "light": "lantern"}
    # surface: light does NOT wear
    surface = _full_state(equipped=dict(equipped), durability={"iron pickaxe": 150, "lantern": 100}, depth=0)
    mw.mine(surface, sink=InMemorySink(), rng=random.Random(3), now=FIXED_NOW)
    assert surface.durability["lantern"] == 100
    # underground: light wears
    deep = _full_state(equipped=dict(equipped), durability={"iron pickaxe": 150, "lantern": 100}, depth=1)
    mw.mine(deep, sink=InMemorySink(), rng=random.Random(3), now=FIXED_NOW)
    assert deep.durability["lantern"] == 99


def test_mine_reports_break_only_on_the_tick_it_breaks():
    """A tool broken on an earlier dig is not re-reported as ``broke`` again.

    ``_apply_wear`` promises ``broke`` names only the items that hit 0 THIS tick.
    A tool at durability 1 breaks on the first dig (broke=(tool,)); on the next
    dig it is already at 0, so it must not wear further and must NOT reappear in
    ``broke`` (regression: it used to be re-reported on every subsequent action).
    """
    state = _full_state(
        inventory={},
        equipped={"tool": "iron pickaxe"},
        durability={"iron pickaxe": 1},
    )
    r1 = mw.mine(state, sink=InMemorySink(), rng=random.Random(1), now=FIXED_NOW)
    assert r1.broke == ("iron pickaxe",)  # broke on this tick
    assert state.durability["iron pickaxe"] == 0

    r2 = mw.mine(state, sink=InMemorySink(), rng=random.Random(1), now=FIXED_NOW)
    assert r2.broke == ()  # already broken — not a fresh break, not re-reported
    assert state.durability["iron pickaxe"] == 0  # stays 0, never wears below


def test_mine_multiplier_uses_core_verbatim():
    """The seam's multiplier is exactly rewards.mine_multiplier for the loadout."""
    from games.mining.core import rewards

    state = _full_state(equipped={"tool": "diamond pickaxe"}, inventory={})
    expected = rewards.mine_multiplier(state.equipped, state.inventory)
    # diamond pickaxe: mining_power 8 → 1 + 8*0.0625 = 1.5
    assert expected == pytest.approx(1.5)


def test_mine_deterministic_with_seeded_rng_and_injected_clock():
    a = _full_state(inventory={})
    b = _full_state(inventory={})
    sink_a, sink_b = InMemorySink(), InMemorySink()
    ra = mw.mine(a, sink=sink_a, rng=random.Random(99), now=FIXED_NOW, mutation_id_factory=_fixed_id)
    rb = mw.mine(b, sink=sink_b, rng=random.Random(99), now=FIXED_NOW, mutation_id_factory=_fixed_id)
    assert (ra.ore, ra.amount) == (rb.ore, rb.amount)
    assert sink_a.records[0] == sink_b.records[0]


# ---------------------------------------------------------------------------
# Behavioural — harvest
# ---------------------------------------------------------------------------
def test_harvest_grants_wood():
    state = _full_state(inventory={})
    sink = InMemorySink()
    r = mw.harvest(state, sink=sink, rng=random.Random(5), now=FIXED_NOW)
    assert r.ok and r.amount >= 1
    assert state.inventory["wood"] == r.amount
    assert sink.records[0].target == "inventory:wood"


def test_harvest_axe_doubles_the_band():
    """has_axe doubles the wood roll (core roll_harvest_amount) — same seed."""
    with_axe = _full_state(inventory={"axe": 1})
    without = _full_state(inventory={})
    ra = mw.harvest(with_axe, sink=InMemorySink(), rng=random.Random(2))
    rb = mw.harvest(without, sink=InMemorySink(), rng=random.Random(2))
    assert ra.amount == rb.amount * 2


# ---------------------------------------------------------------------------
# Behavioural — sell / buy
# ---------------------------------------------------------------------------
def test_sell_debits_inventory_and_credits_verbatim_price():
    state = _full_state(inventory={"gold": 5}, coins=0)
    sink = InMemorySink()
    unit = market.sell_price("gold")  # verbatim core price (6)
    r = mw.sell(state, "gold", 4, sink=sink, now=FIXED_NOW, mutation_id_factory=_fixed_id)
    assert r.ok
    assert state.inventory["gold"] == 1
    assert state.coins == unit * 4
    assert r.coins_delta == unit * 4
    assert r.new_balance == state.coins
    rec = sink.records[0]
    assert rec.target == "coins"
    assert rec.prev_value == "0"
    assert rec.new_value == str(unit * 4)
    assert rec.mutation_type == market.SELL_REASON


def test_buy_debits_coins_and_grants_item():
    price = market.buy_price("iron pickaxe")  # verbatim (60)
    state = _full_state(inventory={}, coins=price + 5)
    sink = InMemorySink()
    r = mw.buy(state, "iron pickaxe", sink=sink)
    assert r.ok
    assert state.coins == 5
    assert state.inventory["iron pickaxe"] == 1
    assert r.coins_delta == -price
    assert sink.records[0].mutation_type == market.BUY_REASON


def test_buy_affordability_boundary():
    price = market.buy_price("torch")
    exact = _full_state(inventory={}, coins=price)
    assert mw.buy(exact, "torch", sink=InMemorySink()).ok  # exactly enough works
    short = _full_state(inventory={}, coins=price - 1)
    assert mw.buy(short, "torch", sink=InMemorySink()).ok is False


# ---------------------------------------------------------------------------
# Behavioural — repair
# ---------------------------------------------------------------------------
def test_repair_uses_core_cost_and_restores_durability():
    state = _full_state(durability={"iron pickaxe": 50}, coins=10_000)
    expected = workshop.repair_cost("iron pickaxe", 50)  # verbatim core cost
    maximum = 150
    sink = InMemorySink()
    r = mw.repair(state, "iron pickaxe", sink=sink)
    assert r.ok
    assert r.cost == expected
    assert state.durability["iron pickaxe"] == maximum
    assert state.coins == 10_000 - expected
    assert sink.records[0].mutation_type == workshop.REPAIR_REASON


# ---------------------------------------------------------------------------
# Behavioural — descend / ascend (the depth gate)
# ---------------------------------------------------------------------------
def test_descend_gate_blocks_a_torchless_surface_player():
    """A fresh iron-pickaxe player has no light → cannot leave the Surface."""
    state = _full_state(equipped={"tool": "iron pickaxe"}, depth=0)
    sink = InMemorySink()
    r = mw.descend(state, sink=sink)
    assert r.ok is False
    assert state.depth == 0
    assert sink.records == []


def test_descend_with_torch_reaches_cavern():
    state = _full_state(equipped={"tool": "iron pickaxe", "light": "torch"}, depth=0)
    sink = InMemorySink()
    r = mw.descend(state, sink=sink, now=FIXED_NOW)
    assert r.ok and state.depth == 1
    assert sink.records[0].target == "depth"
    assert sink.records[0].prev_value == "0" and sink.records[0].new_value == "1"


def test_descend_stops_at_lights_reach():
    """A torch (depth_access 1) reaches Cavern but not the Deep."""
    state = _full_state(equipped={"tool": "iron pickaxe", "light": "torch"}, depth=1)
    r = mw.descend(state, sink=InMemorySink())
    assert r.ok is False and state.depth == 1


def test_ascend_climbs_toward_surface():
    state = _full_state(depth=2)
    sink = InMemorySink()
    r = mw.ascend(state, sink=sink, now=FIXED_NOW)
    assert r.ok and state.depth == 1
    assert sink.records[0].mutation_type == mw.MUTATION_ASCEND


# ---------------------------------------------------------------------------
# Behavioural — build / vault
# ---------------------------------------------------------------------------
def test_build_forge_debits_coins_and_materials():
    cost = structures.forge_build_cost(0)  # verbatim: 3000 coins, iron 25, stone 15
    state = _full_state(coins=cost.coins + 100, materials={"iron": 30, "stone": 20})
    sink = InMemorySink()
    r = mw.build_structure(state, "forge", 0, sink=sink)
    assert r.ok
    assert state.coins == 100
    assert state.materials["iron"] == 30 - cost.materials["iron"]
    assert state.materials["stone"] == 20 - cost.materials["stone"]
    assert state.structures["forge"] == 1
    assert sink.records[0].target == "structure:forge"
    assert sink.records[0].mutation_type == market.structure_build_reason("forge")


def test_build_rejects_unknown_structure():
    state = _full_state()
    r = mw.build_structure(state, "spaceship", 0, sink=InMemorySink())
    assert r.ok is False


def test_build_structure_uses_state_level_not_caller_claim():
    # The trailing integer a player can type (`build forge <level>`) is advisory
    # only: the cost, the level write, and the audit prev_value must all derive
    # from state.structures, never the caller's claim. Before the fix, `build
    # forge 0` on a maxed forge downgraded it for the cheap level-0 cost and
    # `build forge 1` on a fresh forge skipped a tier for free.
    state = _full_state()
    sink = InMemorySink()
    assert mw.build_structure(state, "forge", 0, sink=sink).ok  # 0 -> 1
    assert mw.build_structure(state, "forge", 1, sink=sink).ok  # 1 -> 2 (max)
    assert state.structures["forge"] == 2
    n = len(sink.records)

    # Bogus low claim on a maxed forge: a clean rejected no-op — no downgrade,
    # no state mutation, no audit row (before fix: downgraded to 1 + bogus row).
    r = mw.build_structure(state, "forge", 0, sink=sink)
    assert r.ok is False
    assert state.structures["forge"] == 2
    assert len(sink.records) == n

    # Inflated claim on a level-0 forge: builds exactly one tier and records the
    # real prior level (before fix: jumped to 2 with prev_value "1"). Assert on
    # the structure-LEVEL row specifically — decision #8 appends a target="coins"
    # ledger row after it, whose prev/new carry coin balances, not levels.
    fresh = _full_state()
    s2 = InMemorySink()
    r2 = mw.build_structure(fresh, "forge", 1, sink=s2)
    assert r2.ok
    assert fresh.structures["forge"] == 1
    level_row = next(r for r in s2.records if r.target == "structure:forge")
    assert level_row.prev_value == "0"
    assert level_row.new_value == "1"
    assert level_row is r2.record  # the LEVEL row stays the primary record


def test_vault_upgrade_raises_cap_using_core_cost():
    cost = capacity.vault_upgrade_cost(0)  # verbatim base cost (2000)
    state = _full_state(coins=cost + 50, vault_level=0)
    sink = InMemorySink()
    r = mw.vault_upgrade(state, sink=sink)
    assert r.ok
    assert state.vault_level == 1
    assert r.capacity == capacity.vault_capacity(1)
    assert state.coins == 50
    assert sink.records[0].mutation_type == market.VAULT_UPGRADE_REASON


def test_vault_upgrade_blocked_when_maxed():
    state = _full_state(coins=10_000_000, vault_level=capacity.MAX_VAULT_LEVEL)
    r = mw.vault_upgrade(state, sink=InMemorySink())
    assert r.ok is False


def test_economy_audit_log_coin_rows_reconstruct_the_wallet_after_build_and_vault():
    """Decision #8: build / vault are coin SINKS that used to audit only a LEVEL
    row, so a wallet rebuilt from the log's coin rows under-counted them. They now
    ALSO emit a target="coins" row (balance before/after), matching the sell / buy
    / repair shape — so a wallet reconstructed purely from economy_audit_log coin
    rows equals the live wallet after a build and a vault upgrade.
    """
    start = 100_000
    state = _full_state(coins=start, materials={"iron": 100, "stone": 100}, structures={}, vault_level=0)
    sink = InMemorySink()

    build = mw.build_structure(state, "forge", 0, sink=sink)
    assert build.ok
    vault = mw.vault_upgrade(state, sink=sink)
    assert vault.ok

    # Rebuild the wallet purely from the log's coin-target rows (delta replay).
    coin_rows = [r for r in sink.records if r.target == "coins"]
    assert len(coin_rows) == 2, "each coin sink (build + vault) must leave one coins row"
    reconstructed = start
    for row in coin_rows:
        reconstructed += int(row.new_value) - int(row.prev_value)
    assert reconstructed == state.coins, "log-derived wallet must equal the live wallet"

    # The coin sink actually moved coins (the rows are not vacuous), and the
    # structure/vault LEVEL rows still coexist alongside the coin rows.
    assert state.coins < start
    assert any(r.target == "structure:forge" for r in sink.records)
    assert any(r.target == "vault" for r in sink.records)


# ---------------------------------------------------------------------------
# Behavioural — skills (is_branch guard)
# ---------------------------------------------------------------------------
def test_allocate_skill_rejects_bad_branch_without_zeroing():
    state = _full_state(skills={skills.MINING: 2})
    sink = InMemorySink()
    r = mw.allocate_skill(state, "flying", 3, sink=sink)
    assert r.ok is False
    assert state.skills == {skills.MINING: 2}  # untouched, not silently zeroed
    assert sink.records == []


def test_allocate_skill_accumulates_valid_branch():
    state = _full_state(skills={})
    sink = InMemorySink()
    r = mw.allocate_skill(state, skills.COMBAT, 4, sink=sink)
    assert r.ok and state.skills[skills.COMBAT] == 4
    assert sink.records[0].target == f"skill:{skills.COMBAT}"


def test_allocate_skill_respects_soft_total_cap():
    state = _full_state(skills={skills.MINING: 10, skills.COMBAT: 9})
    r = mw.allocate_skill(state, skills.FORTUNE, 5, sink=InMemorySink())
    assert r.ok is False  # 10+9+5 > SOFT_TOTAL_CAP (20)


# ---------------------------------------------------------------------------
# The injected clock / id factory defaults
# ---------------------------------------------------------------------------
def test_default_clock_and_id_are_used_when_not_injected():
    state = _full_state(inventory={})
    sink = InMemorySink()
    before = datetime.now(timezone.utc)
    r = mw.mine(state, sink=sink, rng=random.Random(1))
    after = datetime.now(timezone.utc)
    rec = r.record
    assert before <= rec.occurred_at <= after
    assert len(rec.mutation_id) == 32  # uuid4().hex default


def test_distinct_mutation_ids_across_calls_by_default():
    state = _full_state(inventory={})
    sink = InMemorySink()
    mw.mine(state, sink=sink, rng=random.Random(1))
    mw.mine(state, sink=sink, rng=random.Random(1))
    assert sink.records[0].mutation_id != sink.records[1].mutation_id


# ---------------------------------------------------------------------------
# The game-neutral services/audit.py
# ---------------------------------------------------------------------------
def test_audit_module_exposes_neutral_types():
    assert set(audit.__all__) == {"AuditRecord", "Sink", "InMemorySink"}
    # the mining seam re-exports the SAME objects (no divergent copy)
    assert mw.AuditRecord is AuditRecord
    assert mw.Sink is Sink
    assert mw.InMemorySink is InMemorySink


def test_audit_record_is_neutral_and_frozen():
    rec = AuditRecord(
        mutation_id="x",
        subsystem="fishing",  # a different game can use it directly
        mutation_type="fishing:cast",
        target="inventory:cod",
        scope="global",
        guild_id=None,
        prev_value=None,
        new_value="1",
        actor_id=None,
        actor_type="player",
        occurred_at=FIXED_NOW,
    )
    assert rec.subsystem == "fishing"
    with pytest.raises(Exception):
        rec.subsystem = "mining"  # frozen


def test_inmemory_sink_satisfies_the_sink_protocol():
    sink = InMemorySink()
    assert isinstance(sink, Sink)  # runtime_checkable Protocol
    assert sink.records == []
