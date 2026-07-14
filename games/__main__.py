"""``python3 -m games`` — the GAME HUB launcher (list + launch both games).

This is the unified front door the two standalone CLIs
(``python3 -m games.mining`` / ``python3 -m games.fishing``) were missing: one
place that shows every playable game and launches the one you pick. It is the
COMPOSITION ROOT for the neutral :mod:`services.world_registry` — at startup it
calls :func:`games.registry_wiring.wire_games`, which binds each game's
standalone CLI ``main`` into a :class:`~services.world_registry.WorldEntry` as an
OPAQUE opener. The registry itself never imports a game; this module supplies the
``games -> registry`` edge from above.

The player loop is factored so a test can drive it TTY-free: :func:`run_hub`
takes a list of command strings plus an injectable *registry* and *launch*, so a
test can assert "picking mining invoked mining's opener" against a FAKE launcher
without ever spawning an interactive sub-session. :func:`main` wraps an
``input()`` loop around the same dispatch, handling EOF / quit / unknown-id
cleanly.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Callable

from services import world_registry
from services.world_registry import WorldEntry

from games.registry_wiring import wire_games

PROMPT = "games> "

#: Default launcher: run the entry's opaque opener as the game's session and
#: normalise its return (``None`` -> ``0``) to a process-style exit code. The hub
#: passes an injectable *launch* so a test can substitute a fake that records the
#: pick instead of entering a sub-REPL.
def _default_launch(entry: WorldEntry) -> int:
    code = entry.opener()
    return code if isinstance(code, int) else 0


# ---------------------------------------------------------------------------
# Rendering — pure string builders (no printing), so tests can assert on them
# ---------------------------------------------------------------------------
def listing_lines(entries: tuple[WorldEntry, ...]) -> list[str]:
    """The hub menu: one numbered ``id · title · blurb`` row per registered game."""
    if not entries:
        return ["No games are registered."]
    lines = ["Available games (type 'play <id>' or a number):"]
    for idx, entry in enumerate(entries, start=1):
        lines.append(f"  {idx}. {entry.game_id:<10} {entry.title} — {entry.blurb}")
    return lines


def launching_line(game_id: str) -> str:
    """The pre-launch banner. Emitted by the CALLER'S launch wrapper BEFORE the
    opener runs — the opener is a synchronous sub-session, so a line returned
    from :func:`hub_step` after dispatch would print only once the game ended.
    """
    return f"Launching {game_id}…"


def help_lines() -> list[str]:
    """The command reference printed by ``help`` (and on an unknown command)."""
    return [
        "Commands:",
        "  list                 show every registered game",
        "  play <id>            launch a game by id (e.g. play mining)",
        "  play <n> / <n>       launch a game by its list number",
        "  help                 show this list",
        "  quit / exit          leave the hub",
    ]


# ---------------------------------------------------------------------------
# One command → hub dispatch
# ---------------------------------------------------------------------------
@dataclass
class HubStep:
    """What running one hub input line produced."""

    lines: list[str] = field(default_factory=list)
    quit: bool = False
    launched: str | None = None  # game_id dispatched to a launcher this step


def _resolve(token: str, entries: tuple[WorldEntry, ...]) -> WorldEntry | None:
    """Resolve *token* (a game_id or a 1-based list number) to an entry, or None."""
    if token.isdigit():
        idx = int(token)
        if 1 <= idx <= len(entries):
            return entries[idx - 1]
        return None
    return world_lookup(token, entries)


def world_lookup(game_id: str, entries: tuple[WorldEntry, ...]) -> WorldEntry | None:
    """Find an entry by exact ``game_id`` within *entries* (case-insensitive)."""
    want = game_id.lower()
    for entry in entries:
        if entry.game_id.lower() == want:
            return entry
    return None


def hub_step(
    line: str,
    entries: tuple[WorldEntry, ...],
    *,
    launch: Callable[[WorldEntry], int | None],
) -> HubStep:
    """Run one hub input *line* against *entries*; never raises on bad input.

    An empty line is a no-op; ``list`` prints the menu; ``help`` / an unknown
    command prints the help; ``quit`` stops; ``play <id>`` (or a bare id /
    number) dispatches to the resolved entry's opener via *launch*. An unknown id
    or an out-of-range number is reported gracefully with the menu, launching
    nothing.
    """
    tokens = line.strip().split()
    if not tokens:
        return HubStep()
    verb = tokens[0].lower()
    args = tokens[1:]

    if verb in {"quit", "exit", "q"}:
        return HubStep(quit=True)
    if verb in {"list", "ls", "games"}:
        return HubStep(lines=listing_lines(entries))
    if verb in {"help", "?"}:
        return HubStep(lines=help_lines())

    if verb == "play":
        if not args:
            return HubStep(lines=["Usage: play <id> (or a number).", *listing_lines(entries)])
        target = args[0]
    elif verb.isdigit() or world_lookup(verb, entries) is not None:
        # Bare number or bare known id is a shortcut for `play <that>`.
        target = verb
    else:
        return HubStep(lines=[f"Unknown command: {verb!r}.", *help_lines()])

    entry = _resolve(target, entries)
    if entry is None:
        valid = ", ".join(e.game_id for e in entries) or "(none)"
        return HubStep(
            lines=[
                f"Unknown game: {target!r}. Valid games: {valid}.",
                *listing_lines(entries),
            ]
        )

    # The "Launching …" banner is NOT returned here: the opener runs synchronously
    # inside launch(), so a returned line would render only after the game session
    # ended. Callers announce via launching_line() BEFORE invoking their launcher.
    launch(entry)
    return HubStep(launched=entry.game_id)


# ---------------------------------------------------------------------------
# Scripted (non-interactive) driver — the testable entry point
# ---------------------------------------------------------------------------
@dataclass
class HubResult:
    """The outcome of a scripted hub session (what a test asserts against)."""

    lines: list[str]
    launched: list[str]  # game_ids dispatched, in order

    @property
    def text(self) -> str:
        """The whole hub transcript as one string."""
        return "\n".join(self.lines)


def run_hub(
    commands: list[str],
    *,
    registry=None,
    launch: Callable[[WorldEntry], int | None] | None = None,
) -> HubResult:
    """Drive a scripted, TTY-free hub session and return its :class:`HubResult`.

    *registry* is the world-registry module (or a compatible stand-in exposing
    ``all_entries``); when ``None`` the default :mod:`services.world_registry` is
    used AND freshly wired via :func:`games.registry_wiring.wire_games`, so the
    two real games are present. *launch* is the game launcher — injectable so a
    test can pass a FAKE that records the pick instead of entering a real
    sub-session (the default runs the entry's opaque opener). A ``quit`` (or the
    end of the list) closes the session.
    """
    if registry is None:
        registry = world_registry
        wire_games(registry)
    if launch is None:
        launch = _default_launch

    entries = tuple(registry.all_entries())
    lines: list[str] = list(listing_lines(entries))
    launched: list[str] = []

    def announcing_launch(entry: WorldEntry) -> int | None:
        # Record the banner BEFORE the opener runs, so the transcript shows the
        # launch preceding the game session (the launcher itself is unchanged).
        lines.append(launching_line(entry.game_id))
        return launch(entry)

    for command in commands:
        step = hub_step(command, entries, launch=announcing_launch)
        if step.quit:
            break
        lines.extend(step.lines)
        if step.launched is not None:
            launched.append(step.launched)

    lines.append("Thanks for playing — see you at the hub!")
    return HubResult(lines=lines, launched=launched)


# ---------------------------------------------------------------------------
# Interactive loop — thin input() wrapper over hub_step; handles EOF/quit clean
# ---------------------------------------------------------------------------
def main() -> int:
    """Run the interactive hub REPL. Returns a process exit code."""
    wire_games(world_registry)
    entries = tuple(world_registry.all_entries())

    print("🎮  Superbot Games — the hub. Type 'help' for commands, 'quit' to leave.")
    for line in listing_lines(entries):
        print(line)

    def interactive_launch(entry: WorldEntry) -> int:
        # Print the banner BEFORE the opener runs its synchronous sub-session,
        # so "Launching X…" precedes the game instead of trailing its summary.
        print(launching_line(entry.game_id))
        return _default_launch(entry)

    while True:
        try:
            line = input(PROMPT)
        except (EOFError, KeyboardInterrupt):
            print()  # clean newline after ^D / ^C
            break
        step = hub_step(line, entries, launch=interactive_launch)
        if step.quit:
            break
        for out in step.lines:
            print(out)

    print("Thanks for playing — see you at the hub!")
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = [
    "PROMPT",
    "listing_lines",
    "launching_line",
    "help_lines",
    "HubStep",
    "hub_step",
    "world_lookup",
    "HubResult",
    "run_hub",
    "main",
]
