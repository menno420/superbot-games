"""Fishing species — THE THEME DATA (data rows only, no mechanics).

Every player-visible noun in the fishing domain — a species' name, emoji, flavour
line, how big it gets, and how rare it is — lives here as **data**, keyed on a
*neutral* string id (``"minnow"``, ``"bass"``, ``"pike"``, ``"legend_carp"``). The
resolver in :mod:`games.fishing.core.catch` keys every mechanic on those ids and reads
the numbers/strings off these rows; it never hard-codes a species name in a logic
branch. This is the Q-0267 **theme-readiness** shape (the same one mining uses for its
ore/depth tables): re-theme the game — swap "bass" for "star-koi", change an emoji,
add a row — by editing this table alone, with zero change to the catch logic or its
tests' *mechanics* (the theme tests key on the neutral ids, not the display strings).

A species row carries:

* ``species_id`` — the neutral key mechanics use (never shown raw to a player).
* ``name`` / ``emoji`` / ``flavor`` — the display nouns (the only re-theme surface).
* ``size_rank`` — 1-based "how big does this get" tier; the resolver scales a caught
  fish's reported size off this, and ``fishing_power`` biases toward higher ranks.
* ``rarity_weight`` — the base weighted-pick weight (bigger = more common). Rarer
  species have smaller weights; ``fishing_power`` shifts weight toward the rare tail.

Pure data: no imports beyond the stdlib dataclass. The table is deliberately small
(four species) so the data-driven-ness is demonstrable and the sim bounds are stable;
grow it by adding rows.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Species:
    """One catchable species — a pure data row (display nouns + balance numbers)."""

    species_id: str  # neutral mechanic key (e.g. "legend_carp") — never shown raw
    name: str  # display noun (the re-theme surface)
    emoji: str  # display glyph
    flavor: str  # short flavour line, assembled into narration from DATA
    size_rank: int  # 1-based size tier (bigger fish = higher rank)
    rarity_weight: float  # base weighted-pick weight (bigger = more common)


# The species table — ordered common → legendary. Neutral ids on the left; every
# player-visible noun on the right is data, swappable without touching catch.py.
_SPECIES: tuple[Species, ...] = (
    Species(
        species_id="minnow",
        name="Minnow",
        emoji="🐟",
        flavor="a tiny silver flash, barely a bite",
        size_rank=1,
        rarity_weight=50.0,
    ),
    Species(
        species_id="bass",
        name="Bass",
        emoji="🐠",
        flavor="a solid, scrappy fighter",
        size_rank=2,
        rarity_weight=30.0,
    ),
    Species(
        species_id="pike",
        name="Pike",
        emoji="🐡",
        flavor="a long, toothy ambush predator",
        size_rank=3,
        rarity_weight=15.0,
    ),
    Species(
        species_id="legend_carp",
        name="Legendary Carp",
        emoji="🎏",
        flavor="the pond's fabled giant — a catch to boast about",
        size_rank=4,
        rarity_weight=5.0,
    ),
)

# Index by id for O(1) lookup — built from the table (still one source of truth).
_BY_ID: dict[str, Species] = {s.species_id: s for s in _SPECIES}

# The largest size_rank in the table — the resolver scales reported sizes against it
# (read off the data so adding a bigger species needs no logic change).
MAX_SIZE_RANK: int = max(s.size_rank for s in _SPECIES)


def all_species() -> tuple[Species, ...]:
    """Every species row, ordered common → rare (the theme table itself)."""
    return _SPECIES


def species_ids() -> tuple[str, ...]:
    """Every neutral species id (mechanics key on these)."""
    return tuple(s.species_id for s in _SPECIES)


def get(species_id: str) -> Species:
    """The row for *species_id* (raises ``KeyError`` if it is not in the table)."""
    return _BY_ID[species_id]


def is_species(species_id: str) -> bool:
    """True if *species_id* is a key in the table."""
    return species_id in _BY_ID


__all__ = [
    "Species",
    "MAX_SIZE_RANK",
    "all_species",
    "species_ids",
    "get",
    "is_species",
]
