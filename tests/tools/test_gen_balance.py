"""gen_balance — the docs/balance.md generator that gates every merge.

Pins the seam CI actually runs (``--check`` against the committed page),
the deterministic render, every section header, the ``_num`` / ``_table`` /
``_read_floor`` helpers, and the stale-detection path (mutated copy →
``check()`` returns 1 with a unified diff). READS ONLY — no test writes to
the real ``docs/balance.md``; all mutation happens under ``tmp_path``.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "tools"))

import gen_balance  # noqa: E402

# Every section/subsection header render() emits, in document order.
EXPECTED_HEADERS = [
    "# World Games — Economy Balance (auto-generated)",
    "## Global reward ceiling",
    "## Action-rate ceilings (emission throttle)",
    "## Mining",
    "### Loot roll (`rewards.py`)",
    "### Encounter tunables (`encounters.py`)",
    "### Per-unit ore coin value (`items.py`)",
    "### Storage caps + vault coin sink (`capacity.py`)",
    "## Fishing",
    "### Catch resolver (`catch.py`)",
    "### Species (`species.py`)",
    "### Spot bite biases (`spots.py`)",
    "### Fishing economy (V043) (`economy.py`)",
    "## DND",
    "## Exploration quests",
    "## Test suite floors",
    "## Notes",
]


def test_check_is_green_against_committed_doc(capsys) -> None:
    """The exact CI gate: the committed docs/balance.md is byte-fresh."""
    assert gen_balance.check() == 0
    assert capsys.readouterr().out == ""  # green check prints nothing


def test_render_is_deterministic() -> None:
    assert gen_balance.render() == gen_balance.render()


def test_render_matches_committed_doc_bytes() -> None:
    committed = gen_balance.DOC_PATH.read_text(encoding="utf-8")
    assert gen_balance.render() == committed


def test_all_section_headers_present_in_order() -> None:
    lines = gen_balance.render().splitlines()
    positions = []
    for header in EXPECTED_HEADERS:
        assert header in lines, f"missing section header: {header!r}"
        positions.append(lines.index(header))
    assert positions == sorted(positions), "section order drifted"


def test_num_formats_ints_floats_bools_and_passthrough() -> None:
    assert gen_balance._num(3) == "3"
    assert gen_balance._num(-7) == "-7"
    # bool guard: bool is an int subclass but renders as True/False.
    assert gen_balance._num(True) == "True"
    # floats: fixed precision, trailing zeros then trailing dot stripped.
    assert gen_balance._num(3.0) == "3"
    assert gen_balance._num(0.6000) == "0.6"
    assert gen_balance._num(0.1234567) == "0.1235"
    # non-numbers pass through str().
    assert gen_balance._num("wood") == "wood"


def test_table_renders_github_markdown_shape() -> None:
    lines = gen_balance._table(("a", "b"), [("1", "2"), ("3", "4")])
    assert lines == [
        "| a | b |",
        "| --- | --- |",
        "| 1 | 2 |",
        "| 3 | 4 |",
    ]


def test_read_floor_strips_whitespace(tmp_path: Path) -> None:
    floor = tmp_path / "EXPECTED_MIN_TESTS.txt"
    floor.write_text("  42\n\n", encoding="utf-8")
    assert gen_balance._read_floor(floor) == "42"


def test_write_then_check_roundtrip(tmp_path: Path) -> None:
    target = tmp_path / "balance.md"
    gen_balance.write(target)
    assert gen_balance.check(target) == 0


def test_check_flags_stale_copy_with_diff(capsys) -> None:
    # In-repo scratch path: check()'s stale message calls
    # path.relative_to(repo root), so the target must live under the repo.
    target = _REPO_ROOT / "docs" / "balance-stale-probe.md"
    stale = gen_balance.render().replace(
        "## Global reward ceiling", "## Global reward ceiling (stale)"
    )
    assert stale != gen_balance.render()
    try:
        target.write_text(stale, encoding="utf-8")
        assert gen_balance.check(target) == 1
    finally:
        target.unlink()
    out = capsys.readouterr().out
    assert "is stale" in out
    assert "--- " in out and "+++ " in out  # unified diff headers
    assert "regenerate with `python3 tools/gen_balance.py`" in out


def test_check_missing_file_is_stale(capsys) -> None:
    missing = _REPO_ROOT / "docs" / "never-written-balance.md"
    assert not missing.exists()
    assert gen_balance.check(missing) == 1
    assert "is stale" in capsys.readouterr().out


def test_check_stale_path_outside_repo_returns_1(tmp_path: Path, capsys) -> None:
    """#121 pinned this as a ValueError crash in the error message's
    ``relative_to(_REPO_ROOT)``; fixed: an out-of-repo stale path now
    returns 1 and the message shows the absolute path."""
    outside = tmp_path / "balance.md"
    outside.write_text("stale\n", encoding="utf-8")
    assert gen_balance.check(outside) == 1
    out = capsys.readouterr().out
    assert "is stale" in out
    assert str(outside) in out


def test_main_dispatch_check_and_usage(capsys) -> None:
    assert gen_balance.main(["gen_balance.py", "--check"]) == 0
    assert gen_balance.main(["gen_balance.py", "--bogus"]) == 2
    captured = capsys.readouterr()
    assert "usage:" in captured.err
    assert "[--write | --check]" in captured.err


def test_suite_floors_section_covers_every_registered_suite() -> None:
    text = gen_balance.render()
    registry = _REPO_ROOT / "tests" / "EXPECTED_SUITES.txt"
    for line in registry.read_text(encoding="utf-8").splitlines():
        suite = line.strip()
        if not suite or suite.startswith("#"):
            continue
        assert f"| `{suite}` |" in text, f"suite floor row missing: {suite}"
