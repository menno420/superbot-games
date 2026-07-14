"""Gate-parity preflight + registry-derived pytest roots.

`tools/preflight.py` is the ONE gate sequence CI and local hands both run
(floor guard → pytest over registry-derived paths → balance freshness), and
`tests/check_suite_floors.py --print-suites` is where it gets its pytest
paths — derived from `tests/EXPECTED_SUITES.txt`, never hand-synced. These
tests pin the derivation rule (pure function + subprocess mode) and smoke the
whole preflight end-to-end on the green repo.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FLOOR_GUARD = REPO_ROOT / "tests" / "check_suite_floors.py"
PREFLIGHT = REPO_ROOT / "tools" / "preflight.py"

#: The three execution roots the registry derives to at HEAD — the same paths
#: the tests workflow used to hardcode. If a registered suite moves outside
#: these trees, this pin (and the workflow behavior) changes in the same PR.
KNOWN_ROOTS = ["tests", "games/exploration/tests", "services/tests"]


def _load_guard_module():
    spec = importlib.util.spec_from_file_location("check_suite_floors", FLOOR_GUARD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_derive_pytest_roots_collapses_to_outermost_test_tree():
    mod = _load_guard_module()
    roots, underivable = mod.derive_pytest_roots(
        ["tests/mining", "tests/shared/inventory", "services/tests", "games/exploration/tests"]
    )
    assert roots == ["tests", "services/tests", "games/exploration/tests"]
    assert underivable == []


def test_derive_pytest_roots_reports_entry_without_tests_component():
    mod = _load_guard_module()
    roots, underivable = mod.derive_pytest_roots(["tests/mining", "games/exploration/quest"])
    assert roots == ["tests"]
    assert underivable == ["games/exploration/quest"]


def test_derive_pytest_roots_keeps_first_seen_order_and_dedupes():
    mod = _load_guard_module()
    roots, underivable = mod.derive_pytest_roots(
        ["services/tests", "tests/dnd", "tests/fishing", "services/tests"]
    )
    assert roots == ["services/tests", "tests"]
    assert underivable == []


def test_print_suites_emits_exactly_the_known_roots_at_head():
    proc = subprocess.run(
        [sys.executable, str(FLOOR_GUARD), "--print-suites"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.splitlines() == KNOWN_ROOTS
    assert proc.stderr == ""


def test_print_suites_covers_every_registry_entry():
    """Structural pin: each registered suite lies under one derived root, so
    pytest over the roots executes every registered suite by construction."""
    registry = [
        line.strip()
        for line in (REPO_ROOT / "tests" / "EXPECTED_SUITES.txt").read_text().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    proc = subprocess.run(
        [sys.executable, str(FLOOR_GUARD), "--print-suites"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    roots = proc.stdout.splitlines()
    for entry in registry:
        assert any(entry == root or entry.startswith(root + "/") for root in roots), entry


@pytest.mark.skipif(
    os.environ.get("SBG_PREFLIGHT") == "1",
    reason="already inside a preflight-launched suite (re-entrancy guard)",
)
def test_preflight_green_repo_exits_zero_with_all_three_banners():
    """End-to-end smoke: on a green repo the ONE command passes all gates.

    Slow by design (it runs the full suite once); the SBG_PREFLIGHT guard
    keeps the nesting to a single level when preflight itself runs pytest.
    """
    proc = subprocess.run(
        [sys.executable, str(PREFLIGHT)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=600,
    )
    assert proc.returncode == 0, f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    assert "preflight 1/3: suite-floor guard" in proc.stdout
    assert "preflight 2/3: pytest (registry-derived paths)" in proc.stdout
    assert "preflight 3/3: balance-page freshness" in proc.stdout
    assert "preflight GREEN" in proc.stdout
