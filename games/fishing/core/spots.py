"""Fishing spots (biomes) — THE SPOT DATA (data rows only, no mechanics).

Where you fish biases *what* you catch. Every fishing spot — its display name, emoji,
flavour line, and its **catch profile** (how it re-weights the species table plus a
per-spot bite modifier) — lives here as **data**, keyed on a *neutral* string id
(``"tide_pool"``, ``"dock"``, ``"deep_water"``). This mirrors
:mod:`games.fishing.core.species`: the resolver in :mod:`games.fishing.core.catch` keys
every mechanic on those ids and reads the numbers/strings off these rows; it never
hard-codes a spot name in a logic branch. Re-theme or re-tune a biome — swap ``"dock"``
for ``"harbor"``, change an emoji, nudge a weight, add a row — by editing this table
alone, with zero change to the catch logic (Q-0267 theme-readiness, the same shape
mining's ore/depth tables use).

A spot row (:class:`Spot`) carries:

* ``spot_id`` — the neutral key mechanics use (never shown raw to a player).
* ``name`` / ``emoji`` / ``flavor`` — the display nouns (the only re-theme surface),
  assembled into narration from DATA alongside the species row's nouns.
* ``weight_mult`` — the **catch profile**: a ``{species_id: multiplier}`` map applied on
  top of each species' ``rarity_weight`` (a species not named defaults to ``1.0``). This
  is the balance data that makes a spot favour the small/common tail or the big/rare tail.
  Every multiplier is **strictly positive** (:func:`Spot.__post_init__` enforces it), so a
  spot can *bias* the distribution but never *gate* a species out — fair access per spot
  (Q-0039/Q-0190, no pay-to-win).
* ``bite_bias`` — an additive nudge to the base bite chance (calm shallows bite readily,
  cold deep water is stingier). The resolver clamps the final chance to an honest band so
  a negative bias can never kill bites entirely.

The **default / neutral** profile (:data:`DEFAULT_SPOT`) carries an empty ``weight_mult``
and ``bite_bias`` 0.0 — an exact identity. An unknown or ``None`` ``spot_id`` falls back to
it (honest, no raise, no advantage), and — because multiplying a weight by ``1.0`` and
adding ``0.0`` to the bite chance are exact IEEE operations — a cast at the default profile
is **byte-identical** to the pre-spots skeleton resolver. The shipped ``dock`` row is a
*named* neutral spot (identity profile), so the skeleton's ``dock``-keyed determinism
fixtures stay byte-identical while the flanking biomes carry the bias.

Pure data: no imports beyond the stdlib dataclass. The table is deliberately small (three
spots) so the data-driven-ness is demonstrable and the sim bounds are stable; grow it by
adding rows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True)
class Spot:
    """One fishing spot / biome — a pure data row (display nouns + balance numbers)."""

    spot_id: str  # neutral mechanic key (e.g. "deep_water") — never shown raw
    name: str  # display noun (the re-theme surface)
    emoji: str  # display glyph
    flavor: str  # short flavour line, assembled into narration from DATA
    # The catch profile: per-species weight multipliers over rarity_weight. A species not
    # named here defaults to 1.0; every named multiplier must be > 0 (bias, never gate).
    weight_mult: Mapping[str, float] = field(default_factory=dict)
    # Additive nudge to the base bite chance (before the honest clamp in the resolver).
    bite_bias: float = 0.0

    def __post_init__(self) -> None:
        # Fair-access invariant: a spot can down-weight a species but never zero it out —
        # every species stays reachable at every spot (no gating, no pay-to-win).
        for sid, mult in self.weight_mult.items():
            if mult <= 0.0:
                raise ValueError(
                    f"spot {self.spot_id!r}: weight multiplier for {sid!r} must be > 0 "
                    f"(a spot biases the catch, it never gates a species out); got {mult!r}"
                )
        # Freeze the mapping so a row's balance data cannot be mutated after construction
        # (the table is one source of truth; a caller reads it, never edits it in place).
        object.__setattr__(self, "weight_mult", MappingProxyType(dict(self.weight_mult)))

    def multiplier_for(self, species_id: str) -> float:
        """This spot's weight multiplier for *species_id* (``1.0`` if the row is silent)."""
        return self.weight_mult.get(species_id, 1.0)


