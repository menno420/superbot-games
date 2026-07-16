"""Shared deterministic-RNG seam — the audited splitmix64 `(seed, coords…)` mix.

One place for the integer-only, process-independent hash the mining world was
built on, so every game plugin gets byte-reproducible, subprocess-stable
determinism from a single implementation instead of hand-rolling its own
(``docs/ideas/shared-deterministic-rng-seam-2026-07-10.md``).

This is the **mining family** of the mix — lifted **verbatim** from
``games.mining.core.grid._cell_seed`` (and the byte-identical private copy that
used to live in ``games.mining.core.encounters``): a per-element xor-then-mix
over a 64-bit accumulator, seeded with the world seed. It is deterministic
*across processes* because it touches only integer arithmetic — never Python's
per-process ``hash(str)`` randomisation — so the same ``(seed, coords…)`` maps to
the same value in every interpreter (the property the mining grid unit-tests with
a subprocess check).

Note this is the *mining* splitmix64 family (``<<6 … >>2`` mixing on the
golden-ratio gamma), distinct from the *canonical* splitmix64 that
``games.exploration.quest.rng`` uses (the ``0xBF58476D…`` finaliser variant).
They share a name and a gamma constant but are different algorithms; callers that
need byte-compatibility with the mining grid derive from **this** module.

Pure: stdlib-only, no global state, no wall-clock, no I/O.
"""

from __future__ import annotations

# 64-bit mask for the stable coordinate hash (Python ints are unbounded).
MASK64 = (1 << 64) - 1

# splitmix64's odd-increment constant (the golden-ratio gamma).
_GAMMA = 0x9E3779B97F4A7C15


def mix64(h: int) -> int:
    """One splitmix64-style mixing step on a 64-bit accumulator (integer-only).

    Masks the input first, so it is safe to call on an unmasked ``h``; the result
    is always within :data:`MASK64`. Byte-identical to the mixing step that was
    inlined in ``grid._cell_seed`` / ``encounters.encounter_seed``.
    """
    h &= MASK64
    return (h + _GAMMA + ((h << 6) & MASK64) + (h >> 2)) & MASK64


def cell_seed(seed: int, *coords: int) -> int:
    """A stable 64-bit hash of ``(seed, coords…)`` — deterministic across processes.

    Built from integer arithmetic only (the splitmix64-style :func:`mix64`), so it
    never depends on Python's per-process string-hash randomisation; negative
    coordinates wrap deterministically under :data:`MASK64`. Each coordinate is
    xored into the accumulator, then mixed — the exact ``(seed, x, y, z)``
    convention the mining grid pinned.
    """
    h = seed & MASK64
    for value in coords:
        h = mix64(h ^ (value & MASK64))
    return h


__all__ = ["MASK64", "mix64", "cell_seed"]
