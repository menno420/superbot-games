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

Exit status: 0 when every step passes; the FIRST failing step's exit code
otherwise (later steps do not run — fix, rerun, repeat).

Re-entrancy: ``SBG_PREFLIGHT=1`` is set for the pytest step so the preflight
smoke test in ``tests/tools/`` (which subprocesses this script) can skip
itself inside a preflight-launched suite instead of recursing.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FLOOR_GUARD = REPO_ROOT / "tests" / "check_suite_floors.py"
GEN_BALANCE = REPO_ROOT / "tools" / "gen_balance.py"


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


def main() -> int:
    _run("1/3", "suite-floor guard", [sys.executable, str(FLOOR_GUARD)])

    roots = _derived_roots()
    _run("2/3", "pytest (registry-derived paths)", [sys.executable, "-m", "pytest", *roots, "-q"])

    _run("3/3", "balance-page freshness", [sys.executable, str(GEN_BALANCE), "--check"])

    print("=" * 72, flush=True)
    print("preflight GREEN — all three gates passed (floor guard, pytest, balance)", flush=True)
    print("=" * 72, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
