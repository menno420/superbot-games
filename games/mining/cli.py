"""Standalone mining CLI — a playable text session over the audited seam.

This is the *player loop* the mining ladder was missing: rung 1 shipped the
pure core (``games/mining/core/``), rung 2 shipped the audited WORKFLOW seam
(``services/mining_workflow.py``), but nothing actually *drove* the seam — there
was no way to sit down and play. This module is that driver: a text REPL that
holds one mutable :class:`~services.mining_workflow.MiningState`, an in-memory
:class:`~services.audit.InMemorySink`, and dispatches player commands to the ten
seam actions (mine / harvest / sell / buy / repair / descend / ascend / build /
vault / skill).

It is deliberately **thin and non-balance**: every price, cost, loot weight and
gate is read VERBATIM from the seam/core (this module invents no economy number).
Its only additions are UX / orchestration — a status header, a help screen, a
discoverable descend hint when the surface lock blocks you, and an end-of-session
summary (actions taken, audit rows recorded, coins earned).

Testability: the loop is factored so a test can drive a scripted session with no
TTY — :func:`run_commands` takes a list of command strings (plus an optional
injected sink / state / clock / rng) and returns a :class:`SessionResult`. The
``__main__`` module wraps an ``input()`` loop around the same :func:`step`.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime, timezone

from services import mining_workflow as mw
from services.audit import InMemorySink

from games.mining.core import energy, equipment, world
from games.shared.cli import repl

#: The base tool a fresh player starts equipped with — the core's entry-tier
#: pickaxe (``games/mining/core/equipment.py``). Its durability is read from the
#: core's ``MAX_DURABILITY`` table, never invented here.
STARTER_TOOL = "pickaxe"

PROMPT = "mining> "

#: The verbs that route to a state-changing seam action (as opposed to the
#: read-only ``status`` / ``inv`` / ``help`` and the ``quit`` control verbs)
#: are ``_ACTION_VERBS`` — derived from the single dispatch table ``_ACTIONS``
#: in the dispatch section below, never hand-synced.


# ---------------------------------------------------------------------------
# Fresh-player state — assembled from REAL core defaults (no invented numbers)
# ---------------------------------------------------------------------------
def new_state(*, now: datetime | None = None) -> mw.MiningState:
    """A fresh mining session built from the core's own defaults.

    Energy starts at the core's full bar (:data:`energy.MAX_ENERGY`), depth 0
    (the Surface), 0 coins, an empty pack, and the entry-tier pickaxe equipped
    at its core-defined max durability. Every value is quoted from the core —
    nothing here is a new balance number.
    """
    now_dt = now if now is not None else datetime.now(timezone.utc)
    return mw.MiningState(
        equipped={equipment.TOOL: STARTER_TOOL},
        durability={STARTER_TOOL: equipment.max_durability(STARTER_TOOL) or 0},
        energy=energy.EnergyState(energy.MAX_ENERGY, int(now_dt.timestamp())),
    )


# ---------------------------------------------------------------------------
# Rendering — pure string builders (no printing), so tests can assert on them
# ---------------------------------------------------------------------------
def status_lines(state: mw.MiningState, *, now: datetime) -> list[str]:
    """The status header: coins, energy, tool + durability, depth, inventory."""
    now_unix = int(now.timestamp())
    settled = energy.settle(state.energy, now_unix)
    tool = state.equipped.get(equipment.TOOL)
    tool_line = "(no tool equipped)"
    if tool:
        dur = state.durability.get(tool)
        cap = equipment.max_durability(tool)
        if dur is not None and cap:
            tool_line = f"{tool} ({dur}/{cap})"
        elif dur is not None:
            tool_line = f"{tool} ({dur})"
        else:
            tool_line = tool
    light = state.equipped.get(equipment.LIGHT)
    if light:
        ldur = state.durability.get(light)
        lcap = equipment.max_durability(light)
        tool_line += f" · light: {light}" + (f" ({ldur}/{lcap})" if ldur is not None and lcap else "")

    lines = [
        "─" * 44,
        f"  coins:  {state.coins}",
        f"  energy: {energy.bar(settled.current)}",
        f"  gear:   {tool_line}",
        f"  depth:  {world.describe_position(state.depth)}",
        f"  pack:   {_render_inventory(state.inventory)}",
        "─" * 44,
    ]
    return lines


def _render_inventory(inventory: dict[str, int]) -> str:
    """A compact ``2× bronze, 1× stone`` pack line (or ``(empty)``)."""
    rows = [(name, qty) for name, qty in inventory.items() if qty > 0]
    if not rows:
        return "(empty)"
    rows.sort(key=lambda r: r[0])
    return ", ".join(f"{qty}× {name}" for name, qty in rows)


def help_lines() -> list[str]:
    """The command reference printed by ``help`` (and on an unknown command)."""
    return [
        "Commands:",
        "  mine                 dig once — spend energy, roll loot, wear the tool",
        "  harvest              chop once for wood",
        "  sell <item> [qty]    sell a resource (default: all you hold)",
        "  buy <item>           buy one shop item (e.g. buy torch)",
        "  repair <item>        fully repair a worn item (e.g. repair pickaxe)",
        "  descend / ascend     move one band deeper / back toward the Surface",
        "  build <structure> [level]   build/upgrade forge, home, or campfire",
        "  vault                upgrade your vault one level",
        "  skill <branch> [pts] spend skill points (mining/combat/fortune/crafting)",
        "  status / inv         show the status header",
        "  help                 show this list",
        "  quit / exit          end the session (prints a summary)",
    ]


def summary_lines(
    state: mw.MiningState,
    sink: InMemorySink,
    *,
    start_coins: int,
    ok_actions: int,
) -> list[str]:
    """The friendly end-of-session recap printed on quit."""
    return [
        "─" * 44,
        "Session summary:",
        f"  actions taken:   {ok_actions}",
        f"  audit records:   {len(sink.records)}",
        f"  coins earned:    {state.coins - start_coins}",
        f"  final depth:     {world.describe_position(state.depth)}",
        "Thanks for playing!",
    ]


# ---------------------------------------------------------------------------
# One command → seam dispatch
# ---------------------------------------------------------------------------
@dataclass
class StepResult:
    """What running one input line produced."""

    lines: list[str] = field(default_factory=list)
    quit: bool = False
    is_action: bool = False  # routed to a state-changing seam verb
    ok: bool = False  # the seam Result was ``ok`` (a committed mutation)


def _split_item_qty(args: list[str]) -> tuple[str, int | None]:
    """Split ``["iron", "3"]`` → ``("iron", 3)`` / ``["iron"]`` → ``("iron", None)``.

    A trailing integer is the quantity; everything before it is the (possibly
    multi-word) item name.
    """
    if args and args[-1].lstrip("-").isdigit():
        return " ".join(args[:-1]), int(args[-1])
    return " ".join(args), None


def _do_mine(state, sink, args, *, now, rng):
    return mw.mine(state, sink=sink, rng=rng, now=now)


def _do_harvest(state, sink, args, *, now, rng):
    return mw.harvest(state, sink=sink, rng=rng, now=now)


def _do_descend(state, sink, args, *, now, rng):
    return mw.descend(state, sink=sink, now=now)


def _do_ascend(state, sink, args, *, now, rng):
    return mw.ascend(state, sink=sink, now=now)


def _do_vault(state, sink, args, *, now, rng):
    return mw.vault_upgrade(state, sink=sink, now=now)


def _do_sell(state, sink, args, *, now, rng):
    item, qty = _split_item_qty(args)
    if not item:
        return None
    if qty is None:
        held = state.inventory.get(item, 0)
        qty = held if held > 0 else 1
    return mw.sell(state, item, qty, sink=sink, now=now)


def _do_buy(state, sink, args, *, now, rng):
    item = " ".join(args)
    if not item:
        return None
    return mw.buy(state, item, sink=sink, now=now)


def _do_repair(state, sink, args, *, now, rng):
    item = " ".join(args)
    if not item:
        return None
    return mw.repair(state, item, sink=sink, now=now)


def _do_build(state, sink, args, *, now, rng):
    if not args:
        return None
    structure, level = _split_item_qty(args)
    if level is None:
        level = state.structures.get(structure.strip().lower(), 0)
    return mw.build_structure(state, structure, level, sink=sink, now=now)


def _do_skill(state, sink, args, *, now, rng):
    branch, points = _split_item_qty(args)
    if not branch:
        return None
    return mw.allocate_skill(state, branch, points if points is not None else 1, sink=sink, now=now)


#: THE single source for the action-verb surface: verb → handler. The step()
#: gate (``_ACTION_VERBS``) is derived from this table, so the gate and the
#: routing cannot drift; the help-parity test pins ``help_lines()`` to it.
_ACTIONS = {
    "mine": _do_mine,
    "harvest": _do_harvest,
    "sell": _do_sell,
    "buy": _do_buy,
    "repair": _do_repair,
    "descend": _do_descend,
    "ascend": _do_ascend,
    "build": _do_build,
    "vault": _do_vault,
    "skill": _do_skill,
}

_ACTION_VERBS = frozenset(_ACTIONS)


def _dispatch_action(
    state: mw.MiningState,
    sink: InMemorySink,
    verb: str,
    args: list[str],
    *,
    now: datetime,
    rng: random.Random | None,
):
    """Route one action verb to the seam and return its frozen Result (or None
    for a malformed command, whose message is handled by the caller)."""
    handler = _ACTIONS.get(verb)
    if handler is None:
        return None
    return handler(state, sink, args, now=now, rng=rng)


def _blocked_extra(verb: str, result, state: mw.MiningState) -> list[str]:
    """UX-only discoverability hints for a blocked action — non-balance.

    The seam already returns the honest reason as ``result.message`` (for a
    torch-less descend that is ``world.descend_hint`` itself). This adds a small
    orchestration nudge so the *player* knows what to do next, without changing
    any economy number.
    """
    if verb == "descend" and not result.ok:
        reach = world.max_accessible_depth(state.stats())
        if state.depth <= reach:  # blocked by the light gate, not the world floor
            return ["  (Your equipped light gates how deep you can go — see the hint above.)"]
    return []


def step(
    state: mw.MiningState,
    sink: InMemorySink,
    line: str,
    *,
    now: datetime,
    rng: random.Random | None = None,
) -> StepResult:
    """Run one input *line* against *state*/*sink*; return its output + flags.

    Never raises on bad input — an empty line is a no-op, an unknown command
    prints the help. State-changing verbs print the seam's Result message and,
    on success, the refreshed status header.
    """
    tokens = line.strip().split()
    if not tokens:
        return StepResult()
    verb = tokens[0].lower()
    args = tokens[1:]

    if verb in {"quit", "exit", "q"}:
        return StepResult(quit=True)
    if verb in {"status", "inv", "inventory"}:
        return StepResult(lines=status_lines(state, now=now))
    if verb in {"help", "?"}:
        return StepResult(lines=help_lines())

    if verb not in _ACTION_VERBS:
        return StepResult(lines=[f"Unknown command: {verb!r}.", *help_lines()])

    result = _dispatch_action(state, sink, verb, args, now=now, rng=rng)
    if result is None:
        return StepResult(lines=[f"Usage — see 'help' for how to use '{verb}'."])

    out = [result.message]
    out += _blocked_extra(verb, result, state)
    if result.ok:
        out += status_lines(state, now=now)
    return StepResult(lines=out, is_action=True, ok=result.ok)


# ---------------------------------------------------------------------------
# Scripted (non-interactive) driver — the testable entry point
# ---------------------------------------------------------------------------
@dataclass
class SessionResult:
    """The outcome of a scripted session (what a test asserts against)."""

    lines: list[str]
    state: mw.MiningState
    sink: InMemorySink
    ok_actions: int  # state-changing actions that committed (== len(sink.records))
    start_coins: int

    @property
    def text(self) -> str:
        """The whole session transcript as one string."""
        return "\n".join(self.lines)


def run_commands(
    commands: list[str],
    *,
    sink: InMemorySink | None = None,
    state: mw.MiningState | None = None,
    now: datetime | None = None,
    rng: random.Random | None = None,
) -> SessionResult:
    """Drive a scripted, TTY-free session and return its :class:`SessionResult`.

    Feeds each string in *commands* through :func:`step` against a shared state +
    sink. Injectable *sink* / *state* / *now* / *rng* make a run fully
    deterministic for tests. A ``quit`` (or the end of the list) closes the
    session and appends the summary.
    """
    now = now if now is not None else datetime(2026, 7, 13, 12, 0, 0, tzinfo=timezone.utc)
    if state is None:
        state = new_state(now=now)
    if sink is None:
        sink = InMemorySink()

    start_coins = state.coins
    lines: list[str] = list(status_lines(state, now=now))
    ok_actions = 0
    quit_seen = False

    for command in commands:
        res = step(state, sink, command, now=now, rng=rng)
        if res.quit:
            quit_seen = True
            break
        lines.extend(res.lines)
        if res.is_action and res.ok:
            ok_actions += 1

    lines.extend(summary_lines(state, sink, start_coins=start_coins, ok_actions=ok_actions))
    _ = quit_seen  # closing on quit vs end-of-list is intentionally the same path
    return SessionResult(
        lines=lines,
        state=state,
        sink=sink,
        ok_actions=ok_actions,
        start_coins=start_coins,
    )


# ---------------------------------------------------------------------------
# Interactive loop — thin input() wrapper over step(); handles EOF/quit cleanly
# ---------------------------------------------------------------------------
def main() -> int:
    """Run the interactive REPL. Returns a process exit code."""
    sink = InMemorySink()
    state = new_state()
    start_coins = state.coins
    ok_actions = 0

    def step_fn(line: str) -> StepResult:
        nonlocal ok_actions
        res = step(state, sink, line, now=datetime.now(timezone.utc))
        if res.is_action and res.ok:
            ok_actions += 1
        return res

    return repl(
        step_fn,
        prompt=PROMPT,
        banner_lines=[
            "⛏️  Standalone Mining — type 'help' for commands, 'quit' to leave.",
            *status_lines(state, now=datetime.now(timezone.utc)),
        ],
        closing_lines=lambda: summary_lines(
            state, sink, start_coins=start_coins, ok_actions=ok_actions
        ),
    )


__all__ = [
    "STARTER_TOOL",
    "new_state",
    "status_lines",
    "help_lines",
    "summary_lines",
    "StepResult",
    "step",
    "SessionResult",
    "run_commands",
    "main",
]
