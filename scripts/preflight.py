#!/usr/bin/env python3
"""Repo-local preflight wrapper — the kit's conventional convergence path.

Contract (substrate-kit v1.16.0, ``substrate.config.json`` →
``preflight_scripts: ["scripts/preflight.py"]``; kit source
``_default_preflight_scripts`` + ``_run_preflight_scripts`` in
``bootstrap.py``): ``check``'s full lane runs this script from the repo
root under the same interpreter, and the CI substrate-gate's full lane
runs it too (its gate step invokes ``bootstrap.py check --strict``), so
the repo's check list is enforced in both venues with zero workflow
edits. Until this file existed, that leg self-skipped with a NOTE and
neither venue ran it.

This repo's real check list already exists and is single-sourced:
``tools/preflight.py`` (#128's gate-parity preflight — suite-floor guard
→ pytest over registry-derived roots → balance freshness — the exact
sequence ``tests.yml`` runs). This wrapper therefore DELEGATES to it in
its default 3-step mode rather than duplicating the gate sequence; the
plant-a-wrapper-not-edit-the-config shape follows superbot-idle PR #137
(squash ``8ff9f59``), the sibling implementation of the same kit
contract.

Venue note (idle #137's, carried here): the substrate-gate runner
installs NO third-party deps (stdlib-only by design), while ``tests.yml``
pip-installs pytest before its run. To keep one check list that works in
BOTH venues, missing deps are installed quietly here first (a no-op
locally and in ``tests.yml`` where they already exist).

Nested-run guard: ``tools/preflight.py --flip`` step 4 invokes
``bootstrap.py check --strict`` itself (with ``SBG_PREFLIGHT=1`` in the
child env) — without a guard that inner check would re-enter this
wrapper and run the full suite a second time inside the same preflight.
When ``SBG_PREFLIGHT=1`` this wrapper self-skips with a note and exit 0:
the outer ``tools/preflight.py`` run owns the leg, the same doctrine as
the kit's own ``SUBSTRATE_KIT_PREFLIGHT`` check-within-check guard.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GATE_PARITY_PREFLIGHT = REPO_ROOT / "tools" / "preflight.py"

# (import-name, pip-name) — what tests.yml installs before running the
# same gate sequence in its venue.
_DEPS = (("pytest", "pytest"),)


def _ensure_deps() -> None:
    missing = [pip for mod, pip in _DEPS if importlib.util.find_spec(mod) is None]
    if not missing:
        return
    print(f"preflight-wrapper: installing missing deps: {' '.join(missing)}", flush=True)
    proc = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--quiet", *missing],
        check=False,
    )
    if proc.returncode != 0:
        print(
            f"preflight-wrapper: pip install {' '.join(missing)} failed "
            f"(exit {proc.returncode}) — cannot run the check list",
            flush=True,
        )
        sys.exit(1)


def main() -> int:
    if os.environ.get("SBG_PREFLIGHT") == "1":
        print(
            "preflight-wrapper: skipped — already inside a tools/preflight.py "
            "run (SBG_PREFLIGHT=1; the outer preflight owns this leg).",
            flush=True,
        )
        return 0
    _ensure_deps()
    proc = subprocess.run(
        [sys.executable, str(GATE_PARITY_PREFLIGHT)],
        cwd=REPO_ROOT,
        check=False,
    )
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
