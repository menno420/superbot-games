"""Spot biomes — the spot DATA drives the catch, keyed on neutral ids, fair per spot.

Proves the Q-0267 shape a second time for spots: every spot id is neutral and present in
the ``spots.py`` table; each spot's catch profile *biases* the species weighting but never
*gates* a species out (the common species stay reachable at zero gear at every spot);
swapping a spot data row changes the catch distribution but not the determinism; and an
unknown / ``None`` spot_id falls back to the neutral default profile with no raise.
"""

from __future__ import annotations

import random

from games.fishing.core import catch, species, spots


# --- the spot table is neutral-id data --------------------------------------

def test_every_spot_id_is_neutral_and_in_the_table() -> None:
    for spot in spots.all_spots():
        sid = spot.spot_id
        # Neutral snake_case ids (lowercase, underscores/alnum only) — never a display noun.
        assert sid == sid.lower()
        assert sid.replace("_", "").isalnum(), sid
        assert spots.is_spot(sid)
        assert sid in spots.spot_ids()
        # A display name distinct from the id proves nouns live in data, not in the key.
        assert spot.name != sid


def test_spot_ids_match_the_intended_biomes() -> None:
    # The shipped biomes (neutral ids); dock is the neutral middle spot.
    assert set(spots.spot_ids()) == {"tide_pool", "dock", "deep_water"}


def test_dock_is_the_neutral_identity_profile() -> None:
    # dock carries no weight overrides and no bite nudge — an exact identity, so the
    # skeleton's dock-keyed determinism fixtures stay byte-identical for the mechanic outcome.
    dock = spots.get("dock")
    assert dict(dock.weight_mult) == {}
    assert dock.bite_bias == 0.0
    for sid in species.species_ids():
        assert dock.multiplier_for(sid) == 1.0


# --- fair access per spot (no pay-to-win, no gating) ------------------------

def test_every_spot_profile_keeps_all_species_reachable() -> None:
    # Fair-access invariant: every named multiplier is strictly positive, so no spot can
    # zero a species out of its weighting (bias, never gate). Silent species default to 1.0.
    for spot in (*spots.all_spots(), spots.DEFAULT_SPOT):
        for sid in species.species_ids():
            assert spot.multiplier_for(sid) > 0.0, (spot.spot_id, sid)


def test_a_nonpositive_multiplier_is_rejected() -> None:
    # The data model enforces the fair-access invariant at construction — a gating (≤0)
    # multiplier is a ValueError, not a silently-shipped lockout.
    import pytest

    with pytest.raises(ValueError):
        spots.Spot(spot_id="rigged", name="Rigged", emoji="x", flavor="x",
                   weight_mult={"minnow": 0.0})


def test_zero_gear_lands_the_common_species_at_every_spot() -> None:
    # A bare angler (no gear) still lands the common species in quantity at every biome —
    # even the deep-water spot that biases hard toward the rare tail never gates minnow out.
    from games.mining.core.equipment import EffectiveStats

    for spot_id in spots.spot_ids():
        counts: dict[str, int] = {}
        for s in range(2000):
            o = catch.resolve_cast(s, spot_id, EffectiveStats())
            if o.bit and o.catch is not None:
                counts[o.catch.species_id] = counts.get(o.catch.species_id, 0) + 1
        assert counts.get("minnow", 0) > 0, spot_id
        assert counts.get("bass", 0) > 0, spot_id


# --- the spot profile actually biases the distribution ----------------------

def _dist(spot_id: str, n: int = 3000) -> dict[str, int]:
    from games.mining.core.equipment import EffectiveStats

    counts: dict[str, int] = {}
    for s in range(n):
        o = catch.resolve_cast(s, spot_id, EffectiveStats())
        if o.bit and o.catch is not None:
            counts[o.catch.species_id] = counts.get(o.catch.species_id, 0) + 1
    return counts


def _rare_share(counts: dict[str, int]) -> float:
    rare = tuple(s.species_id for s in species.all_species() if s.size_rank >= 3)
    total = sum(counts.values())
    return sum(counts.get(r, 0) for r in rare) / total if total else 0.0


def test_spots_bias_the_rare_tail_in_the_expected_order() -> None:
    # Deep water favours the big/rare tail; the tide pool suppresses it; dock sits between —
    # the ordering is driven purely by the spots.py weight profiles at zero gear.
    tide = _rare_share(_dist("tide_pool"))
    dock = _rare_share(_dist("dock"))
    deep = _rare_share(_dist("deep_water"))
    assert tide < dock < deep


