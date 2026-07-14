"""Detector-trip registry — every sim invariant predicate has a proven witness.

The invariant predicates are the sims' alarm wires: a predicate that can
never return False is a dead detector, and (as #99 found for economy_sim)
nothing structurally prevented one from rotting into an always-True stub.
This registry closes that class:

* the predicate set is ENUMERATED from the sim modules themselves — every
  module-level function a sim module defines with a ``bool`` return
  annotation — never hand-listed, so a new predicate is seen automatically;
* each enumerated predicate must have a registered VIOLATION WITNESS — a
  construction (``dataclasses.replace`` on a report / targeted monkeypatch;
  no shipped constant is edited) under which the predicate returns False;
* completeness is asserted both ways: a predicate without a witness fails
  ("dead detector until proven trippable"), and a stale witness for a
  removed/renamed predicate also fails;
* each predicate is additionally asserted True on the shipped state, so a
  witness can't pass by breaking the predicate outright.

Spec provenance: the detector-trip registry card idea from
``.sessions/2026-07-14-night-coverage-economy-sim.md``.
"""

from __future__ import annotations

import inspect
from dataclasses import replace
from functools import lru_cache
from types import ModuleType, SimpleNamespace

import pytest

from games.dnd.sim import menu_sim
from games.exploration.quest import catalog
from games.exploration.quest.models import RewardBundle
from games.exploration.survival import sim as survival_sim
from games.fishing.sim import catch_sim
from games.mining.sim import encounters_sim
from games.shared.sim import economy_sim

# Every shipped sim module (mirrors the smoke registry's coverage).
SIM_MODULES: tuple[ModuleType, ...] = (
    economy_sim,
    menu_sim,
    catch_sim,
    encounters_sim,
    survival_sim,
)

# A tiny sweep — the witnesses doctor the report, the pinned bands don't matter.
_KW = dict(seeds=range(2), digs_per_seed=5, casts_per_seed=5)


@lru_cache(maxsize=1)
def _economy_report() -> economy_sim.EconomyReport:
    return economy_sim.run(**_KW)


def _bool_predicates(module: ModuleType) -> set[str]:
    """Names of module-level functions *defined in* ``module`` returning bool.

    All sim modules use ``from __future__ import annotations`` so the return
    annotation is normally the string ``"bool"``; the class object is accepted
    too so the enumeration survives a module dropping the future import.
    """
    found: set[str] = set()
    for name, obj in vars(module).items():
        if not inspect.isfunction(obj) or obj.__module__ != module.__name__:
            continue
        if obj.__annotations__.get("return") in ("bool", bool):
            found.add(name)
    return found


def enumerate_predicates() -> set[tuple[str, str]]:
    """(module name, predicate name) for every sim invariant predicate."""
    return {
        (module.__name__, name)
        for module in SIM_MODULES
        for name in _bool_predicates(module)
    }


# ---------------------------------------------------------------------------
# The witness registry. Key = (module name, predicate name). Each entry maps
# to (healthy, violate): ``healthy(monkeypatch)`` must return True (shipped
# state), ``violate(monkeypatch)`` must return False (constructed violation).
# ---------------------------------------------------------------------------


def _cap_bundle_violation() -> tuple[int, int, int]:
    cap = catalog.GLOBAL_MAX
    return (cap.global_xp + 1, cap.game_xp, cap.currency)


def _violate_global_cap(monkeypatch: pytest.MonkeyPatch) -> bool:
    report = _economy_report()
    doctored = replace(
        report, dnd=replace(report.dnd, per_completion_bundle=_cap_bundle_violation())
    )
    return economy_sim.all_bundles_within_global_cap(doctored)


def _violate_item_faucet(monkeypatch: pytest.MonkeyPatch) -> bool:
    report = _economy_report()
    doctored = replace(
        report, mining=replace(report.mining, native_currency_per_hour=1.0)
    )
    return economy_sim.item_faucets_mint_no_currency_or_xp(doctored)


def _violate_noop(monkeypatch: pytest.MonkeyPatch) -> bool:
    minting = SimpleNamespace(
        apply=lambda *, seed, player_id: SimpleNamespace(reward=object())
    )
    monkeypatch.setitem(economy_sim.effects.EFFECTS, "rest_noop", minting)
    return economy_sim.noop_paths_mint_nothing()


def _violate_menu_cap(monkeypatch: pytest.MonkeyPatch) -> bool:
    cap = catalog.GLOBAL_MAX
    over = RewardBundle(
        global_xp=cap.global_xp + 1, game_xp=cap.game_xp, currency=cap.currency
    )
    return menu_sim._reward_leq_global_max(over)


WITNESSES: dict[tuple[str, str], tuple] = {
    (economy_sim.__name__, "all_bundles_within_global_cap"): (
        lambda mp: economy_sim.all_bundles_within_global_cap(_economy_report()),
        _violate_global_cap,
    ),
    (economy_sim.__name__, "item_faucets_mint_no_currency_or_xp"): (
        lambda mp: economy_sim.item_faucets_mint_no_currency_or_xp(_economy_report()),
        _violate_item_faucet,
    ),
    (economy_sim.__name__, "noop_paths_mint_nothing"): (
        lambda mp: economy_sim.noop_paths_mint_nothing(),
        _violate_noop,
    ),
    (menu_sim.__name__, "_reward_leq_global_max"): (
        lambda mp: menu_sim._reward_leq_global_max(catalog.GLOBAL_MAX),
        _violate_menu_cap,
    ),
}

_IDS = [f"{mod.rsplit('.', 1)[-1]}::{name}" for mod, name in sorted(WITNESSES)]
_SORTED_KEYS = sorted(WITNESSES)


# ---------------------------------------------------------------------------
# Completeness — enumeration ↔ registry, both directions.
# ---------------------------------------------------------------------------


def test_every_enumerated_predicate_has_a_witness() -> None:
    missing = enumerate_predicates() - set(WITNESSES)
    assert not missing, (
        "invariant predicate(s) without a registered violation witness "
        f"(dead detector until proven trippable): {sorted(missing)}"
    )


def test_registry_has_no_stale_witnesses() -> None:
    stale = set(WITNESSES) - enumerate_predicates()
    assert not stale, (
        f"witness(es) registered for predicates that no longer exist: {sorted(stale)}"
    )


def test_enumeration_sees_the_known_anchor_predicates() -> None:
    # Guards the enumerator itself: if annotation scanning ever rots to
    # yielding nothing, these documented anchors make it fail loudly.
    enumerated = enumerate_predicates()
    for anchor in (
        (economy_sim.__name__, "all_bundles_within_global_cap"),
        (economy_sim.__name__, "item_faucets_mint_no_currency_or_xp"),
        (economy_sim.__name__, "noop_paths_mint_nothing"),
        (menu_sim.__name__, "_reward_leq_global_max"),
    ):
        assert anchor in enumerated, anchor


# ---------------------------------------------------------------------------
# Per-predicate: shipped state passes, the witness trips.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("key", _SORTED_KEYS, ids=_IDS)
def test_shipped_state_keeps_predicate_true(
    key: tuple[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    healthy, _ = WITNESSES[key]
    assert healthy(monkeypatch) is True, key


@pytest.mark.parametrize("key", _SORTED_KEYS, ids=_IDS)
def test_witness_makes_predicate_trip(
    key: tuple[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    _, violate = WITNESSES[key]
    assert violate(monkeypatch) is False, key
