"""Fishing economy — the V043 sim-pinned sell + progression curves (pure data/math).

Every constant here is copied VERBATIM from sim-lab **VERDICT 043**
(APPROVE-WITH-CONSTANTS), relayed into this repo as ORDER 007 item (2) in
``control/inbox.md`` @ ``d6a9526`` (landed via PR #80; sim-lab ``afe18f3``
``control/outbox.md`` VERDICT 043). Nothing in this module is invented,
rolled, or re-derived — this closes the fishing-economy-tuning SIM-REQUEST
(``control/outbox.md``) with sim-backed numbers:

* **Sell curve** — per-species sell values in coins:
  minnow 8 · bass 13 · pike 27 · legend_carp 80.
* **Progression curve** — ``ProgressionDelta.game_xp = size_rank`` per catch
  (wired in :mod:`games.fishing.inventory.adapter`); advancing FROM level ``L``
  costs ``xp_to_next(L) = 50·L``; milestone SURFACES at L10 and L25.
* **STAT-NEUTRAL levels** — a fishing level is a progression readout ONLY. It
  never feeds ``fishing_power`` / ``bite_luck`` or any other mechanic lever;
  nothing in this module is read by the catch resolver.
* **Sell-OR-cook, never both** — one landed fish is consumed by exactly one
  economy leg. The seam (:func:`services.fishing_workflow.sell`) enforces this
  structurally by debiting the fish from the haul when it is sold; a future
  cook leg must consume from the same haul the same way.

Verdict anchor (for the record, not enforced here): 4.42–10.20 coins/energy by
(spot, tier) × 360 energy/h.

Pure and stdlib-only: data + integer math, no IO, no RNG, no game imports (the
tests pin that ``SELL_VALUES`` covers exactly the ``species.py`` table).
"""

from __future__ import annotations

# --- Sell curve (VERDICT 043, verbatim) -------------------------------------
# Per-species sell value in coins. Keys are the neutral species ids from
# ``species.py``; values are the sim-pinned constants, never scaled here.
SELL_VALUES: dict[str, int] = {
    "minnow": 8,
    "bass": 13,
    "pike": 27,
    "legend_carp": 80,
}

# --- Progression curve (VERDICT 043, verbatim) ------------------------------
#: XP cost to advance FROM level ``L`` to ``L+1`` is ``XP_PER_LEVEL * L``.
XP_PER_LEVEL: int = 50

#: Levels at which a milestone SURFACES (a message/readout, never a stat).
MILESTONE_LEVELS: tuple[int, ...] = (10, 25)

#: A fresh angler's level (levels are 1-based; the curve starts at L1).
BASE_LEVEL: int = 1


def sell_value(species_id: str) -> int:
    """The sim-pinned sell value (coins) for one fish of *species_id*.

    Raises ``KeyError`` for an unknown species — the curve is defined exactly
    over the ``species.py`` table (callers guard with :func:`is_sellable`).
    """
    return SELL_VALUES[species_id]


def is_sellable(species_id: str) -> bool:
    """True iff *species_id* has a sim-pinned sell value."""
    return species_id in SELL_VALUES


def xp_to_next(level: int) -> int:
    """XP needed to advance FROM *level* to *level*+1 — ``50·L``, verbatim V043."""
    if level < BASE_LEVEL:
        raise ValueError(f"level must be >= {BASE_LEVEL}, got {level!r}")
    return XP_PER_LEVEL * level


def cumulative_xp_for(level: int) -> int:
    """Total game_xp required to REACH *level* from a fresh L1 angler.

    The closed form of summing ``xp_to_next`` over L1..L-1:
    ``sum_{k=1}^{L-1} 50·k = 25·L·(L-1)``. Derived from the V043 curve, not a
    new constant.
    """
    if level < BASE_LEVEL:
        raise ValueError(f"level must be >= {BASE_LEVEL}, got {level!r}")
    return XP_PER_LEVEL * (level - 1) * level // 2


def level_for_xp(total_xp: int) -> int:
    """The level a *total_xp* pool has reached (STAT-NEUTRAL readout).

    The largest ``L`` with ``cumulative_xp_for(L) <= total_xp``; a negative
    pool clamps to :data:`BASE_LEVEL` (levels never go below the base).
    """
    if total_xp < 0:
        return BASE_LEVEL
    level = BASE_LEVEL
    while cumulative_xp_for(level + 1) <= total_xp:
        level += 1
    return level


def milestones_crossed(prev_xp: int, new_xp: int) -> tuple[int, ...]:
    """The V043 milestone levels (L10/L25) crossed moving *prev_xp* → *new_xp*.

    A milestone SURFACES when the level readout passes it — this returns the
    milestone levels newly reached so a seam/CLI can announce them. Purely a
    surfacing helper: crossing a milestone changes NO mechanic (stat-neutral).
    """
    prev_level = level_for_xp(prev_xp)
    new_level = level_for_xp(new_xp)
    return tuple(m for m in MILESTONE_LEVELS if prev_level < m <= new_level)


__all__ = [
    "SELL_VALUES",
    "XP_PER_LEVEL",
    "MILESTONE_LEVELS",
    "BASE_LEVEL",
    "sell_value",
    "is_sellable",
    "xp_to_next",
    "cumulative_xp_for",
    "level_for_xp",
    "milestones_crossed",
]
