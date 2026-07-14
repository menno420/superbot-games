"""Sim-harness smoke registry — every sim's render path executes in CI.

Every balance harness's ``__main__`` entry is ``pragma: no cover`` and its
full-scale run is manual, which is exactly how #106's
``format_report(SimReport())`` ZeroDivisionError stayed latent: nothing ever
executed the renderers end-to-end in CI. This registry closes that gap
permanently: for every shipped sim it asserts ``format_report(run(**tiny_kw))``
returns non-empty text without raising, at deliberately tiny sweep bounds
(each entry measured well under a second).

Completeness is enforced, not hoped for: a glob over ``games/**/*_sim.py``
(test files excluded) must be a subset of the registry's module set, so a NEW
sim cannot ship without either a registry line here or a loud failure naming
it. The exploration survival sim (``games/exploration/survival/sim.py``) does
not match the ``*_sim.py`` glob and is enumerated explicitly — the registry is
the union of both signals.

A new sim costs one ``_REGISTRY`` entry: ``(dotted module path, tiny kwargs)``.
The module must expose the shared harness contract: ``run(**kwargs) -> report``
and ``format_report(report) -> str``.
"""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_GAMES_ROOT = _REPO_ROOT / "games"

# The registry: (dotted sim module, tiny sweep kwargs). Kwargs are the
# smallest bounds that still exercise every aggregation bucket the renderer
# walks — keep them tiny; this file is a smoke, not a balance re-derivation.
_REGISTRY: tuple[tuple[str, dict], ...] = (
    (
        "games.mining.sim.encounters_sim",
        dict(seeds=range(2), coord=range(-3, 3), depths=(0, 3)),
    ),
    (
        "games.shared.sim.economy_sim",
        dict(seeds=range(2), digs_per_seed=5, casts_per_seed=5),
    ),
    (
        "games.fishing.sim.catch_sim",
        dict(seeds=range(2), casts_per_spot=2),
    ),
    (
        "games.dnd.sim.menu_sim",
        dict(seeds=range(2)),
    ),
    # Not a *_sim.py name — the survival harness lives at survival/sim.py and
    # is enumerated explicitly (the glob below cannot see it).
    (
        "games.exploration.survival.sim",
        dict(seeds=range(2)),
    ),
)

_REGISTRY_MODULES = frozenset(module for module, _ in _REGISTRY)


def _module_path(dotted: str) -> Path:
    """The repo-relative file a dotted module name resolves to."""
    return _REPO_ROOT / (dotted.replace(".", "/") + ".py")


@pytest.mark.parametrize(
    ("module_name", "kwargs"),
    _REGISTRY,
    ids=[module for module, _ in _REGISTRY],
)
def test_sim_render_path_executes(module_name: str, kwargs: dict) -> None:
    """``format_report(run(**tiny_kw))`` returns non-empty text, no raise."""
    sim = importlib.import_module(module_name)
    report = sim.run(**kwargs)
    text = sim.format_report(report)
    assert isinstance(text, str)
    assert text.strip(), f"{module_name}.format_report returned empty text"


@pytest.mark.parametrize(
    ("module_name", "kwargs"),
    _REGISTRY,
    ids=[module for module, _ in _REGISTRY],
)
def test_registry_entries_resolve_to_real_files(
    module_name: str, kwargs: dict
) -> None:
    """Every registry line names a real module file and dict kwargs — a
    renamed/moved sim reddens its own entry instead of rotting silently."""
    assert _module_path(module_name).is_file(), (
        f"registry names {module_name} but "
        f"{_module_path(module_name).relative_to(_REPO_ROOT)} does not exist"
    )
    assert isinstance(kwargs, dict)


def test_registry_enumerates_every_sim_under_games() -> None:
    """Glob-derived completeness: every ``*_sim.py`` under games/ (test files
    excluded) must be registered above, so a new sim cannot dodge the smoke."""
    discovered = {
        path.relative_to(_REPO_ROOT).with_suffix("").as_posix().replace("/", ".")
        for path in _GAMES_ROOT.rglob("*_sim.py")
        if not path.name.startswith("test_")
        and "__pycache__" not in path.parts
    }
    assert discovered, "glob found no *_sim.py under games/ — sweep is broken"
    missing = discovered - _REGISTRY_MODULES
    assert not missing, (
        "sims exist under games/ that the smoke registry does not enumerate — "
        f"add a (module, tiny kwargs) line for: {sorted(missing)}"
    )
