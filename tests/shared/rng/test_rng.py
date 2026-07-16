"""games.shared.rng — the extracted mining splitmix64 seam.

Pins the shared module's three guarantees (determinism, a known-vector, and
process-independence) plus the extraction invariant: mining's two call sites
(``grid._cell_seed`` and ``encounters.encounter_seed``) now route through this
module and stay byte-identical to the values they produced before the extraction.

Mirrors ``tests/mining/test_grid.py`` / ``tests/fishing/test_determinism.py``:
the derivation is a pure function of ``(seed, coords…)`` (integer splitmix64, no
str-hashing), re-checked across a fresh interpreter.
"""

from __future__ import annotations

import os
import subprocess
import sys

from games.mining.core import encounters, grid
from games.shared import rng


def _repo_root() -> str:
    # tests/shared/rng/ -> repo root is three levels up.
    here = os.path.abspath(__file__)
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(here))))


# ---------------------------------------------------------------------------
# Determinism + masking
# ---------------------------------------------------------------------------
def test_cell_seed_is_deterministic() -> None:
    assert rng.cell_seed(12345, 3, -7, 2) == rng.cell_seed(12345, 3, -7, 2)
    assert rng.mix64(42) == rng.mix64(42)


def test_output_stays_within_64_bits() -> None:
    for seed in (0, 1, 2**63, 2**64 - 1, 2**64 + 5):
        for coords in ((), (0,), (3, -7, 2), (-100, -100, 0, 999)):
            value = rng.cell_seed(seed, *coords)
            assert 0 <= value <= rng.MASK64
    assert 0 <= rng.mix64(2**70) <= rng.MASK64  # unmasked input is masked internally


def test_no_coords_returns_masked_seed() -> None:
    assert rng.cell_seed(0) == 0
    assert rng.cell_seed(2**64 + 7) == 7  # seed wraps under MASK64


def test_negative_coords_wrap_deterministically() -> None:
    # Negative coordinates fold under the 64-bit mask, stably.
    a = rng.cell_seed(7, -100, -100, 0)
    b = rng.cell_seed(7, -100, -100, 0)
    assert a == b
    assert 0 <= a <= rng.MASK64


# ---------------------------------------------------------------------------
# Known-vector — pins the exact wire values so a mix-step change reds loudly
# ---------------------------------------------------------------------------
def test_known_vectors() -> None:
    # mix64(0) is the golden-ratio gamma itself: (0 + GAMMA + 0 + 0) & MASK64.
    assert rng.mix64(0) == 0x9E3779B97F4A7C15
    assert rng.mix64(0) == 11400714819323198485
    assert rng.mix64(1) == 11400714819323198550
    assert rng.cell_seed(0, 0, 0, 0) == 4853079772965231455
    assert rng.cell_seed(12345, 3, -7, 2) == 17319971336489335733
    assert rng.cell_seed(999, -4, 8, 3) == 7447153158053695402


# ---------------------------------------------------------------------------
# Seeding independence — distinct inputs give distinct streams
# ---------------------------------------------------------------------------
def test_different_seeds_diverge() -> None:
    values = {rng.cell_seed(s, 1, 2, 3) for s in range(64)}
    assert len(values) == 64  # no collisions over a small seed sweep


def test_different_coords_diverge() -> None:
    values = {rng.cell_seed(42, x, 0, 0) for x in range(64)}
    assert len(values) == 64


def test_coord_order_matters() -> None:
    # The per-coordinate mix is order-sensitive (a real hash, not a symmetric sum).
    assert rng.cell_seed(0, 1, 2, 3) != rng.cell_seed(0, 3, 2, 1)


# ---------------------------------------------------------------------------
# Process-independence — never touches hash(str) randomisation
# ---------------------------------------------------------------------------
def test_process_independent() -> None:
    # A fresh interpreter (PYTHONHASHSEED randomised by default) must produce the
    # identical value — proving the mix uses integer arithmetic only.
    inproc = rng.cell_seed(999, -4, 8, 3)
    code = (
        "from games.shared import rng;"
        "print(rng.cell_seed(999, -4, 8, 3))"
    )
    out = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=True,
        cwd=_repo_root(),
    ).stdout.strip()
    assert out == str(inproc)


# ---------------------------------------------------------------------------
# Extraction invariant — mining's seams route through the shared module and
# stay byte-identical to the pre-extraction derivation.
# ---------------------------------------------------------------------------
def test_grid_cell_seed_routes_through_shared() -> None:
    for seed in (0, 12345, 999, 2**64 - 1):
        for x in range(-3, 4):
            for y in range(-3, 4):
                for z in range(0, 5):
                    assert grid._cell_seed(seed, x, y, z) == rng.cell_seed(seed, x, y, z)


def test_encounter_seed_is_salted_shared_mix() -> None:
    # encounter_seed = mix64(cell_seed(...) ^ salt): a distinct stream from the
    # grid's own, but built from the same shared seam.
    salt = encounters._ENCOUNTER_SALT
    for seed in (0, 12345, 999):
        for x in range(-2, 3):
            for y in range(-2, 3):
                for z in range(0, 4):
                    expected = rng.mix64(rng.cell_seed(seed, x, y, z) ^ salt)
                    assert encounters.encounter_seed(seed, x, y, z) == expected
                    # and it does NOT equal the un-salted grid seed (independent stream)
                    assert encounters.encounter_seed(seed, x, y, z) != rng.cell_seed(seed, x, y, z)
