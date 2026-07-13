"""Cross-domain economy sim — the whole-economy emission pins + global invariants.

Re-asserts the three named invariants (``GRANT_WITHIN_GLOBAL_CAP``,
``ITEM_FAUCET_MINTS_NO_CURRENCY``, ``NOOP_MINTS_NOTHING``) and the sim-pinned
per-domain emission bands over a smaller sweep, so a cross-domain balance
regression reddens CI. The full-scale evidence + pinned-table live in
``docs/design/economy-sim.md``.
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import replace
from types import SimpleNamespace

import pytest

from games.exploration.quest import catalog
from games.shared.inventory.interface import Grant, ProgressionDelta, Stack
from games.shared.sim import economy_sim as sim

# A smaller sweep than the sim default — fast, still stable at the pinned bands.
_KW = dict(seeds=range(8), digs_per_seed=300, casts_per_seed=300)


def test_all_bundles_within_global_cap() -> None:
    report = sim.run(**_KW)
    assert sim.all_bundles_within_global_cap(report) is True
    assert report.grant_within_global_cap is True

    # Directly: every quest tier bundle AND the dnd escort bundle <= GLOBAL_MAX.
    cap = (
        catalog.GLOBAL_MAX.global_xp,
        catalog.GLOBAL_MAX.game_xp,
        catalog.GLOBAL_MAX.currency,
    )
    for bundle in catalog.TIER_CAPS.values():
        tup = (bundle.global_xp, bundle.game_xp, bundle.currency)
        assert all(c <= limit for c, limit in zip(tup, cap)), tup
    assert report.dnd.per_completion_bundle is not None
    assert all(
        c <= limit for c, limit in zip(report.dnd.per_completion_bundle, cap)
    ), report.dnd.per_completion_bundle


def test_item_faucets_mint_no_currency_or_xp() -> None:
    report = sim.run(**_KW)
    assert sim.item_faucets_mint_no_currency_or_xp(report) is True
    for domain in (report.mining, report.fishing):
        assert domain.native_currency_per_hour == 0.0
        assert domain.native_global_xp_per_hour == 0.0
        assert domain.native_game_xp_per_hour == 0.0
        # Item faucets DO mint items.
        assert domain.items_per_hour > 0.0


def test_noop_paths_mint_nothing() -> None:
    # Resolves the real dnd/mining/fishing no-op paths through the shipped code.
    assert sim.noop_paths_mint_nothing() is True


def test_mining_emission_within_pinned_band() -> None:
    lo, hi = sim._MINING_ORE_PER_HOUR
    items_per_hour = sim.run(**_KW).mining.items_per_hour
    assert lo <= items_per_hour <= hi, items_per_hour


def test_fishing_emission_within_pinned_band() -> None:
    lo, hi = sim._FISHING_FISH_PER_HOUR
    items_per_hour = sim.run(**_KW).fishing.items_per_hour
    assert lo <= items_per_hour <= hi, items_per_hour


def test_report_is_deterministic_within_process() -> None:
    a = sim.run(**_KW)
    b = sim.run(**_KW)
    assert a == b


def test_report_is_deterministic_across_process() -> None:
    # A fresh interpreter (PYTHONHASHSEED randomised) must produce the identical
    # pinned emission values — proving the sweep never depends on str-hashing.
    report = sim.run(**_KW)
    inproc = (
        f"{report.mining.items_per_hour:.6f}|{report.fishing.items_per_hour:.6f}|"
        f"{report.dnd.per_completion_bundle}|{report.exploration.per_completion_bundle}|"
        f"{report.global_cap}"
    )
    code = (
        "from games.shared.sim import economy_sim as sim;"
        "r = sim.run(seeds=range(8), digs_per_seed=300, casts_per_seed=300);"
        "print(f'{r.mining.items_per_hour:.6f}|{r.fishing.items_per_hour:.6f}|"
        "{r.dnd.per_completion_bundle}|{r.exploration.per_completion_bundle}|{r.global_cap}')"
    )
    out = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=True,
        cwd=_repo_root(),
        env=_randomized_hashseed_env(),
    ).stdout.strip()
    assert out == inproc


# ---------------------------------------------------------------------------
# Detector FAIL paths — each named invariant must actually TRIP on a violating
# report/path, not just pass on the shipped one. Violations are constructed
# (dataclasses.replace / targeted monkeypatch); no shipped constant is edited.
# ---------------------------------------------------------------------------


def test_domains_property_orders_all_four() -> None:
    report = sim.run(**_KW)
    assert report.domains == (
        report.mining,
        report.fishing,
        report.dnd,
        report.exploration,
    )
    assert [d.domain for d in report.domains] == [
        "mining",
        "fishing",
        "dnd",
        "exploration",
    ]


def test_mean_surface_ore_coin_value_guards_empty_weights(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Shipped surface weights give a real positive coins/ore figure...
    assert sim._mean_surface_ore_coin_value() > 0.0
    # ...and an empty weight table (total weight 0) hits the guard, not a
    # ZeroDivisionError.
    monkeypatch.setattr(sim.rewards, "ore_weights_for_depth", lambda depth: {})
    assert sim._mean_surface_ore_coin_value() == 0.0


def test_item_faucet_invariant_trips_on_any_nonzero_mint() -> None:
    # A single nonzero currency/xp figure on EITHER item faucet must flip the
    # ITEM_FAUCET_MINTS_NO_CURRENCY invariant to False.
    report = sim.run(**_KW)
    for domain_attr in ("mining", "fishing"):
        for field_name in (
            "native_currency_per_hour",
            "native_global_xp_per_hour",
            "native_game_xp_per_hour",
        ):
            doctored = replace(
                report,
                **{
                    domain_attr: replace(
                        getattr(report, domain_attr), **{field_name: 1.0}
                    )
                },
            )
            assert sim.item_faucets_mint_no_currency_or_xp(doctored) is False, (
                domain_attr,
                field_name,
            )


@pytest.mark.parametrize("effect_id", ["rest_noop", "scout_narrate"])
def test_noop_invariant_trips_when_dnd_narrate_mints(
    effect_id: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # If a narrate-only dnd effect ever started minting, NOOP_MINTS_NOTHING
    # must go False.
    minting = SimpleNamespace(
        apply=lambda *, seed, player_id: SimpleNamespace(reward=object())
    )
    monkeypatch.setitem(sim.effects.EFFECTS, effect_id, minting)
    assert sim.noop_paths_mint_nothing() is False


def test_noop_invariant_trips_when_mining_baseline_mints(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    none_kind = sim.encounters.EncounterKind.NONE
    # A BARREN cell resolving to NONE but carrying rewards → trips.
    monkeypatch.setattr(
        sim.encounters,
        "resolve",
        lambda seed, cell: SimpleNamespace(kind=none_kind, rewards=(("stone", 1),)),
    )
    assert sim.noop_paths_mint_nothing() is False
    # A BARREN cell resolving to a non-NONE kind at all → also trips.
    loot_kind = sim.encounters.EncounterKind.LOOT_CACHE
    monkeypatch.setattr(
        sim.encounters,
        "resolve",
        lambda seed, cell: SimpleNamespace(kind=loot_kind, rewards=()),
    )
    assert sim.noop_paths_mint_nothing() is False


def test_noop_invariant_trips_when_fishing_noop_grants(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A too-tired cast granting an item stack → trips.
    monkeypatch.setattr(
        sim.fishing_adapter,
        "cast_to_grant",
        lambda outcome: Grant(items=(Stack(item="fish", qty=1),)),
    )
    assert sim.noop_paths_mint_nothing() is False
    # A too-tired cast granting progression (no items) → also trips.
    monkeypatch.setattr(
        sim.fishing_adapter,
        "cast_to_grant",
        lambda outcome: Grant(progression=ProgressionDelta(currency=1)),
    )
    assert sim.noop_paths_mint_nothing() is False


def test_noop_invariant_accepts_value_equal_empty_grant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The documented defensive branch: a freshly-constructed empty Grant is not
    # the EMPTY_GRANT sentinel by identity, but mints nothing → still passes.
    monkeypatch.setattr(
        sim.fishing_adapter, "cast_to_grant", lambda outcome: Grant()
    )
    assert sim.noop_paths_mint_nothing() is True


# ---------------------------------------------------------------------------
# format_report — the human-readable ledger rendering (previously 0% covered).
# ---------------------------------------------------------------------------


def test_format_report_pins_domain_rows_and_ceilings() -> None:
    report = sim.run(**_KW)
    text = sim.format_report(report)
    lines = text.splitlines()
    assert lines[0] == "CROSS-DOMAIN ECONOMY EMISSION (per active hour)"
    # Item faucets render their numeric energy-throttled ceiling; host-gated
    # domains render the literal "host".
    mining_row = next(l for l in lines if l.startswith("mining"))
    fishing_row = next(l for l in lines if l.startswith("fishing"))
    assert mining_row.split()[-1] == f"{sim._mining_action_ceiling():.0f}"
    assert fishing_row.split()[-1] == f"{sim._fishing_action_ceiling():.0f}"
    for host_gated in ("dnd", "exploration"):
        row = next(l for l in lines if l.startswith(host_gated))
        assert row.split()[-1] == "host"


def test_format_report_renders_invariant_flags_both_ways() -> None:
    report = sim.run(**_KW)
    text = sim.format_report(report)
    # The shipped economy passes all three named invariants...
    for name in (
        "GRANT_WITHIN_GLOBAL_CAP",
        "ITEM_FAUCET_MINTS_NO_CURRENCY",
        "NOOP_MINTS_NOTHING",
    ):
        assert f"{name}" in text
    assert text.count("PASS") == 3
    assert "FAIL" not in text
    # ...and a red report renders FAIL per flipped flag (rendering only — the
    # report object is doctored, no shipped behavior is touched).
    red = replace(
        report,
        grant_within_global_cap=False,
        item_faucet_mints_no_currency=False,
        noop_mints_nothing=False,
    )
    red_text = sim.format_report(red)
    assert red_text.count("FAIL") == 3
    assert "PASS" not in red_text


def test_format_report_lists_bundles_and_pinned_bands() -> None:
    report = sim.run(**_KW)
    text = sim.format_report(report)
    # Host-gated per-completion bundles + the one global cap.
    assert f"dnd          {report.dnd.per_completion_bundle}" in text
    assert (
        f"exploration  {report.exploration.per_completion_bundle}" in text
    )
    assert f"GLOBAL_MAX   {report.global_cap}" in text
    # Pinned bands echo the module constants and the observed per-hour figures.
    assert f"mining items/hr  {sim._MINING_ORE_PER_HOUR}" in text
    assert f"fishing items/hr {sim._FISHING_FISH_PER_HOUR}" in text
    assert f"(observed {report.mining.items_per_hour:.1f})" in text
    assert f"(observed {report.fishing.items_per_hour:.1f})" in text


def _repo_root() -> str:
    import os

    # tests/shared/sim/ -> repo root is three levels up.
    return os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )


def _randomized_hashseed_env() -> dict[str, str]:
    import os

    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "random"
    return env
