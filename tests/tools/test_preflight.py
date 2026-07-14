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


def _record_gate_runs(monkeypatch, mod, *, strict_exit: int = 0, added_cards=()):
    """Stub the module's subprocess.run: record commands, run nothing.

    ``added_cards`` is what the fake `git diff --diff-filter=A` derivation
    reports — the knob that selects between --flip's three card paths
    (zero / one / many).
    """
    calls: list[list[str]] = []

    def fake_run(command, **kwargs):
        cmd = [str(part) for part in command]
        calls.append(cmd)
        if cmd[0] == "git":
            return _FakeProc(0, "".join(f"{card}\n" for card in added_cards), "")
        if kwargs.get("capture_output"):
            return _FakeProc(0, "tests\n", "")  # --print-suites derivation
        if str(BOOTSTRAP) in cmd:
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
    # never bootstrap, never the git card derivation.
    assert len(calls) == 4
    assert not any(str(BOOTSTRAP) in call for call in calls)
    assert not any(call[0] == "git" for call in calls)
    out = capsys.readouterr().out
    for banner in ("preflight 1/3:", "preflight 2/3:", "preflight 3/3:"):
        assert banner in out
    assert "preflight GREEN — all three gates passed (floor guard, pytest, balance)" in out
    # No step-4 banner and no flip-ready line — matched on the banner PREFIX,
    # not a bare "4/" substring: the banners echo the interpreter path, and a
    # CI toolcache python lives under e.g. .../Python/3.14.6/x64/... which
    # contains "4/" (the exact false positive that reddened the first push).
    assert "preflight 4/" not in out
    assert "flip-ready" not in out
    assert "flip-readiness" not in out


def test_flip_mode_zero_added_cards_falls_back_to_bare_strict(monkeypatch, capsys):
    """Path 1/3 (control-fast-lane tree): no card in the branch diff → the
    pre-parity bare strict, behind an explicit banner naming the fallback."""
    mod = _load_preflight_module()
    calls = _record_gate_runs(monkeypatch, mod, added_cards=())
    assert mod.main(["--flip"]) == 0
    # The derivation runs FIRST (fail-fast, before any gate), then the gates.
    assert calls[0][0] == "git"
    assert calls[0][1:4] == ["diff", "--name-only", "--diff-filter=A"]
    assert "origin/main...HEAD" in calls[0]
    assert calls[-1] == [sys.executable, str(BOOTSTRAP), "check", "--strict"]
    out = capsys.readouterr().out
    for banner in ("preflight 1/4:", "preflight 2/4:", "preflight 3/4:", "preflight 4/4:"):
        assert banner in out
    assert "flip card: none ADDED on this branch" in out
    assert "newest-by-mtime card fallback" in out
    assert "flip-readiness (bootstrap check --strict)" in out
    assert "flip-ready" in out


def test_flip_mode_one_added_card_is_passed_via_session_log(monkeypatch, capsys):
    """Path 2/3 (the parity fix): the branch's OWN added card is what step 4
    grades — via `--session-log`, never strict's newest-by-mtime guess."""
    mod = _load_preflight_module()
    card = ".sessions/2026-07-14-parity-probe.md"
    calls = _record_gate_runs(monkeypatch, mod, added_cards=(card,))
    assert mod.main(["--flip"]) == 0
    assert calls[-1] == [
        sys.executable,
        str(BOOTSTRAP),
        "check",
        "--strict",
        "--session-log",
        card,
    ]
    out = capsys.readouterr().out
    assert f"flip card derived from the branch diff (origin/main...HEAD): {card}" in out
    assert "flip-ready" in out


def test_flip_mode_multiple_added_cards_error_loud_before_any_gate(monkeypatch, capsys):
    """Path 3/3: two added cards is ambiguous — loud error listing both,
    non-zero exit, and NO gate (not even the floor guard) has run."""
    mod = _load_preflight_module()
    cards = (
        ".sessions/2026-07-14-card-one.md",
        ".sessions/2026-07-14-card-two.md",
    )
    calls = _record_gate_runs(monkeypatch, mod, added_cards=cards)
    with pytest.raises(SystemExit) as excinfo:
        mod.main(["--flip"])
    assert excinfo.value.code == 1
    # Only the git derivation ran — fail-fast means no suite pass is wasted.
    assert len(calls) == 1
    assert calls[0][0] == "git"
    out = capsys.readouterr().out
    assert "2 session cards ADDED on this branch" in out
    assert "a flip grades ONE card" in out
    for card in cards:
        assert f"  {card}" in out


def test_flip_mode_propagates_a_red_strict_exit_code(monkeypatch, capsys):
    mod = _load_preflight_module()
    _record_gate_runs(monkeypatch, mod, strict_exit=7)
    with pytest.raises(SystemExit) as excinfo:
        mod.main(["--flip"])
    assert excinfo.value.code == 7
    out = capsys.readouterr().out
    assert "preflight FAILED at 4/4 (flip-readiness (bootstrap check --strict)) — exit 7" in out


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    )


def test_added_session_cards_derives_from_diff_not_mtime(tmp_path, monkeypatch):
    """Real-git pin of the card idea's scenario: the branch ADDS an
    older-named card while a bystander card (already on main) carries the
    freshest mtime — the mtime fallback's wrong pick. The diff derivation
    must return exactly the branch's card, exclude the not-added bystander
    (--diff-filter=A) and the README (pathspec), regardless of mtimes."""
    repo = tmp_path / "repo"
    (repo / ".sessions").mkdir(parents=True)
    bystander = repo / ".sessions" / "2026-07-13-bystander.md"
    bystander.write_text("# bystander card already on main\n", encoding="utf-8")
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "probe@example.invalid")
    _git(repo, "config", "user.name", "probe")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    # Synthetic remote-tracking ref: the derivation's diff base.
    _git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    branch_card = repo / ".sessions" / "2026-07-01-branch-card.md"
    branch_card.write_text("# the branch's own card\n", encoding="utf-8")
    readme = repo / ".sessions" / "README.md"
    readme.write_text("# added README must be excluded\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "born-red card + README")
    # Make the BYSTANDER the newest file by mtime — latest_session_log's pick.
    fresh = bystander.stat().st_mtime + 3600
    os.utime(bystander, (fresh, fresh))
    mod = _load_preflight_module()
    monkeypatch.setattr(mod, "REPO_ROOT", repo)
    assert mod._added_session_cards() == [".sessions/2026-07-01-branch-card.md"]


def test_pick_flip_card_zero_and_one(capsys):
    mod = _load_preflight_module()
    assert mod._pick_flip_card([]) is None
    assert mod._pick_flip_card([".sessions/x.md"]) == ".sessions/x.md"


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
