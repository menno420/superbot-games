"""stamp_scaffold — the truth-stamp anchor parser + bullet skeleton emitter.

Pins the pure helpers (anchor grammar, bullet formatting, the missing-anchor
failure) and the one repo-level contract that makes the tool useful at all:
``docs/current-state.md`` actually carries a parseable
``<!-- truth-stamped-at: <sha> -->`` anchor. Kept git-history-independent
(no fixed ancestor SHAs) so the suite passes on shallow CI checkouts.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "tools"))

import stamp_scaffold  # noqa: E402


def test_parse_anchor_reads_the_comment() -> None:
    text = "prose above\n<!-- truth-stamped-at: fdea1035fde718 -->\nprose below\n"
    assert stamp_scaffold.parse_anchor(text) == "fdea1035fde718"


def test_parse_anchor_tolerates_spacing() -> None:
    assert stamp_scaffold.parse_anchor("<!--truth-stamped-at:abc1234-->") == "abc1234"
    assert (
        stamp_scaffold.parse_anchor("<!--   truth-stamped-at:   abc1234   -->")
        == "abc1234"
    )


def test_parse_anchor_rejects_non_sha_and_absence() -> None:
    assert stamp_scaffold.parse_anchor("no anchor here") is None
    # Too short / not hex — must not match, a corrupt anchor is no anchor.
    assert stamp_scaffold.parse_anchor("<!-- truth-stamped-at: abc12 -->") is None
    assert stamp_scaffold.parse_anchor("<!-- truth-stamped-at: notasha -->") is None


def test_format_bullet_promotes_the_squash_pr_number() -> None:
    bullet = stamp_scaffold.format_bullet(
        "fdea103aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "2026-07-14",
        "test: sim-harness smoke registry — every sim's render path executes in CI (#119)",
    )
    assert bullet == (
        "- **#119** (2026-07-14, `fdea103`) — test: sim-harness smoke registry "
        "— every sim's render path executes in CI"
    )


def test_format_bullet_placeholder_when_no_pr_suffix() -> None:
    bullet = stamp_scaffold.format_bullet(
        "abc1234def", "2026-07-14", "a direct push without a squash suffix"
    )
    assert bullet.startswith("- **#?** (2026-07-14, `abc1234`) — ")
    assert "a direct push without a squash suffix" in bullet


def test_scaffold_requires_an_anchor() -> None:
    with pytest.raises(ValueError, match="truth-stamped-at"):
        stamp_scaffold.scaffold("a ledger that lost its anchor")


def test_scaffold_empty_when_anchor_is_head() -> None:
    # anchor..anchor is an empty range — the tool reports nothing to groom
    # without touching history depth (shallow-checkout safe).
    doc = "<!-- truth-stamped-at: 0000000 -->"
    doc = doc.replace("0000000", _head_sha())
    assert stamp_scaffold.scaffold(doc, head=_head_sha()) == []


def test_the_real_ledger_carries_a_parseable_anchor() -> None:
    text = (_REPO_ROOT / "docs" / "current-state.md").read_text(encoding="utf-8")
    anchor = stamp_scaffold.parse_anchor(text)
    assert anchor is not None, (
        "docs/current-state.md lost its <!-- truth-stamped-at: <sha> --> anchor "
        "— restore it beside the prose stamp"
    )


def _head_sha() -> str:
    import subprocess

    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        cwd=_REPO_ROOT,
        check=True,
    ).stdout.strip()
