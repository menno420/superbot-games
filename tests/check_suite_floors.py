#!/usr/bin/env python3
"""Per-suite pytest count-floor guard (ORDER-001 coverage ratchet).

Why this exists
---------------
CI used to carry ONE hardcoded ``-lt <N>`` count floor for the whole suite in
``.github/workflows/tests.yml``. Every PR that added a test had to bump that
single shared integer, so two test-adding PRs always collided on the same line
and every merge re-conflicted every other open PR.

This guard replaces that shared int with a self-maintaining, per-suite floor:
each real test-suite directory owns an ``EXPECTED_MIN_TESTS.txt`` (a single
integer = that suite's minimum collected count). A test-adding PR bumps only its
OWN suite's file, so suites never collide on the floor.

The ORDER-001 guarantee is preserved and, if anything, sharpened: the gate still
fails LOUDLY the moment any suite drops out of collection or shrinks below its
floor — now naming the exact suite instead of reporting one opaque total.

Discovery
---------
A suite is any directory that either

  * directly contains at least one ``test_*.py`` file, under ``tests/`` or
    matching ``games/*/tests``, OR
  * carries an ``EXPECTED_MIN_TESTS.txt`` floor file.

Taking the UNION means:

  * a suite that gains test files but forgets its floor file  -> LOUD failure
    ("no EXPECTED_MIN_TESTS.txt"), forcing the PR to add one (its own file);
  * a suite whose floor file survives but whose tests all vanished -> collected 0
    -> LOUD failure (the "suite dropped out of collection" case);
  * a suite that shrinks below its recorded floor -> LOUD failure naming it.

Exit status
-----------
0  every suite collected >= its floor (prints a per-suite table).
1  any suite below floor / missing floor file / collection error / zero collected.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FLOOR_FILENAME = "EXPECTED_MIN_TESTS.txt"

# Roots under which a directory holding test_*.py counts as a suite.
TESTS_ROOT = REPO_ROOT / "tests"
GAMES_ROOT = REPO_ROOT / "games"


def _discover_suite_dirs() -> list[Path]:
    """Return the sorted set of suite directories (union of the two signals)."""
    suites: set[Path] = set()

    # 1. dirs directly containing test_*.py under tests/
    if TESTS_ROOT.is_dir():
        for test_file in TESTS_ROOT.rglob("test_*.py"):
            suites.add(test_file.parent)

    # 2. dirs directly containing test_*.py under games/*/tests
    if GAMES_ROOT.is_dir():
        for tests_dir in GAMES_ROOT.glob("*/tests"):
            if tests_dir.is_dir() and any(tests_dir.glob("test_*.py")):
                suites.add(tests_dir)
        # also catch nested game test files (games/*/**/tests/test_*.py)
        for test_file in GAMES_ROOT.rglob("test_*.py"):
            if test_file.parent.name == "tests" or "tests" in test_file.parent.parts:
                suites.add(test_file.parent)

    # 3. any dir that already owns a floor file (catches a suite whose tests
    #    all vanished but whose floor file survives -> a dropped suite).
    for floor in REPO_ROOT.rglob(FLOOR_FILENAME):
        suites.add(floor.parent)

    return sorted(suites)


def _collect_count(suite_dir: Path) -> tuple[int, str | None]:
    """Collect a suite; return (collected_count, error_string_or_None)."""
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", str(suite_dir), "--collect-only", "-q"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    out = proc.stdout + proc.stderr
    collected = sum(1 for line in out.splitlines() if "::" in line)
    # pytest exits 0 with tests, 5 when it collects nothing, non-zero on a real
    # collection error (import failure, syntax error, ...).
    if collected == 0 and proc.returncode not in (0, 5):
        return 0, f"pytest collection errored (rc={proc.returncode})\n{out.strip()}"
    return collected, None


def _read_floor(suite_dir: Path) -> tuple[int | None, str | None]:
    """Read a suite's EXPECTED_MIN_TESTS.txt; return (floor, error_or_None)."""
    floor_path = suite_dir / FLOOR_FILENAME
    if not floor_path.is_file():
        return None, f"no {FLOOR_FILENAME} floor file — add one owning this suite's minimum"
    raw = floor_path.read_text(encoding="utf-8").strip()
    try:
        return int(raw), None
    except ValueError:
        return None, f"{FLOOR_FILENAME} is not a single integer (got {raw!r})"


def main() -> int:
    suites = _discover_suite_dirs()
    if not suites:
        print("FLOOR GUARD FAILURE: no test suites discovered at all", file=sys.stderr)
        return 1

    rows: list[tuple[str, int, int]] = []
    failures: list[str] = []

    for suite_dir in suites:
        rel = suite_dir.relative_to(REPO_ROOT).as_posix()
        floor, floor_err = _read_floor(suite_dir)
        if floor_err is not None:
            failures.append(f"[{rel}] {floor_err}")
            continue

        collected, collect_err = _collect_count(suite_dir)
        if collect_err is not None:
            failures.append(f"[{rel}] {collect_err}")
            continue
        if collected == 0:
            failures.append(
                f"[{rel}] collected 0 tests — suite dropped out of collection "
                f"(floor is {floor})"
            )
            continue
        if collected < floor:
            failures.append(
                f"[{rel}] SHRANK: collected {collected} < floor {floor} "
                f"— a test was removed/renamed or stopped collecting"
            )
            continue
        rows.append((rel, collected, floor))

    if failures:
        print("=" * 72, file=sys.stderr)
        print("SUITE FLOOR GUARD FAILED (ORDER-001) — coverage ratchet tripped:", file=sys.stderr)
        print("=" * 72, file=sys.stderr)
        for f in failures:
            print(f"  !! {f}", file=sys.stderr)
        print("=" * 72, file=sys.stderr)
        return 1

    width = max((len(r[0]) for r in rows), default=5)
    total = sum(r[1] for r in rows)
    print("per-suite test-count floors — all suites at or above floor:")
    print(f"  {'suite'.ljust(width)}  collected  floor")
    for rel, collected, floor in sorted(rows):
        print(f"  {rel.ljust(width)}  {collected:>9}  {floor:>5}")
    print(f"  {'TOTAL'.ljust(width)}  {total:>9}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
