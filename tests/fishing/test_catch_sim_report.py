"""Catch-sim harness: the share/rare-tail helpers + the balance-report renderer.

``tests/fishing/test_catch_sim.py`` pins the sweep loop and the sim-pinned
outcome gradients; this module pins the pieces it leaves untested —
``CatchTierStats.species_share`` (with its zero-bites guard), ``_rare_ids``
(the size_rank ≥ 3 tail read off species DATA, not hard-coded), and
``format_report`` (header grammar, per-spot sections, the species-share
table, the cross-spot aggregate, the trailing energy line, and the guarded
zero-denominator renders). Tests only, at EXISTING constants. Mirrors
``tests/mining/test_encounters_sim.py``'s renderer-pin pattern (#104).
"""

from __future__ import annotations

from collections import Counter

from games.fishing.core import catch, species
from games.fishing.sim import catch_sim as sim


def _tiny_run() -> sim.SimReport:
    # The smallest deterministic sweep that still fills every (spot, tier)
    # bucket: 2 seeds × 3 spots × 2 casts × 3 tiers = 12 casts per tier.
    return sim.run(seeds=range(2), casts_per_spot=2)


# ---------------------------------------------------------------------------
# CatchTierStats.species_share — the per-species share of bites.
# ---------------------------------------------------------------------------
def test_species_share_is_the_fraction_of_bites() -> None:
    st = sim.CatchTierStats(
        casts=10, bites=4, species_counts=Counter({"minnow": 3, "bass": 1})
    )
    assert st.species_share("minnow") == 0.75
    assert st.species_share("bass") == 0.25
    # An id absent from the counter is a 0-share, not a KeyError.
    assert st.species_share("legend_carp") == 0.0


def test_species_share_with_zero_bites_is_zero_not_an_error() -> None:
    # The guard mirrors bite_rate/mean_size: an empty bucket reads as 0.0.
    st = sim.CatchTierStats(casts=5)
    assert st.species_share("minnow") == 0.0


# ---------------------------------------------------------------------------
# _rare_ids — the rare/big tail is derived from species DATA.
# ---------------------------------------------------------------------------
def test_rare_ids_are_exactly_the_size_rank_3_plus_species() -> None:
    expected = tuple(
        s.species_id for s in species.all_species() if s.size_rank >= 3
    )
    rare = sim._rare_ids()
    assert rare == expected
    # The tail is real and proper: non-empty, but never the whole table.
    assert rare
    assert set(rare) < set(species.species_ids())


# ---------------------------------------------------------------------------
# format_report — grammar and section order over a tiny deterministic sweep.
# ---------------------------------------------------------------------------
def test_report_header_lines_quote_the_sweep_and_the_species_data() -> None:
    report = _tiny_run()
    lines = sim.format_report(report).splitlines()
    assert lines[0] == f"casts per tier: {report.casts_per_tier:,}"
    assert lines[1] == f"spots: {', '.join(report.spots)}"
    assert lines[2] == f"species table: {', '.join(species.species_ids())}"
    assert lines[3] == f"rare tail (size_rank ≥ 3): {', '.join(sim._rare_ids())}"
    assert lines[4] == ""


def test_report_renders_one_section_per_spot_with_a_row_per_tier() -> None:
    report = _tiny_run()
    lines = sim.format_report(report).splitlines()
    for spot in report.spots:
        header = f"[{spot}] (bite rate · rare-tail share of bites · mean size):"
        assert header in lines, spot
        at = lines.index(header)
        # The tier rows immediately follow the spot header, in tier order.
        for offset, name in enumerate(report.tiers, start=1):
            assert lines[at + offset].startswith(f"  {name:<8} bite "), (spot, name)


def test_species_share_table_columns_follow_the_species_table() -> None:
    report = _tiny_run()
    text = sim.format_report(report)
    header = "    " + " " * 6 + "".join(f"{sid:>13}" for sid in species.species_ids())
    # One aligned column header per spot section, in species-table order.
    assert text.count(header) == len(report.spots)
    assert text.count("    species share of bites:") == len(report.spots)


def test_tier_row_grammar_matches_the_bucket_it_renders() -> None:
    report = _tiny_run()
    rare = sim._rare_ids()
    spot, name = report.spots[0], report.tiers[0]
    st = report.spot_tier(spot, name)
    expected = (
        f"  {name:<8} bite {st.bite_rate:6.2%}  rare {st.rare_share(rare):6.2%}  "
        f"size {st.mean_size:5.1f}  (bites={st.bites:,})"
    )
    lines = sim.format_report(report).splitlines()
    at = lines.index(f"[{spot}] (bite rate · rare-tail share of bites · mean size):")
    assert lines[at + 1] == expected


def test_aggregate_section_follows_every_spot_section() -> None:
    report = _tiny_run()
    lines = sim.format_report(report).splitlines()
    agg = lines.index("aggregate across spots (bite rate · rare-tail share · mean size):")
    for spot in report.spots:
        spot_at = lines.index(
            f"[{spot}] (bite rate · rare-tail share of bites · mean size):"
        )
        assert spot_at < agg, spot
    # One aggregate row per tier, in tier order, right after the header.
    for offset, name in enumerate(report.tiers, start=1):
        assert lines[agg + offset].startswith(f"  {name:<8} bite "), name


def test_energy_line_is_last_and_quotes_the_cast_cost() -> None:
    report = _tiny_run()
    lines = sim.format_report(report).splitlines()
    # Every cast costs exactly CAST_COST (pinned by the sim suite), so the
    # trailing economy line renders that constant.
    assert lines[-1] == f"mean energy cost per cast: {float(catch.CAST_COST):.2f}"


def test_format_report_is_pure_and_repeatable() -> None:
    report = _tiny_run()
    before = {key: Counter(st.species_counts) for key, st in report.by_spot_tier.items()}
    first = sim.format_report(report)
    second = sim.format_report(report)
    assert first == second
    # Rendering never mutates the report it reads.
    assert {k: st.species_counts for k, st in report.by_spot_tier.items()} == before


# ---------------------------------------------------------------------------
# format_report — guarded zero-denominator renders (hand-built reports).
# ---------------------------------------------------------------------------
def test_empty_report_renders_zeroes_without_error() -> None:
    lines = sim.format_report(sim.SimReport()).splitlines()
    assert lines[0] == "casts per tier: 0"
    # No spots/tiers → no sections; the aggregate header and the guarded
    # 0.00 energy mean still render (mean_energy_cost divides behind a guard).
    assert lines[-1] == "mean energy cost per cast: 0.00"


def test_zero_bite_bucket_renders_zero_rates_not_a_division_error() -> None:
    # A (spot, tier) bucket with casts but no bites: every rate the row
    # renders (bite_rate, rare_share, mean_size) is guarded to 0 — the
    # zero-denominator shape that bit encounters_sim (#106) is safe here.
    report = sim.SimReport(
        casts_per_tier=3,
        spots=("dock",),
        tiers=("fresh",),
        by_spot_tier={("dock", "fresh"): sim.CatchTierStats(casts=3)},
        by_tier={"fresh": sim.CatchTierStats(casts=3)},
    )
    lines = sim.format_report(report).splitlines()
    row = f"  {'fresh':<8} bite {0:6.2%}  rare {0:6.2%}  size {0.0:5.1f}  (bites=0)"
    # The same guarded row appears in the spot section and the aggregate.
    assert lines.count(row) == 2
