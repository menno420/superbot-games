"""Game-neutral world registry — the in-repo hub spine (opener-as-opaque-callable).

This is the neutral front-door registry every playable game docks into. It
mirrors the oracle's shipped ``disbot/services/world_registry.py`` (the
``WorldEntry`` seam): a game announces itself with one :class:`WorldEntry`, and
the hub (the composition root) lists and launches them — *without* this module
ever importing a game.

The load-bearing rule is the **opener-as-OPAQUE-callable** discipline. A
``WorldEntry`` carries an ``opener`` — a plain ``Callable`` the registry never
introspects, imports, or knows the origin of. That keeps this module in the
services (WORKFLOW) layer free of any ``services -> games`` edge: exactly as the
oracle's registry keeps no ``services -> views`` edge. The composition root (the
``python -m games`` hub, via ``games/registry_wiring.py``) is the ONLY place that
knows a concrete game's launcher and binds it into an entry. Adding a new game is
one ``register`` call at that root — never an edit here.

Stdlib-only, so CI stays hermetic. State is a module-level ordered registry;
:func:`clear` resets it (registration is done at the composition root and is
idempotent there, so tests can rewire without leaking entries between cases).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class WorldEntry:
    """One game's registration in the hub — a neutral, opaque-opener seam.

    Copied in spirit from the oracle's ``WorldEntry`` (buildability map §world
    spine). The ``opener`` is an OPAQUE ``Callable`` the registry never calls or
    inspects — only the hub does, when the player picks this entry. Its return is
    a process-style exit code (``int``) or ``None`` (treated as success), so an
    entry can wrap a game's ``main()`` / ``run_commands`` verbatim.
    """

    game_id: str  # stable, url-safe id the player types (e.g. "mining")
    title: str  # short human title shown in the hub listing
    blurb: str  # one-line pitch shown beside the title
    opener: Callable[..., int | None]  # opaque launcher — supplied by the root


# The ordered registry. Insertion order is the listing order the hub shows, so a
# dict (ordered since 3.7) both dedupes on game_id and preserves stable order.
_REGISTRY: dict[str, WorldEntry] = {}


def register(entry: WorldEntry) -> None:
    """Register *entry* under its ``game_id`` (last write wins for that id).

    Re-registering the same ``game_id`` replaces the prior entry in place without
    changing its position in the listing order, so the composition root can
    idempotently re-wire (clear-then-register or a guarded re-register) without
    duplicating a game or reshuffling the menu.
    """
    _REGISTRY[entry.game_id] = entry


def get(game_id: str) -> WorldEntry | None:
    """Return the registered :class:`WorldEntry` for *game_id*, or ``None``."""
    return _REGISTRY.get(game_id)


def all_entries() -> tuple[WorldEntry, ...]:
    """Every registered entry, in stable registration (insertion) order."""
    return tuple(_REGISTRY.values())


def clear() -> None:
    """Drop every registration (for tests / a clean re-wire at the root)."""
    _REGISTRY.clear()


__all__ = ["WorldEntry", "register", "get", "all_entries", "clear"]
