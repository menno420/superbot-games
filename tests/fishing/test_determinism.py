"""Determinism — (seed, spot_id) → a byte-identical cast; different seeds diverge.

Mirrors ``tests/mining/test_encounters.py``: the deterministic default stream is a pure
function of ``(seed, spot_id)`` (integer splitmix64, no str-hashing), re-checked across a
fresh interpreter; an injected rng overrides it for the live-roll path.
"""

from __future__ import annotations

import random
import subprocess
import sys

from games.fishing.core import catch


def test_resolve_is_deterministic_within_process() -> None:
    a = catch.resolve_cast(12345, "dock")
    b = catch.resolve_cast(12345, "dock")
    assert a == b
    assert isinstance(a, catch.CastOutcome)


def test_different_seeds_diverge() -> None:
    # Over many seeds the same spot yields a spread of outcomes (not one fixed cast).
    outs = {
        (o.bit, o.catch.species_id if o.catch else None, o.catch.size if o.catch else None)
        for s in range(80)
        for o in [catch.resolve_cast(s, "dock")]
    }
    assert len(outs) > 1


def test_different_spots_diverge() -> None:
    outs = {
        (o.bit, o.catch.species_id if o.catch else None)
        for spot in ("dock", "deep_lake", "reef", "river_bend", "pier")
        for o in [catch.resolve_cast(7, spot)]
    }
    assert len(outs) > 1


def test_resolve_process_independent() -> None:
    # A fresh interpreter (PYTHONHASHSEED randomised) must produce the identical cast —
    # proving the fishing seed never uses str-hashing (integer splitmix64 only).
    inproc = catch.resolve_cast(999, "deep_lake")
    code = (
        "from games.fishing.core import catch;"
        "o = catch.resolve_cast(999, 'deep_lake');"
        "c = o.catch;"
        "print(f'{o.bit}|{o.energy_cost}|"
        "{(c.species_id, c.size) if c else None}')"
    )
    out = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=True,
        cwd=_repo_root(),
    ).stdout.strip()
    c = inproc.catch
    expected = f"{inproc.bit}|{inproc.energy_cost}|{(c.species_id, c.size) if c else None}"
    assert out == expected


def test_injected_rng_overrides_default_stream() -> None:
    # A host injecting its own rng (the live-roll path) drives the outcome: over many
    # streams the same cast yields a spread of results, proving it is rng-driven rather
    # than pinned to the deterministic default.
    outs = {
        (o.bit, o.catch.species_id if o.catch else None, o.catch.size if o.catch else None)
        for s in range(80)
        for o in [catch.resolve_cast(1, "dock", rng=random.Random(s))]
    }
    assert len(outs) > 1


def _repo_root() -> str:
    import os

    # tests/fishing/ -> repo root is two levels up.
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
