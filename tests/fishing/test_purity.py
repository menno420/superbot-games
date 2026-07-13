"""The load-bearing guarantee: the fishing core imports zero impure deps.

Mirrors ``tests/mining/test_purity.py``. The fishing core is PURE — stdlib +
dataclasses/random only — and legitimately reuses the shared PURE mining
primitives (``games.mining.core.energy`` / ``.equipment``), so the guard ALLOWS
every ``games.`` import and forbids only the host / db / service layers. Crucially
it must NOT pull in ``services.fishing_workflow`` (the impure seam layer lives
above the core, never below it).
"""

from __future__ import annotations

import importlib
import pkgutil
import sys

import games.fishing.core as core

_FORBIDDEN = ("discord", "asyncpg", "aiohttp", "requests", "sqlalchemy", "psycopg")
_FORBIDDEN_PREFIXES = ("services", "cogs", "views", "utils.", "disbot")


def test_core_imports_no_discord_db_or_host_layers() -> None:
    before = set(sys.modules)
    modules = [m.name for m in pkgutil.iter_modules(core.__path__)]
    # The fishing core is exactly five modules (catch / economy / rng / species
    # / spots — economy added by the V043 wiring, ORDER 007); pin it so a new
    # module cannot slip in an impure import untested.
    assert sorted(modules) == ["catch", "economy", "rng", "species", "spots"]
    for m in modules:
        importlib.import_module(f"games.fishing.core.{m}")
    loaded = set(sys.modules) - before

    forbidden_hits = [
        n
        for n in loaded
        if any(n == f or n.startswith(f + ".") for f in _FORBIDDEN)
        or n.startswith(_FORBIDDEN_PREFIXES)
    ]
    assert forbidden_hits == [], f"impure imports leaked in: {forbidden_hits}"
