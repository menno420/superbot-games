"""Deterministic per-spot seed helper for fishing — an INDEPENDENT stream.

:func:`fishing_seed` mixes a fishing world *seed* with a fishing *spot id* into a stable
64-bit value seeding the catch resolver's deterministic-default RNG. It is built on the
shared splitmix64 seam (:func:`games.shared.rng.mix64` — the **mining family** the mining
grid pinned, ``games.mining.core.grid`` / ``encounters``), plus a fishing-domain salt
(:data:`_FISHING_SALT`) so the fishing stream is *independent* of any mining stream at a
coincidentally-equal base seed (mixing the same seed twice with no salt would correlate
the two rolls). Integer-only, so it never touches Python's per-process string-hash
randomisation — ``(seed, spot_id)`` maps to the identical seed across processes (the same
property the mining grid unit-tests with a subprocess check).

The ``spot_id`` is a free-form string ("dock", "deep_lake", …); it is folded in through
its stable byte encoding, so a spot is identified by name, not by coordinates.

Sourced from the shared seam (``docs/ideas/shared-deterministic-rng-seam-2026-07-10.md``).
This module used to hand-roll its own byte-identical copy of the splitmix64 mixing step —
the third such copy in-repo (mining grid, mining encounters, fishing) that #150 named a
promotion candidate. #150 extracted the mix into :mod:`games.shared.rng`; fishing now
consumes it, deleting the duplicate. The salt + ``spot_id`` byte-fold below are the only
fishing-specific logic that remains local.
"""

from __future__ import annotations

from games.shared import rng as shared_rng

# A fishing-domain salt so the fishing stream is independent of the mining streams that
# share the same splitmix64 family (an arbitrary fixed 64-bit odd constant).
_FISHING_SALT = 0x9E6C63C0B2A5D3F1


def fishing_seed(seed: int, spot_id: str) -> int:
    """Deterministic 64-bit seed for a cast at *spot_id* in world *seed*.

    Process-independent (integer + fixed-byte-encoding only, never ``hash(str)``): the
    same ``(seed, spot_id)`` yields the same value in every interpreter. Folds the
    fishing salt so the stream does not correlate with a mining stream at an equal seed.
    """
    h = (seed & shared_rng.MASK64) ^ _FISHING_SALT
    h = shared_rng.mix64(h)
    for byte in spot_id.encode("utf-8"):
        h = shared_rng.mix64(h ^ byte)
    return h & shared_rng.MASK64


__all__ = ["fishing_seed"]
