"""grid: seed-determinism (process-independent) + negative-coord wrap."""

from __future__ import annotations

import subprocess
import sys

from games.mining.core import grid


def test_cell_at_is_deterministic_within_process() -> None:
    a = grid.cell_at(12345, 3, -7, 2)
    b = grid.cell_at(12345, 3, -7, 2)
    assert a == b
    assert isinstance(a, grid.Cell)
    assert a.feature in grid.CellFeature
    assert a.featured_resource in grid.ore_weights_for_depth(2)


def test_cell_at_process_independent() -> None:
    # A fresh interpreter (PYTHONHASHSEED randomised by default) must produce the
    # identical cell — proving the splitmix64 hash never uses str-hashing.
    inproc = grid.cell_at(999, -4, 8, 3)
    code = (
        "from games.mining.core import grid;"
        "c = grid.cell_at(999, -4, 8, 3);"
        "print(f'{c.feature.value}|{c.featured_resource}|{c.richness}')"
    )
    out = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=True,
        cwd=_repo_root(),
    ).stdout.strip()
    assert out == f"{inproc.feature.value}|{inproc.featured_resource}|{inproc.richness}"


def test_negative_coords_wrap_and_stay_valid() -> None:
    c = grid.cell_at(7, -100, -100, 0)
    assert isinstance(c, grid.Cell)
    assert c.feature in grid.CellFeature


def test_richness_table_and_features_preserved() -> None:
    seen = {grid.cell_at(1, x, 0, 0).feature for x in range(500)}
    # over enough cells every feature appears (weights 70/10/18/2).
    assert seen == set(grid.CellFeature)


def test_apply_cell_to_loot_folds_richness() -> None:
    rich = grid.Cell(0, 0, 0, grid.CellFeature.RICH, "gold", 2.0)
    item, amount, note = grid.apply_cell_to_loot(rich, "stone", 3)
    assert item == "gold"  # rich cell yields its featured ore
    assert amount == 6  # round(3 * 2.0)
    assert note is not None
    barren = grid.Cell(0, 0, 0, grid.CellFeature.BARREN, "stone", 0.5)
    item, amount, note = grid.apply_cell_to_loot(barren, "iron", 3)
    assert item == "iron"
    assert amount == 2  # max(1, round(3 * 0.5)) → round(1.5)=2
    normal = grid.Cell(0, 0, 0, grid.CellFeature.NORMAL, "stone", 1.0)
    assert grid.apply_cell_to_loot(normal, "iron", 4) == ("iron", 4, None)


def test_reveal_radius_non_regressive() -> None:
    assert grid.reveal_radius(0) == 2
    assert grid.reveal_radius(1) == 2
    assert grid.reveal_radius(2) == 3
    assert grid.reveal_radius(3) == 4
    assert grid.reveal_radius(99) == 4  # capped


def _repo_root() -> str:
    import os

    # tests/mining/ -> repo root is two levels up.
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
