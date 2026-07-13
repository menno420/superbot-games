"""Standalone fishing CLI — a playable text session over the audited seam.

This is the *player loop* the fishing ladder was missing: rung 1 shipped the
pure core (``games/fishing/core/`` — the stateless catch resolver + the
species/spot data tables), rung 2 shipped the audited WORKFLOW seam
(``services/fishing_workflow.py``, the single :func:`~services.fishing_workflow.cast`
action), but nothing actually *drove* the seam — there was no way to sit down and
cast a line. This module is that driver: a text REPL that holds one mutable
:class:`~services.fishing_workflow.FishingState`, an in-memory
:class:`~services.audit.InMemorySink`, and dispatches player commands to the one
seam action (``cast``) plus the read-only navigation verbs (``spot`` / ``spots``
/ ``status`` / ``haul``).

It is deliberately **thin and non-balance**: every bite chance, catch weight,
size and narration string is read VERBATIM from the seam/core (this module
invents no balance number). Its only additions are UX / orchestration — a status
header, a discoverable ``spots`` listing (+ valid-id hints when you mistype a
spot), a clear help screen, and an end-of-session summary (casts made, fish
caught by species, audit rows recorded).

Testability: the loop is factored so a test can drive a scripted session with no
TTY — :func:`run_commands` takes a list of command strings (plus an optional
injected sink / state / clock / rng) and returns a :class:`SessionResult`. The
``__main__`` module wraps an ``input()`` loop around the same :func:`step`.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime, timezone

from services import fishing_workflow as fw
from services.audit import InMemorySink

from games.fishing.core import spots as spot_table
from games.fishing.core import species as species_table
from games.mining.core import energy

#: The spot a fresh angler starts at — the in-table NEUTRAL ``dock`` row (an
#: identity catch profile). Read off the spot table, never a new balance choice.
STARTER_SPOT = "dock"

PROMPT = "fishing> "

#: The one verb that routes to a state-changing seam action (as opposed to the
#: read-only ``spot`` / ``spots`` / ``status`` / ``haul`` / ``help`` and the
#: ``quit`` control verbs).
_ACTION_VERBS = frozenset({"cast"})


# ---------------------------------------------------------------------------
# Fresh-player state — assembled from REAL core defaults (no invented numbers)
# ---------------------------------------------------------------------------
def new_state() -> fw.FishingState:
    """A fresh fishing session built from the core's own defaults.

    Energy starts at the shared engine's full bar
    (:data:`games.mining.core.energy.MAX_ENERGY`), the spot at the in-table
    neutral :data:`STARTER_SPOT` (``dock``), and an empty haul. Every value is
    quoted from the core — nothing here is a new balance number.
    """
    return fw.FishingState(
        spot_id=STARTER_SPOT,
        energy=energy.MAX_ENERGY,
        haul={},
    )


# ---------------------------------------------------------------------------
# Rendering — pure string builders (no printing), so tests can assert on them
# ---------------------------------------------------------------------------
def _spot_label(spot_id: str) -> str:
    """A friendly ``🪝 The Old Dock`` label for *spot_id* (falls back to the
    core's neutral default profile for an unknown id — honest, no raise)."""
    spot = spot_table.profile_for(spot_id)
    return f"{spot.emoji} {spot.name}"


def _render_haul(haul: dict[str, int]) -> str:
    """A compact ``2× Bass, 1× Pike`` haul line (or ``(nothing yet)``).

    Counts are keyed on neutral species ids; the display noun is read off the
    species table so a re-theme flows through untouched.
    """
    rows = [(sid, qty) for sid, qty in haul.items() if qty > 0]
    if not rows:
        return "(nothing yet)"
    rows.sort(key=lambda r: r[0])
    parts = []
    for sid, qty in rows:
        name = species_table.get(sid).name if species_table.is_species(sid) else sid
        parts.append(f"{qty}× {name}")
    return ", ".join(parts)


def status_lines(state: fw.FishingState) -> list[str]:
    """The status header: energy bar, current spot, running haul."""
    return [
        "─" * 44,
        f"  energy: {energy.bar(state.energy)}",
        f"  spot:   {_spot_label(state.spot_id)}",
        f"  haul:   {_render_haul(state.haul)}",
        "─" * 44,
    ]


def spots_lines(current: str | None = None) -> list[str]:
    """The ``spots`` listing — every fishable biome, its vibe, and its id.

    UX-only discoverability: the valid ids the ``spot`` command accepts are
    :func:`games.fishing.core.spots.spot_ids`; each is shown with its display
    name and flavour so a player can pick without reading the source.
    """
    lines = ["Fishing spots (use 'spot <id>' to switch):"]
    for spot in spot_table.all_spots():
        marker = " (here)" if spot.spot_id == current else ""
        lines.append(f"  {spot.emoji} {spot.spot_id:<12} {spot.name} — {spot.flavor}{marker}")
    return lines


def help_lines() -> list[str]:
    """The command reference printed by ``help`` (and on an unknown command)."""
    valid = ", ".join(spot_table.spot_ids())
    return [
        "Commands:",
        "  cast                 cast once at your current spot — spend energy, maybe land a fish",
        f"  spot <id>            move to a fishing spot (valid: {valid})",
        "  spots                list every spot + its vibe",
        "  status / haul        show energy, current spot, and your running haul",
        "  help                 show this list",
        "  quit / exit          end the session (prints a summary)",
    ]


def summary_lines(
    state: fw.FishingState,
    sink: InMemorySink,
    *,
    casts_made: int,
) -> list[str]:
    """The friendly end-of-session recap printed on quit."""
    caught = sum(state.haul.values())
    lines = [
        "─" * 44,
        "Session summary:",
        f"  casts made:      {casts_made}",
        f"  fish caught:     {caught}",
    ]
    if caught:
        lines.append(f"  by species:      {_render_haul(state.haul)}")
    lines += [
        f"  audit records:   {len(sink.records)}",
        f"  final spot:      {_spot_label(state.spot_id)}",
        "Tight lines — thanks for playing!",
    ]
    return lines


# ---------------------------------------------------------------------------
# One command → seam dispatch
# ---------------------------------------------------------------------------
@dataclass
class StepResult:
    """What running one input line produced."""

    lines: list[str] = field(default_factory=list)
    quit: bool = False
    is_cast: bool = False  # routed to the state-changing ``cast`` seam verb
    ok: bool = False  # the seam Result was ``ok`` (a committed mutation)


def _cast_extra(state: fw.FishingState, result: fw.FishingResult) -> list[str]:
    """UX-only lines printed after a cast — energy + running haul (non-balance).

    The seam already returns the honest narration (a bite, an empty cast, or the
    too-tired 😴 rest) as ``result.message``; this only surfaces the *player*
    state that moved, without inventing any economy number.
    """
    return [
        f"  energy: {energy.bar(state.energy)}",
        f"  haul:   {_render_haul(state.haul)}",
    ]


def step(
    state: fw.FishingState,
    sink: InMemorySink,
    line: str,
    *,
    now: datetime | None = None,
    rng: random.Random | None = None,
) -> StepResult:
    """Run one input *line* against *state*/*sink*; return its output + flags.

    Never raises on bad input — an empty line is a no-op, an unknown command
    prints the help, and an unknown spot id is handled gracefully (the core
    resolves an unknown spot to its neutral default, so the CLI just nudges the
    player with the valid ids and does NOT switch). A ``cast`` prints the seam's
    Result message plus the refreshed energy/haul; a too-tired cast prints the
    honest rest message and records nothing.
    """
    tokens = line.strip().split()
    if not tokens:
        return StepResult()
    verb = tokens[0].lower()
    args = tokens[1:]

    if verb in {"quit", "exit", "q"}:
        return StepResult(quit=True)
    if verb in {"status", "haul"}:
        return StepResult(lines=status_lines(state))
    if verb in {"spots"}:
        return StepResult(lines=spots_lines(current=state.spot_id))
    if verb in {"help", "?"}:
        return StepResult(lines=help_lines())

    if verb == "spot":
        if not args:
            return StepResult(lines=["Usage: spot <id>", *spots_lines(current=state.spot_id)])
        target = args[0]
        if not spot_table.is_spot(target):
            valid = ", ".join(spot_table.spot_ids())
            return StepResult(
                lines=[
                    f"Unknown spot: {target!r}. Valid spots: {valid}.",
                    "  (Try 'spots' to see each one's vibe.)",
                ]
            )
        state.spot_id = target
        return StepResult(lines=[f"You move to {_spot_label(target)}.", *status_lines(state)])

    if verb not in _ACTION_VERBS:
        return StepResult(lines=[f"Unknown command: {verb!r}.", *help_lines()])

    # The one state-changing action — cast at the current spot.
    result = fw.cast(state, sink=sink, rng=rng, now=now)
    out = [result.message]
    out += _cast_extra(state, result)
    return StepResult(lines=out, is_cast=True, ok=result.ok)


# ---------------------------------------------------------------------------
# Scripted (non-interactive) driver — the testable entry point
# ---------------------------------------------------------------------------
@dataclass
class SessionResult:
    """The outcome of a scripted session (what a test asserts against)."""

    lines: list[str]
    state: fw.FishingState
    sink: InMemorySink
    casts_made: int  # ``cast`` commands routed to the seam (ok OR too-tired)
    ok_casts: int  # casts that committed (== len(sink.records))

    @property
    def text(self) -> str:
        """The whole session transcript as one string."""
        return "\n".join(self.lines)


def run_commands(
    commands: list[str],
    *,
    sink: InMemorySink | None = None,
    state: fw.FishingState | None = None,
    now: datetime | None = None,
    rng: random.Random | None = None,
) -> SessionResult:
    """Drive a scripted, TTY-free session and return its :class:`SessionResult`.

    Feeds each string in *commands* through :func:`step` against a shared state +
    sink. Injectable *sink* / *state* / *now* / *rng* make a run fully
    deterministic for tests. A ``quit`` (or the end of the list) closes the
    session and appends the summary. ``casts_made`` counts every ``cast`` verb
    the player issued; ``ok_casts`` counts only the ones that committed a
    mutation (a too-tired cast is a cast made but not an ok cast, and records
    nothing).
    """
    now = now if now is not None else datetime(2026, 7, 13, 12, 0, 0, tzinfo=timezone.utc)
    if state is None:
        state = new_state()
    if sink is None:
        sink = InMemorySink()

    lines: list[str] = list(status_lines(state))
    casts_made = 0
    ok_casts = 0

    for command in commands:
        res = step(state, sink, command, now=now, rng=rng)
        if res.quit:
            break
        lines.extend(res.lines)
        if res.is_cast:
            casts_made += 1
            if res.ok:
                ok_casts += 1

    lines.extend(summary_lines(state, sink, casts_made=casts_made))
    return SessionResult(
        lines=lines,
        state=state,
        sink=sink,
        casts_made=casts_made,
        ok_casts=ok_casts,
    )


# ---------------------------------------------------------------------------
# Interactive loop — thin input() wrapper over step(); handles EOF/quit cleanly
# ---------------------------------------------------------------------------
def main() -> int:
    """Run the interactive REPL. Returns a process exit code."""
    sink = InMemorySink()
    state = new_state()
    casts_made = 0

    print("🎣  Standalone Fishing — type 'help' for commands, 'quit' to leave.")
    for line in status_lines(state):
        print(line)

    while True:
        try:
            line = input(PROMPT)
        except (EOFError, KeyboardInterrupt):
            print()  # clean newline after ^D / ^C
            break
        res = step(state, sink, line, now=datetime.now(timezone.utc))
        if res.quit:
            break
        for out in res.lines:
            print(out)
        if res.is_cast:
            casts_made += 1

    for line in summary_lines(state, sink, casts_made=casts_made):
        print(line)
    return 0


__all__ = [
    "STARTER_SPOT",
    "new_state",
    "status_lines",
    "spots_lines",
    "help_lines",
    "summary_lines",
    "StepResult",
    "step",
    "SessionResult",
    "run_commands",
    "main",
]
