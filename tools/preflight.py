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

so "am I ready to flip?" is one command: green means the tree passes every
tests-workflow gate AND strict. Mid-slice it stays red BY DESIGN — the
born-red card's in-progress Status is the strict gate's designed HOLD —
and goes green once the card flips complete. The default three-step mode
is byte-identical to the pre-flag behavior; CI (``tests.yml``) keeps
calling the bare command and never runs step 4.

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


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gate-parity preflight: floor guard, pytest, balance freshness.",
    )
    parser.add_argument(
        "--flip",
        action="store_true",
        help=(
            "append step 4 — `bootstrap.py check --strict` — so flip-readiness "
            "is one command (red on a still-in-progress card is the designed "
            "born-red HOLD, not a defect)"
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    total = 4 if args.flip else 3

    _run(f"1/{total}", "suite-floor guard", [sys.executable, str(FLOOR_GUARD)])

    roots = _derived_roots()
    _run(
        f"2/{total}",
        "pytest (registry-derived paths)",
        [sys.executable, "-m", "pytest", *roots, "-q"],
    )

    _run(f"3/{total}", "balance-page freshness", [sys.executable, str(GEN_BALANCE), "--check"])

    if args.flip:
        _run(
            f"4/{total}",
            "flip-readiness (bootstrap check --strict)",
            [sys.executable, str(BOOTSTRAP), "check", "--strict"],
        )
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