def test_swapping_a_spot_row_changes_weighting_but_not_determinism(monkeypatch) -> None:
    # Determinism is a property of the resolver + data, not of a fixed row: with the shipped
    # deep_water row the distribution favours the rare tail; swap the row's weight profile
    # for the tide-pool-style one and the distribution flips — yet each configuration is
    # itself perfectly reproducible (same seed → same cast).
    baseline = _rare_share(_dist("deep_water"))

    swapped_row = spots.Spot(
        spot_id="deep_water",
        name="Deep Water",
        emoji="🌊",
        flavor="now a shallow-style profile",
        weight_mult={"minnow": 1.6, "bass": 1.2, "pike": 0.6, "legend_carp": 0.3},
        bite_bias=0.10,
    )
    monkeypatch.setitem(spots._BY_ID, "deep_water", swapped_row)

    swapped = _rare_share(_dist("deep_water"))
    assert swapped < baseline  # the data swap moved the distribution off the rare tail

    # …and the swapped configuration is still deterministic (data-driven, not stochastic).
    a = catch.resolve_cast(4242, "deep_water")
    b = catch.resolve_cast(4242, "deep_water")
    assert a == b


# --- unknown / None spot_id → the neutral default profile -------------------

def test_unknown_spot_id_falls_back_to_default_profile_no_raise() -> None:
    # An id not in the table resolves to the neutral default (an exact identity), no raise.
    assert spots.profile_for("no_such_spot") is spots.DEFAULT_SPOT
    assert spots.profile_for(None) is spots.DEFAULT_SPOT
    # And a cast at an unknown spot still returns a well-formed outcome (never raises).
    out = catch.resolve_cast(1, "no_such_spot")
    assert isinstance(out, catch.CastOutcome)


def test_unknown_spot_matches_the_default_identity_profile() -> None:
    # An unknown spot (default profile) and the in-table neutral dock spot share the SAME
    # identity profile. Injecting one shared rng stream neutralises the only other
    # spot-dependent input (the default seed folds the spot_id), so the mechanical outcome
    # (bit / catch / energy) is byte-identical — proving the fallback is a true identity, not
    # a special-cased branch. (Only the narration differs — it names the spot from DATA.)
    for s in range(200):
        a = catch.resolve_cast(0, "totally_unknown_spot", rng=random.Random(s))
        b = catch.resolve_cast(0, "dock", rng=random.Random(s))
        assert (a.bit, a.catch, a.energy_cost) == (b.bit, b.catch, b.energy_cost)


# --- determinism across spots -----------------------------------------------

def test_same_seed_spot_stats_is_byte_identical() -> None:
    from games.mining.core.equipment import compute_stats, CHARM

    stats = compute_stats({CHARM: "fishing charm"})
    a = catch.resolve_cast(777, "deep_water", stats)
    b = catch.resolve_cast(777, "deep_water", stats)
    assert a == b


def test_different_spots_diverge_in_distribution() -> None:
    # The same seeds at two different biomes yield different catch distributions (the spot
    # is a real lever on the outcome, not just seed entropy).
    assert _dist("tide_pool") != _dist("deep_water")


def test_injected_rng_still_applies_the_spot_profile() -> None:
    # Even on the live-roll path (injected rng), the spot profile biases the pick — the same
    # rng stream at two spots lands different species distributions over a sweep.
    def dist(spot_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for s in range(1500):
            o = catch.resolve_cast(0, spot_id, rng=random.Random(s))
            if o.bit and o.catch is not None:
                counts[o.catch.species_id] = counts.get(o.catch.species_id, 0) + 1
        return counts

    assert _rare_share(dist("tide_pool")) < _rare_share(dist("deep_water"))


# --- banner grammar: the template's article never doubles the name's --------

def _first_outcome(spot_id: str, *, bit: bool) -> catch.CastOutcome:
    """The first deterministic default-stream cast at *spot_id* with the wanted bite."""
    for seed in range(200):
        o = catch.resolve_cast(seed, spot_id)
        if o.bit is bit:
            return o
    raise AssertionError(f"no {'bite' if bit else 'no-bite'} cast in 200 seeds at {spot_id!r}")


def test_bite_banner_dedupes_article_for_the_dock() -> None:
    # The dock's DATA name carries its own article ("The Old Dock"); the "At the …"
    # template must not double it (regression: "🪝 At the The Old Dock — …").
    o = _first_outcome("dock", bit=True)
    assert o.narration.startswith("🪝 At the Old Dock — ")
    assert "At the The" not in o.narration


def test_bite_banner_unchanged_for_a_non_the_spot() -> None:
    # A name WITHOUT its own article renders through the same template untouched.
    o = _first_outcome("tide_pool", bit=True)
    assert o.narration.startswith("🪸 At the Tide Pool — ")


def test_no_bite_line_dedupes_article_for_the_dock() -> None:
    # The no-bite sibling template ("cast into the …") de-dupes the same way
    # (regression: "You cast into the the old dock…").
    o = _first_outcome("dock", bit=False)
    assert o.narration == "🎣 You cast into the old dock… but nothing bites this time."
    assert "the the" not in o.narration
