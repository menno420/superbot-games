#!/usr/bin/env python3
"""Gate-parity preflight — the ONE command a session runs before any flip.

Why this exists
---------------
The tests workflow used to run three hand-synced steps — the suite-floor
guard, pytest over a HARDCODED path list, and the balance-page freshness
check — with no single local equivalent. That cost one CI round-trip per
newly-met gate (a floor bump making ``docs/balance.md`` stale is only
discovered post-push) and duplicated the suite list out of
``tests/EXPECTED_SUITES.txt``, the drift class that let ``services/tests``
collect-but-not-run (the #107 gap).

This script IS the gate sequence, run by CI and by hands alike, so the two
cannot drift by construction:

  1/3  suite-floor guard      ``tests/check_suite_floors.py``
  2/3  pytest                 over the roots ``--print-suites`` derives from
                              the suite registry (never a hardcoded list)
  3/3  balance freshness      ``tools/gen_balance.py --check``

``--flip`` appends the FOURTH gate a session flip needs (the substrate
gate's strict session-card grading, which the three tests-workflow gates
never run):

  4/4  flip-readiness         ``bootstrap.py check --strict``
                              ``[--session-log <card from the branch diff>]``

so "am I ready to flip?" is one command: green means the tree passes every
tests-workflow gate AND strict. Mid-slice it stays red BY DESIGN — the
born-red card's in-progress Status is the strict gate's designed HOLD —
and goes green once the card flips complete. The default three-step mode
is byte-identical to the pre-flag behavior; CI (``tests.yml``) keeps
calling the bare command and never runs step 4.

Card-selection parity (the #131 card's idea): bare ``check --strict``
picks the graded card by NEWEST MTIME (``latest_session_log``), which is
the wrong card exactly when it matters — touch any bystander card (a
groom, a merge-conflict resolution, a fresh checkout equalizing mtimes)
and flip-readiness silently grades the bystander while the branch's own
card goes unexamined. ``--flip`` therefore derives the card from the
branch's OWN diff — session cards ADDED relative to
``origin/main...HEAD`` (merge-base semantics, so a moved main never
pollutes the derivation), the same card the substrate gate's added-card
lane will grade — and passes it via strict's existing ``--session-log``
flag. Exactly one added card: graded explicitly. Multiple added cards:
loud error before any gate runs (a flip grades ONE card). Zero added
cards (a control-fast-lane tree): today's bare strict behind an explicit
banner naming the mtime fallback.

Exit status: 0 when every step passes; the FIRST failing step's exit code
otherwise (later steps do not run — fix, rerun, repeat).

Re-entrancy: ``SBG_PREFLIGHT=1`` is set for the pytest step so the preflight
smoke test in ``tests/tools/`` (which subprocesses this script) can skip
itself inside a preflight-launched suite instead of recursing.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FLOOR_GUARD = REPO_ROOT / "tests" / "check_suite_floors.py"
GEN_BALANCE = REPO_ROOT / "tools" / "gen_balance.py"
BOOTSTRAP = REPO_ROOT / "bootstrap.py"

#: Where session cards live and what the flip derivation diffs against.
SESSIONS_DIR = ".sessions"
FLIP_BASE_REF = "origin/main"


def _banner(step: str, label: str, command: list[str]) -> None:
    print("=" * 72, flush=True)
    print(f"preflight {step}: {label}", flush=True)
    print(f"  $ {' '.join(command)}", flush=True)
    print("=" * 72, flush=True)


def _run(step: str, label: str, command: list[str]) -> None:
    """Run one gate; on failure print a red banner and exit with its code."""
    _banner(step, label, command)
    env = dict(os.environ, SBG_PREFLIGHT="1")
    proc = subprocess.run(command, cwd=REPO_ROOT, env=env)
    if proc.returncode != 0:
        print("=" * 72, flush=True)
        print(f"preflight FAILED at {step} ({label}) — exit {proc.returncode}", flush=True)
        print("=" * 72, flush=True)
        raise SystemExit(proc.returncode)


def _derived_roots() -> list[str]:
    """Ask the floor guard for the registry-derived pytest roots."""
    proc = subprocess.run(
        [sys.executable, str(FLOOR_GUARD), "--print-suites"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        print("preflight FAILED deriving pytest roots (--print-suites)", flush=True)
        raise SystemExit(proc.returncode or 1)
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def _added_session_cards() -> list[str]:
    """Session cards ADDED on this branch relative to ``FLIP_BASE_REF``.

    The same derivation the substrate gate's added-card lane runs in CI:
    ``--diff-filter=A`` over ``origin/main...HEAD`` (three-dot = against the
    merge base) scoped to ``.sessions/*.md`` minus the README. Returned in
    git's (path-sorted) order.
    """
    command = [
        "git",
        "diff",
        "--name-only",
        "--diff-filter=A",
        f"{FLIP_BASE_REF}...HEAD",
        "--",
        f"{SESSIONS_DIR}/*.md",
        f":!{SESSIONS_DIR}/README.md",
    ]
    proc = subprocess.run(command, capture_output=True, text=True, cwd=REPO_ROOT)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        print(
            f"preflight FAILED deriving the flip card (git diff against {FLIP_BASE_REF})",
            flush=True,
        )
        raise SystemExit(proc.returncode or 1)
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def _pick_flip_card(added: list[str]) -> str | None:
    """The ONE card ``--flip`` grades, or ``None`` for the bare fallback.

    Multiple added cards are a loud error, not a guess: a flip grades one
    card, and picking silently is exactly the false-green class this
    derivation exists to close.
    """
    if not added:
        return None
    if len(added) > 1:
        print("=" * 72, flush=True)
        print(
            f"preflight FAILED deriving the flip card: {len(added)} session "
            f"cards ADDED on this branch ({FLIP_BASE_REF}...HEAD) — a flip "
            "grades ONE card:",
            flush=True,
        )
        for card in added:
            print(f"  {card}", flush=True)
        print("=" * 72, flush=True)
        raise SystemExit(1)
    return added[0]


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gate-parity preflight: floor guard, pytest, balance freshness.",
    )
    parser.add_argument(
        "--flip",
        action="store_true",
        help=(
            "append step 4 — `bootstrap.py check --strict` on the session "
            "card this branch ADDS vs origin/main (multiple added cards "
            "error loud; none falls back to bare strict with a banner) — so "
            "flip-readiness is one command grading the RIGHT card (red on a "
            "still-in-progress card is the designed born-red HOLD, not a "
            "defect)"
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    total = 4 if args.flip else 3

    flip_card: str | None = None
    if args.flip:
        # Derive BEFORE any gate runs: a multi-card branch should fail in
        # milliseconds, not after a full suite pass.
        flip_card = _pick_flip_card(_added_session_cards())
        if flip_card is None:
            print(
                f"flip card: none ADDED on this branch ({FLIP_BASE_REF}...HEAD) "
                "— control-fast-lane tree; step 4 runs bare strict "
                "(newest-by-mtime card fallback)",
                flush=True,
            )
        else:
            print(
                f"flip card derived from the branch diff "
                f"({FLIP_BASE_REF}...HEAD): {flip_card}",
                flush=True,
            )

    _run(f"1/{total}", "suite-floor guard", [sys.executable, str(FLOOR_GUARD)])

    roots = _derived_roots()
    _run(
        f"2/{total}",
        "pytest (registry-derived paths)",
        [sys.executable, "-m", "pytest", *roots, "-q"],
    )

    _run(f"3/{total}", "balance-page freshness", [sys.executable, str(GEN_BALANCE), "--check"])

    if args.flip:
        strict_command = [sys.executable, str(BOOTSTRAP), "check", "--strict"]
        if flip_card is not None:
            strict_command += ["--session-log", flip_card]
        _run(f"4/{total}", "flip-readiness (bootstrap check --strict)", strict_command)
        print("=" * 72, flush=True)
        print(
            "preflight GREEN — all four gates passed (floor guard, pytest, "
            "balance, strict) — flip-ready",
            flush=True,
        )
        print("=" * 72, flush=True)
        return 0

    print("=" * 72, flush=True)
    print("preflight GREEN — all three gates passed (floor guard, pytest, balance)", flush=True)
    print("=" * 72, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
