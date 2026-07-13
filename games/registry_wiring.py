"""Composition root — bind each playable game into the neutral world registry.

This is the ONE place that knows a concrete game's launcher. It imports the
per-game CLIs (``games.mining.cli`` / ``games.fishing.cli``) and constructs a
:class:`~services.world_registry.WorldEntry` for each, passing the CLI's
``main`` as the entry's opaque ``opener``. The neutral registry
(``services/world_registry.py``) never imports a game — this module supplies the
``games -> registry`` edge from ABOVE, so the services layer stays free of any
``services -> games`` dependency (the oracle's opener-as-opaque-callable rule).

Wiring is idempotent: :func:`wire_games` clears then re-registers, so calling it
more than once (or from a test) yields exactly the two entries in a stable order
and never double-registers.
"""

from __future__ import annotations

from services import world_registry

from games.fishing import cli as fishing_cli
from games.mining import cli as mining_cli

#: The catalogue this root binds, in listing order. Each row is
#: ``(game_id, title, blurb, opener)`` — the opener is the standalone CLI's
#: ``main`` (an opaque ``Callable[[], int]`` from the registry's point of view).
_GAMES = (
    (
        "mining",
        "⛏️  Mining",
        "Dig, descend, and sell your haul over the audited mining seam.",
        mining_cli.main,
    ),
    (
        "fishing",
        "🎣  Fishing",
        "Cast a line across biomes and land a haul over the audited cast seam.",
        fishing_cli.main,
    ),
)


def wire_games(registry=world_registry) -> None:
    """Register both playable games into *registry* (idempotent clear-then-add).

    Takes the registry module (or a compatible stand-in exposing ``clear`` /
    ``register``) so a test can inject a fake and assert what got wired without
    touching module-global state.
    """
    registry.clear()
    for game_id, title, blurb, opener in _GAMES:
        registry.register(
            world_registry.WorldEntry(
                game_id=game_id,
                title=title,
                blurb=blurb,
                opener=opener,
            )
        )


__all__ = ["wire_games"]
