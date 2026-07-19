"""Theme data — outcomes are driven by ``species.py`` DATA, mechanics key on neutral ids.

Proves the Q-0267 theme-readiness shape: every player-visible noun lives in the species
table as data, the resolver keys mechanics on neutral string ids, and narration is
assembled from the picked row's data (not hard-coded per species). Re-theming is a
data-only edit.
"""

from __future__ import annotations

from games.fishing.core import catch, species


def _bites(seed_range: range, spot: str = "dock", stats: object = None) -> list[catch.CastOutcome]:
    out = [catch.resolve_cast(s, spot, stats) for s in seed_range]  # type: ignore[arg-type]
    return [o for o in out if o.bit and o.catch is not None]


def test_every_catch_species_is_a_key_in_the_table() -> None:
    # Mechanics only ever produce ids that exist in the data table.
    for o in _bites(range(500)):
        assert o.catch is not None
        assert species.is_species(o.catch.species_id)
        assert o.catch.species_id in species.species_ids()


def test_all_table_species_are_reachable() -> None:
    # Every data row is a reachable catch (adding a row adds a reachable catch; removing
    # one removes it) — the resolver draws its outcomes from the table, nothing else.
    from games.mining.core.equipment import compute_stats, CHARM

    geared = compute_stats({CHARM: "master angler charm"})
    reachable = {o.catch.species_id for o in _bites(range(2000), stats=geared) if o.catch}
    assert reachable == set(species.species_ids())


def test_narration_is_assembled_from_species_data() -> None:
    # The narration for a bite contains the picked row's DATA (emoji, flavor, name) —
    # proving copy comes from the table, not a hard-coded per-species string.
    found = False
    for o in _bites(range(300)):
        assert o.catch is not None
        row = species.get(o.catch.species_id)
        assert row.emoji in o.narration
        assert row.flavor in o.narration
        assert row.name in o.narration
        found = True
    assert found  # the sweep actually landed at least one fish


def test_mechanics_key_on_neutral_ids_not_display_nouns() -> None:
    # The mechanic key (species_id) is a neutral id distinct from the display name, so
    # logic never depends on a player-visible noun. Demonstrated on the legendary row.
    legend = species.get("legend_carp")
    assert legend.species_id == "legend_carp"  # neutral snake_case id
    assert legend.name == "Legendary Carp"  # display noun differs from the id
    # A Catch carries the id, never the display name.
    for o in _bites(range(2000), stats=_master()):
        assert o.catch is not None
        assert o.catch.species_id in species.species_ids()


def _master() -> object:
    from games.mining.core.equipment import compute_stats, CHARM

    return compute_stats({CHARM: "master angler charm"})


# ---------------------------------------------------------------------------
# Display-name → id resolver (decision #5): a display name resolves to its
# neutral id, id match is preferred, and an unknown token returns None.
# ---------------------------------------------------------------------------
def test_resolve_exact_id_wins() -> None:
    # An exact neutral id resolves to itself, case-insensitively.
    assert species.resolve("legend_carp") == "legend_carp"
    assert species.resolve("Legend_Carp") == "legend_carp"
    assert species.resolve("bass") == "bass"


def test_resolve_multiword_display_name_case_insensitive() -> None:
    # A multi-word display name resolves to its neutral id regardless of case.
    assert species.resolve("Legendary Carp") == "legend_carp"
    assert species.resolve("legendary carp") == "legend_carp"
    assert species.resolve("LEGENDARY CARP") == "legend_carp"


def test_resolve_single_word_display_name() -> None:
    # A single-word display name ("Bass") resolves to its id ("bass"); here the
    # display name folds to the same token as the id, but the resolver still
    # honours the display-name path for names that differ from their id.
    assert species.resolve("Minnow") == "minnow"
    assert species.resolve("Pike") == "pike"


def test_resolve_unknown_returns_none() -> None:
    # A token that matches neither an id nor a display name resolves to None,
    # leaving the caller its honest "unknown species" no-op.
    assert species.resolve("kraken") is None
    assert species.resolve("Giant Kraken") is None
    assert species.resolve("") is None