# The spot table — three biomes. Neutral ids on the left; every player-visible noun on the
# right is data, swappable without touching catch.py. `dock` is the NEUTRAL middle spot (an
# identity profile), so the skeleton's dock-keyed determinism fixtures stay byte-identical;
# the flanking biomes carry the bias (shallow → small/common, deep → big/rare).
_SPOTS: tuple[Spot, ...] = (
    Spot(
        spot_id="tide_pool",
        name="Tide Pool",
        emoji="🪸",
        flavor="warm, shallow, easy water",
        # Shallow calm water: the small common fish crowd in; the big/rare tail is scarce.
        weight_mult={
            "minnow": 1.6,
            "bass": 1.2,
            "pike": 0.6,
            "legend_carp": 0.3,
        },
        bite_bias=0.10,  # fish bite readily in the warm shallows
    ),
    Spot(
        spot_id="dock",
        name="The Old Dock",
        emoji="🪝",
        flavor="the reliable, everyday spot",
        # Neutral / everyday: no weight overrides, no bite nudge — an exact identity that
        # reproduces the pre-spots skeleton resolver (keeps existing dock fixtures green).
        weight_mult={},
        bite_bias=0.0,
    ),
    Spot(
        spot_id="deep_water",
        name="Deep Water",
        emoji="🌊",
        flavor="cold, still, and full of monsters",
        # Deep cold water: the big/rare tail thrives; the little ones stay scarce (but never
        # locked out — minnow multiplier stays > 0, so a zero-gear angler still lands one).
        weight_mult={
            "minnow": 0.5,
            "bass": 0.9,
            "pike": 1.6,
            "legend_carp": 2.2,
        },
        bite_bias=-0.08,  # colder, stingier water — a mild, honest penalty
    ),
)

# Index by id for O(1) lookup — built from the table (still one source of truth).
_BY_ID: dict[str, Spot] = {s.spot_id: s for s in _SPOTS}

# The neutral default / fallback profile — an exact identity (empty weights, zero bias).
# An unknown or None spot_id resolves to this: honest, no raise, no advantage, and
# byte-identical to the pre-spots resolver. It is NOT in the table (it is the "no spot"
# baseline, not a fishable biome); the named `dock` row is the in-table neutral spot.
DEFAULT_SPOT: Spot = Spot(
    spot_id="_default",
    name="Open Water",
    emoji="🎣",
    flavor="open water, no particular character",
    weight_mult={},
    bite_bias=0.0,
)


def all_spots() -> tuple[Spot, ...]:
    """Every spot row, in table order (the biome table itself)."""
    return _SPOTS


def spot_ids() -> tuple[str, ...]:
    """Every neutral spot id (mechanics key on these)."""
    return tuple(s.spot_id for s in _SPOTS)


def get(spot_id: str) -> Spot:
    """The row for *spot_id* (raises ``KeyError`` if it is not in the table)."""
    return _BY_ID[spot_id]


def is_spot(spot_id: str) -> bool:
    """True if *spot_id* is a key in the table."""
    return spot_id in _BY_ID


def profile_for(spot_id: str | None) -> Spot:
    """The spot profile the resolver applies for *spot_id*.

    A known id returns its table row; an **unknown or ``None``** id falls back to the
    neutral :data:`DEFAULT_SPOT` (an exact identity) — honest, no raise, no advantage. This
    is the single lookup the resolver uses, so "unknown spot → default profile" is one
    place, not scattered branches.
    """
    if spot_id is None:
        return DEFAULT_SPOT
    return _BY_ID.get(spot_id, DEFAULT_SPOT)


__all__ = [
    "Spot",
    "DEFAULT_SPOT",
    "all_spots",
    "spot_ids",
    "get",
    "is_spot",
    "profile_for",
]
