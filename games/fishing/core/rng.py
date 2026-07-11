"""Deterministic per-spot seed helper for fishing — an INDEPENDENT stream.

:func:`fishing_seed` mixes a fishing world *seed* with a fishing *spot id* into a stable
64-bit value seeding the catch resolver's deterministic-default RNG. It uses the **same
splitmix64 family** the mining grid uses (``games.mining.core.grid._cell_seed`` /
``encounters.encounter_seed``), plus a fishing-domain salt (:data:`_FISHING_SALT`) so the
fishing stream is *independent* of any mining stream at a coincidentally-equal base seed
(mixing the same seed twice with no salt would correlate the two rolls). Integer-only, so
it never touches Python's per-process string-hash randomisation — ``(seed, spot_id)`` maps
to the identical seed across processes (the same property the mining grid unit-tests with
a subprocess check).

The ``spot_id`` is a free-form string ("dock", "deep_lake", …); it is folded in through
its stable byte encoding, so a spot is identified by name, not by coordinates.

**Promotion candidate.** This is the third hand-rolled copy of the splitmix64
``(seed, …)`` derivation in-repo (mining grid, mining encounters, now fishing). It is a
prime candidate for promotion to a shared ``games/shared/rng.py`` per
``docs/ideas/shared-deterministic-rng-seam-2026-07-10.md`` — deliberately re-rolled
cleanly here (a tiny public mix, NOT a copy of mining's private helpers) so the eventual
extraction has three concrete, byte-identical-tested call sites to migrate at once.
"""

from __future__ import annotations

# 64-bit mask — mirrors the mining grid's convention (Python ints are unbounded).
_MASK = (1 << 64) - 1

# splitmix64's odd-increment constant (the golden-ratio gamma). Same family as the
# mining grid mix; kept public/local so this module depends on no private grid helper.
_GAMMA = 0x9E3779B97F4A7C15

# A fishing-domain salt so the fishing stream is independent of the mining streams that
# share the same splitmix64 family (an arbitrary fixed 64-bit odd constant).
_FISHING_SALT = 0x9E6C63C0B2A5D3F1


def _mix(h: int) -> int:
    """One splitmix64-style mixing step on a 64-bit accumulator (integer-only)."""
    h &= _MASK
    return (h + _GAMMA + ((h << 6) & _MASK) + (h >> 2)) & _MASK


def fishing_seed(seed: int, spot_id: str) -> int:
    """Deterministic 64-bit seed for a cast at *spot_id* in world *seed*.

    Process-independent (integer + fixed-byte-encoding only, never ``hash(str)``): the
    same ``(seed, spot_id)`` yields the same value in every interpreter. Folds the
    fishing salt so the stream does not correlate with a mining stream at an equal seed.
    """
    h = (seed & _MASK) ^ _FISHING_SALT
    h = _mix(h)
    for byte in spot_id.encode("utf-8"):
        h = _mix(h ^ byte)
    return h & _MASK


__all__ = ["fishing_seed"]
