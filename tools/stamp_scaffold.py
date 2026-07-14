#!/usr/bin/env python3
"""Emit "Recently shipped" bullet skeletons from the truth-stamp anchor.

Truth-stamp grooms of ``docs/current-state.md`` hand-transcribe PR numbers,
UTC dates, and squash-merge SHAs into the "Recently shipped" list — the
highest-volume mechanical part of the groom and the only part where a typo
silently corrupts the ledger (a wrong SHA is unfalsifiable prose until someone
re-verifies it). This tool makes those citations correct by construction:

  1. it reads the machine-readable anchor comment the ledger carries beside
     its prose stamp — ``<!-- truth-stamped-at: <sha> -->`` — and
  2. emits one ``- **#N** (YYYY-MM-DD, `sha`) — subject`` bullet per
     first-parent commit in ``git log <anchor>..HEAD`` (GitHub squash-merge
     subjects carry the PR number as a trailing ``(#N)``).

The groom then hand-writes the verified prose on top of machine-derived
citations. This is an AUTHORING AID, deliberately not a CI gate: the ledger
stays a hand-maintained document; only the mechanical transcription is
generated. (Detector-side staleness alarms are a separate concern — see the
#89 ledger-drift KIT-ASK.)

Usage:
    python3 tools/stamp_scaffold.py                # docs/current-state.md .. HEAD
    python3 tools/stamp_scaffold.py --head <ref>   # stop at another ref
    python3 tools/stamp_scaffold.py --doc <path>   # read the anchor elsewhere
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DOC = REPO_ROOT / "docs" / "current-state.md"

ANCHOR_RE = re.compile(r"<!--\s*truth-stamped-at:\s*([0-9a-f]{7,40})\s*-->")
PR_SUFFIX_RE = re.compile(r"^(?P<subject>.*?)\s*\(#(?P<pr>\d+)\)\s*$")

# One field separator that never appears in subjects.
_LOG_FORMAT = "%H%x09%ad%x09%s"


def parse_anchor(text: str) -> str | None:
    """Return the anchored SHA from a ledger's text, or None if absent."""
    match = ANCHOR_RE.search(text)
    return match.group(1) if match else None


def format_bullet(sha: str, date: str, subject: str) -> str:
    """One "Recently shipped" skeleton bullet from a log row.

    Squash-merge subjects carry the PR number as a trailing ``(#N)`` — it is
    promoted to the bullet's ``**#N**`` citation and stripped from the
    subject. A commit without one (rare on this repo's squash-only main)
    keeps a loud ``**#?**`` placeholder so the groom must resolve it by hand.
    """
    short = sha[:7]
    match = PR_SUFFIX_RE.match(subject)
    if match:
        return f"- **#{match.group('pr')}** ({date}, `{short}`) — {match.group('subject')}"
    return f"- **#?** ({date}, `{short}`) — {subject}"


def git_log_rows(anchor: str, head: str = "HEAD") -> list[tuple[str, str, str]]:
    """(sha, utc-date, subject) per first-parent commit in anchor..head, newest first."""
    proc = subprocess.run(
        [
            "git",
            "log",
            "--first-parent",
            f"--format={_LOG_FORMAT}",
            "--date=format-local:%Y-%m-%d",
            f"{anchor}..{head}",
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env={**os.environ, "TZ": "UTC"},
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git log failed (rc={proc.returncode}): {proc.stderr.strip()}")
    rows: list[tuple[str, str, str]] = []
    for line in proc.stdout.splitlines():
        sha, date, subject = line.split("\t", 2)
        rows.append((sha, date, subject))
    return rows


def scaffold(doc_text: str, head: str = "HEAD") -> list[str]:
    """The bullet skeletons for everything merged since doc_text's anchor."""
    anchor = parse_anchor(doc_text)
    if anchor is None:
        raise ValueError(
            "no <!-- truth-stamped-at: <sha> --> anchor found — add one beside "
            "the ledger's prose stamp first"
        )
    return [format_bullet(*row) for row in git_log_rows(anchor, head)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--doc", type=Path, default=DEFAULT_DOC)
    parser.add_argument("--head", default="HEAD")
    args = parser.parse_args(argv)

    try:
        bullets = scaffold(args.doc.read_text(encoding="utf-8"), head=args.head)
    except (ValueError, RuntimeError, OSError) as exc:
        print(f"stamp_scaffold: {exc}", file=sys.stderr)
        return 1

    if not bullets:
        print("stamp_scaffold: anchor is at HEAD — nothing to groom", file=sys.stderr)
        return 0
    print("\n".join(bullets))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
