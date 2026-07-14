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


# ---------------------------------------------------------------------------
# --flip mode — step 4 = `bootstrap.py check --strict` (flip-readiness).
#
# The in-process tests load the script as a module and stub subprocess.run
# with a recorder: a full --flip subprocess run would nest the entire suite
# plus strict (~the whole preflight again), and mid-slice the repo's newest
# session card is in-progress BY DESIGN, so bare strict is red on exactly
# the trees these tests run on. The strict-red semantics step 4 relies on
# (the born-red HOLD) are pinned for real below via `--session-log` against
# a synthetic in-progress card — cheap, hermetic, no tree copy.
# ---------------------------------------------------------------------------
BOOTSTRAP = REPO_ROOT / "bootstrap.py"


def _load_preflight_module():
    spec = importlib.util.spec_from_file_location("preflight_under_test", PREFLIGHT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _FakeProc:
    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = ""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _record_gate_runs(monkeypatch, mod, *, strict_exit: int = 0):
    """Stub the module's subprocess.run: record commands, run nothing."""
    calls: list[list[str]] = []

    def fake_run(command, **kwargs):
        calls.append([str(part) for part in command])
        if kwargs.get("capture_output"):
            return _FakeProc(0, "tests\n", "")  # --print-suites derivation
        if str(BOOTSTRAP) in calls[-1]:
            return _FakeProc(strict_exit)
        return _FakeProc(0)

    monkeypatch.setattr(mod.subprocess, "run", fake_run)
    return calls


def test_default_mode_runs_exactly_three_gates_and_never_bootstrap(monkeypatch, capsys):
    """Byte-compat pin: no --flip → the pre-flag banners, no strict step."""
    mod = _load_preflight_module()
    calls = _record_gate_runs(monkeypatch, mod)
    assert mod.main([]) == 0
    # floor guard, --print-suites derivation, pytest, balance check — and
    # never bootstrap.
    assert len(calls) == 4
    assert not any(str(BOOTSTRAP) in call for call in calls)
    out = capsys.readouterr().out
    for banner in ("preflight 1/3:", "preflight 2/3:", "preflight 3/3:"):
        assert banner in out
    assert "preflight GREEN — all three gates passed (floor guard, pytest, balance)" in out
    assert "4/" not in out and "strict" not in out


def test_flip_mode_appends_bootstrap_check_strict_as_step_four(monkeypatch, capsys):
    mod = _load_preflight_module()
    calls = _record_gate_runs(monkeypatch, mod)
    assert mod.main(["--flip"]) == 0
    assert calls[-1] == [sys.executable, str(BOOTSTRAP), "check", "--strict"]
    out = capsys.readouterr().out
    for banner in ("preflight 1/4:", "preflight 2/4:", "preflight 3/4:", "preflight 4/4:"):
        assert banner in out
    assert "flip-readiness (bootstrap check --strict)" in out
    assert "flip-ready" in out


def test_flip_mode_propagates_a_red_strict_exit_code(monkeypatch, capsys):
    mod = _load_preflight_module()
    _record_gate_runs(monkeypatch, mod, strict_exit=7)
    with pytest.raises(SystemExit) as excinfo:
        mod.main(["--flip"])
    assert excinfo.value.code == 7
    out = capsys.readouterr().out
    assert "preflight FAILED at 4/4 (flip-readiness (bootstrap check --strict)) — exit 7" in out


def test_strict_gate_holds_red_on_an_in_progress_card(tmp_path):
    """The semantics step 4 leans on: strict reds an in-progress card.

    Pinned via `--session-log` (explicit-card selection keeps the locked
    door) against a synthetic born-red card — the real strict runner, the
    real HOLD, no repo-tree simulation needed.
    """
    card = tmp_path / "2026-07-14-synthetic-hold.md"
    card.write_text(
        "# 2026-07-14 · synthetic — born-red hold probe\n\n"
        "> **Status:** in-progress\n>\n"
        "> 📊 Model: Fable · 2026-07-14T00:00:00Z · synthetic\n",
        encoding="utf-8",
    )
    proc = subprocess.run(
        [sys.executable, str(BOOTSTRAP), "check", "--strict", "--session-log", str(card)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=120,
    )
    assert proc.returncode != 0
    assert "badge still says in-progress" in proc.stdout
    assert "designed hold" in proc.stdout
