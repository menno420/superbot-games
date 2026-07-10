"""The load-bearing guarantee: the mining core imports zero impure deps."""

from __future__ import annotations

import importlib
import pkgutil
import sys

import games.mining.core as core

_FORBIDDEN = ("discord", "asyncpg", "aiohttp", "requests", "sqlalchemy", "psycopg")
_FORBIDDEN_PREFIXES = ("services", "cogs", "views", "utils.", "disbot")


def test_core_imports_no_discord_db_or_host_layers() -> None:
    before = set(sys.modules)
    modules = [m.name for m in pkgutil.iter_modules(core.__path__)]
    assert len(modules) == 19
    for m in modules:
        importlib.import_module(f"games.mining.core.{m}")
    loaded = set(sys.modules) - before

    forbidden_hits = [
        n
        for n in loaded
        if any(n == f or n.startswith(f + ".") for f in _FORBIDDEN)
        or n.startswith(_FORBIDDEN_PREFIXES)
    ]
    assert forbidden_hits == [], f"impure imports leaked in: {forbidden_hits}"
