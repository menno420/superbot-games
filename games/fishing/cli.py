"""Standalone fishing CLI — a playable text session over the audited seam.

This is the *player loop* the fishing ladder was missing: rung 1 shipped the
pure core (``games/fishing/core/`` — the stateless catch resolver + the
species/spot data tables), rung 2 shipped the audited WORKFLOW seam
(``services/fishing_workflow.py``, the single :func:`~services.fishing_workflow.cast`
action), but nothing actually *drove* the seam — there was no way to sit down and
cast a line. This module is that driver: a text REPL that holds one mutable
:class:`~services.fishing_workflow.FishingState`, an in-memory
:class:`~services.audit.InMemorySink`, and dispatches player commands to the two
seam actions (``cast`` and the V043 ``sell`` leg —
:func:`~services.fishing_workflow.sell`, the audited sell-OR-cook mutation path)
plus the read-only navigation verbs (``spot`` / ``spots`` / ``status`` /
``haul``).

It is deliberately **thin and non-balance**: every bite chance, catch weight,
size, sell value, XP amount and narration string is read VERBATIM from the
seam/core (this module invents no balance number and duplicates no economy
logic — a sell routes through the seam's audited :func:`sell`, and the coins /
level / milestone readouts only format what the seam/economy module already
computed). Its only additions are UX / orchestration — a status header, a
discoverable ``spots`` listing (+ valid-id hints when you mistype a spot), a
clear help screen, and an end-of-session summary (casts made, fish caught by
species, coins, audit rows recorded).

Testability: the loop is factored so a test can drive a scripted session with no
TTY — :func:`run_commands` takes a list of command strings (plus an optional
injected sink / state / clock / rng) and returns a :class:`SessionResult`. The
``__main__`` module wraps an ``input()`` loop around the same :func:`step`.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable

from services import fishing_workflow as fw
from services.audit import InMemorySink

from games.fishing.core import economy
from games.fishing.core import spots as spot_table
from games.fishing.core import species as species_table
from games.mining.core import energy
from games.shared.cli import repl, run_scripted

#: The spot a fresh angler starts at — the in-table NEUTRAL ``dock`` row (an
#: identity catch profile). Read off the spot table, never a new balance choice.
STARTER_SPOT = "dock"

PROMPT = "fishing> "

#: The verbs that route to a state-changing seam action (as opposed to the
#: read-only ``spot`` / ``spots`` / ``status`` / ``haul`` / ``help`` and the
#: ``quit`` control verbs) — ``cast`` and the V043 ``sell`` leg. Derived from
#: the single dispatch table ``_ACTIONS`` in the dispatch section below,
#: never hand-synced.


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
    """The status header: energy bar, coins, level readout, spot, running haul.

    The coins / level lines are V043 surfacing only: the level is the
    STAT-NEUTRAL :func:`games.fishing.core.economy.level_for_xp` readout over
    the seam-accumulated ``game_xp`` — nothing here computes or feeds a stat.
    """
    level = economy.level_for_xp(state.game_xp)
    return [
        "─" * 44,
        f"  energy: {energy.bar(state.energy)}",
        f"  coins:  {state.coins}",
        f"  level:  L{level} ({state.game_xp} xp)",
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
        "  sell <species> [qty] sell landed fish at the sim-pinned value (default: all you hold)",
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
        f"  coins:           {state.coins}",
        f"  fishing level:   L{economy.level_for_xp(state.game_xp)} ({state.game_xp} xp)",
    ]
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
    is_sell: bool = False  # routed to the state-changing ``sell`` seam verb (V043)
    ok: bool = False  # the seam Result was ``ok`` (a committed mutation)


def _cast_extra(state: fw.FishingState, result: fw.FishingResult) -> list[str]:
    """UX-only lines printed after a cast — milestones, energy, xp, haul.

    The seam already returns the honest narration (a bite, an empty cast, or the
    too-tired 😴 rest) as ``result.message``; this only surfaces the *player*
    state that moved, without inventing any economy number. The milestone /
    xp / level values are quoted VERBATIM off the seam's
    :class:`~services.fishing_workflow.FishingResult` (V043 surfacing — a
    milestone is a readout, never a stat).
    """
    lines = [f"  🏅 milestone — fishing level {m} reached!" for m in result.milestones]
    lines.append(f"  energy: {energy.bar(state.energy)}")
    if result.xp_gained:
        lines.append(f"  xp:     +{result.xp_gained} → L{result.level_after} ({state.game_xp} xp)")
    lines.append(f"  haul:   {_render_haul(state.haul)}")
    return lines


def _sell_extra(state: fw.FishingState) -> list[str]:
    """UX-only lines printed after a committed sell — coins + remaining haul.

    The seam's :class:`~services.fishing_workflow.SellResult` message already
    carries the sim-pinned amounts; this only surfaces the refreshed balance.
    """
    return [
        f"  coins:  {state.coins}",
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
    Result message plus the refreshed energy/xp/haul (and any crossed V043
    milestone); a too-tired cast prints the honest rest message and records
    nothing. A ``sell`` routes through the seam's audited
    :func:`~services.fishing_workflow.sell` and prints its honest message —
    committed sells also print the refreshed coins/haul; the seam's no-ops
    (unknown species, too few held) change nothing and record nothing.
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

    return _ACTIONS[verb](state, sink, args, now=now, rng=rng)


def _do_sell(
    state: fw.FishingState,
    sink: InMemorySink,
    args: list[str],
    *,
    now: datetime | None,
    rng: random.Random | None,
) -> StepResult:
    """The V043 sell leg — routed through the seam's audited ``sell()``, the
    SINGLE mutation path (sell-OR-cook exclusivity lives there, not here)."""
    if not args:
        return StepResult(lines=["Usage: sell <species> [qty]  (see 'haul' for what you hold)"])
    # Grammar: a trailing INTEGER is the quantity; everything before it is the
    # (possibly multi-word) species — addressable by its neutral id OR its
    # display name. This mirrors the mining CLI's ``sell <item> [qty]`` split so
    # a multi-word display name ("Legendary Carp") resolves, not just the
    # single-token id ("legend_carp").
    if args[-1].lstrip("-").isdigit():
        name = " ".join(args[:-1])
        qty: int | None = int(args[-1])
    else:
        name = " ".join(args)
        qty = None
    if not name:
        # A bare quantity with no species (e.g. "sell 3").
        return StepResult(lines=["Usage: sell <species> [qty]  (see 'haul' for what you hold)"])

    resolved = species_table.resolve(name)
    if qty is None and resolved is None:
        # Trailing token is non-integer AND the whole phrase names no species.
        # Disambiguate a botched QUANTITY from part of a longer NAME exactly as
        # the mining CLI does: flag "Quantity must be a number" only when the
        # tokens BEFORE the last already resolve to a species yet the whole phrase
        # does not — so "sell bass lots" flags the bad quantity, while a genuine
        # multi-word display name ("sell Legendary Carp") still resolves.
        if len(args) >= 2 and species_table.resolve(" ".join(args[:-1])) is not None:
            return StepResult(lines=[f"Quantity must be a number, got {args[-1]!r}."])

    # Prefer the resolved neutral id (id match wins inside ``resolve``); fall back
    # to the lower-cased raw token so a genuinely unknown species still reaches
    # the seam for its honest "cannot be sold" no-op.
    species = resolved if resolved is not None else name.lower()
    if qty is None:
        # Mirror the mining CLI's default: sell everything you hold (or ask
        # the seam for 1, whose honest "You only have 0×" no-op answers).
        held = state.haul.get(species, 0)
        qty = held if held > 0 else 1
    sell_result = fw.sell(state, species, qty, sink=sink, now=now)
    out = [sell_result.message]
    if sell_result.ok:
        out += _sell_extra(state)
    return StepResult(lines=out, is_sell=True, ok=sell_result.ok)


def _do_cast(
    state: fw.FishingState,
    sink: InMemorySink,
    args: list[str],
    *,
    now: datetime | None,
    rng: random.Random | None,
) -> StepResult:
    """The other state-changing action — cast at the current spot."""
    result = fw.cast(state, sink=sink, rng=rng, now=now)
    out = [result.message]
    out += _cast_extra(state, result)
    return StepResult(lines=out, is_cast=True, ok=result.ok)


#: THE single source for the action-verb surface: verb → handler. The step()
#: gate (``_ACTION_VERBS``) is derived from this table, so the gate and the
#: routing cannot drift; the help-parity test pins ``help_lines()`` to it.
_ACTIONS = {
    "cast": _do_cast,
    "sell": _do_sell,
}

_ACTION_VERBS = frozenset(_ACTIONS)


# ---------------------------------------------------------------------------
# Shared per-step bookkeeping — ONE closure construction for BOTH drivers
# ---------------------------------------------------------------------------
@dataclass
class StepTally:
    """What the session's step closure accumulates across lines.

    Shared by the scripted and interactive drivers via :func:`make_step_fn`,
    so the two twins cannot count differently by construction.
    """

    casts_made: int = 0  # ``cast`` verbs routed to the seam (ok OR too-tired)
    ok_casts: int = 0  # casts that committed a mutation (one audit row each)


def make_step_fn(
    state: fw.FishingState,
    sink: InMemorySink,
    *,
    now: datetime | None = None,
    rng: random.Random | None = None,
) -> tuple[Callable[[str], StepResult], StepTally]:
    """Build THE per-step bookkeeping closure both drivers dispatch through.

    Before this factory, ``main()`` and :func:`run_commands` each hand-rolled
    a near-identical ``step_fn`` — a drift between the twins (interactive
    counting differently than scripted) would have been invisible to both
    suites, because each driver was only ever tested against itself.

    ``now=None`` (the interactive default) stamps each line with the live
    wall clock, exactly as ``main()`` always did; a fixed *now* makes a
    scripted run deterministic. Returns ``(step_fn, tally)`` — the caller
    reads the shared counters from *tally* after (or during) the session.
    """
    tally = StepTally()

    def step_fn(line: str) -> StepResult:
        at = now if now is not None else datetime.now(timezone.utc)
        res = step(state, sink, line, now=at, rng=rng)
        if res.is_cast:
            tally.casts_made += 1
            if res.ok:
                tally.ok_casts += 1
        return res

    return step_fn, tally


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
    ok_casts: int  # casts that committed (one audit row each; a committed
    # ``sell`` records its own row, so ``len(sink.records)`` >= ``ok_casts``)

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

    step_fn, tally = make_step_fn(state, sink, now=now, rng=rng)

    lines = run_scripted(
        step_fn,
        commands,
        banner_lines=status_lines(state),
        closing_lines=lambda: summary_lines(state, sink, casts_made=tally.casts_made),
    )
    return SessionResult(
        lines=lines,
        state=state,
        sink=sink,
        casts_made=tally.casts_made,
        ok_casts=tally.ok_casts,
    )


# ---------------------------------------------------------------------------
# Interactive loop — thin input() wrapper over step(); handles EOF/quit cleanly
# ---------------------------------------------------------------------------
def main() -> int:
    """Run the interactive REPL. Returns a process exit code."""
    sink = InMemorySink()
    state = new_state()
    step_fn, tally = make_step_fn(state, sink)

    return repl(
        step_fn,
        prompt=PROMPT,
        banner_lines=[
            "🎣  Standalone Fishing — type 'help' for commands, 'quit' to leave.",
            *status_lines(state),
        ],
        closing_lines=lambda: summary_lines(state, sink, casts_made=tally.casts_made),
    )


__all__ = [
    "STARTER_SPOT",
    "new_state",
    "status_lines",
    "spots_lines",
    "help_lines",
    "summary_lines",
    "StepResult",
    "step",
    "StepTally",
    "make_step_fn",
    "SessionResult",
    "run_commands",
    "main",
]
