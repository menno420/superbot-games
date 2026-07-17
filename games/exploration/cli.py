"""Standalone Exploration CLI — a playable session over the audited quest seam.

This is the *player loop* the exploration game was missing: three green islands
shipped independently — the deterministic quest engine
(``games/exploration/quest/``), the survival energy axis
(``games/exploration/survival/``), and the shared encounter resolver
(``games/shared/encounter/``) — but nothing DROVE them together. The audited
WORKFLOW seam (``services/exploration_workflow.py``) wired them into one
lifecycle; this module is the text REPL that drives that seam.

The HUMAN occupies the quest-picker's seat — nothing generative. The loop shows
the bounded ``catalog.menu()`` (``quests``), lets the human ``offer`` a
``(template, tier)`` and ``accept`` it, then ``act <bounded-action>`` to advance
an objective (each action maps 1:1 to an objective-advancing ``GameEvent`` and
rolls a deterministic encounter), banking the tier-capped reward automatically
when a quest completes. There is NO AI-DM, NO generative narration, and NO model
anywhere in the loop: every string is either the seam's echoed outcome or catalog
copy read VERBATIM, and every reward number is the engine's tier-capped bundle
(this module invents no balance number). Read-only ``status`` / ``help`` verbs, a
graceful off-menu path (the seam surfaces the valid menu — never a silent clamp),
and an end-of-session summary (quests completed, rewards banked, audit rows) round
it out.

Testability: the loop is factored so a test can drive a scripted session with no
TTY — :func:`run_commands` takes a list of command strings (plus an optional
injected sink / state / clock / id factory) and returns a :class:`SessionResult`.
The ``__main__`` module wraps an ``input()`` loop around the same :func:`step`.
Mirrors ``games/dnd/cli.py`` structure/voice.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable

from services import exploration_workflow as ew
from services.audit import InMemorySink

from games.exploration.quest import catalog
from games.exploration.quest.models import RewardTier
from games.shared.cli import repl, run_scripted

PROMPT = "explore> "

#: The command words dispatched by :func:`step` (everything else is unknown input).
_QUIT_VERBS = frozenset({"quit", "exit", "q"})
_QUESTS_VERBS = frozenset({"quests", "menu"})
_STATUS_VERBS = frozenset({"status", "state"})
_HELP_VERBS = frozenset({"help", "?"})

#: Accepted reward-tier tokens for ``offer <template> [tier]`` (VERBATIM from the
#: engine's ``RewardTier`` enum values). Defaults to tier I when omitted.
_TIERS: dict[str, RewardTier] = {t.value: t for t in RewardTier}


# ---------------------------------------------------------------------------
# Fresh-player state — the survival Easy floor, no invented numbers
# ---------------------------------------------------------------------------
def new_state() -> ew.ExplorationState:
    """A fresh exploration session (Easy difficulty, full survival energy bar).

    Every field is a seam/engine default — a zero world seed, the ``"player"`` id,
    ``Difficulty.EASY`` and its shipped energy cap. Nothing here is a new balance
    number.
    """
    return ew.ExplorationState()


# ---------------------------------------------------------------------------
# Rendering — pure string builders (no printing), so tests can assert on them
# ---------------------------------------------------------------------------
def quests_lines() -> list[str]:
    """The bounded quest menu — one ``id · title · kind · summary`` row per template.

    The ids are ``catalog.menu()`` VERBATIM (the fixed 5-template list the human
    picks from); the title / kind / summary are the template's own copy. No text
    is generated.
    """
    lines = ["", "Quests you can take (offer <id> [tier], tiers I/II/III):"]
    for idx, template_id in enumerate(catalog.menu(), start=1):
        t = catalog.get(template_id)
        lines.append(f"  {idx}. {template_id:<16} {t.title} ({t.kind.value}) — {t.summary}")
    lines.append("")
    return lines


def status_lines(state: ew.ExplorationState, sink: InMemorySink) -> list[str]:
    """The status header: active quest + objective progress + energy + rewards."""
    quest = state.quest
    ledger = state.ledger
    lines = [
        "─" * 52,
        f"  difficulty:  {state.difficulty.value}   energy: {state.energy}/{state.tunables.max_energy}",
    ]
    if quest is None:
        lines.append("  quest:       (none — 'quests' to see the menu, 'offer <id>' to take one)")
    else:
        lines.append(f"  quest:       {quest.template_id} ({quest.kind.value}, tier {quest.tier.value}) — {quest.state.value}")
        for prog in quest.progress:
            mark = "✓" if prog.done else "•"
            lines.append(f"     {mark} {prog.key}: {prog.current}/{prog.required}")
        actions = ew.pending_actions(quest)
        if actions:
            lines.append(f"  actions:     {', '.join(actions)}   (act <name>)")
    reward = f"xp {ledger.global_xp} · game-xp {ledger.game_xp} · coins {ledger.currency}"
    if ledger.capabilities:
        reward += f" · caps {', '.join(ledger.capabilities)}"
    lines.append(f"  banked:      {ledger.quests_completed} quest(s) — {reward}")
    lines.append(f"  audited:     {len(sink.records)} record(s)")
    lines.append("─" * 52)
    return lines


def help_lines() -> list[str]:
    """The command reference printed by ``help`` (and on an unknown command)."""
    return [
        "Commands:",
        "  quests               show the bounded quest menu (catalog.menu())",
        "  offer <id> [tier]    offer a quest by id (tier I/II/III, default I)",
        "  accept               accept the offered quest (it becomes active)",
        "  act <action>         take a bounded action to advance an objective",
        "  status               show the active quest, energy, and banked rewards",
        "  help                 show this list",
        "  quit / exit          end the session (prints a summary)",
        "",
        "You pick from the bounded menu — a quest from the fixed catalog, then a",
        "bounded action from the active quest's own objectives. There is no AI DM",
        "and nothing generative; each action rolls a deterministic encounter and",
        "advances the objective it names. A completed quest banks its reward",
        "automatically.",
    ]


def summary_lines(
    state: ew.ExplorationState,
    sink: InMemorySink,
    *,
    actions_taken: int,
) -> list[str]:
    """The friendly end-of-session recap printed on quit."""
    ledger = state.ledger
    reward = f"xp {ledger.global_xp} · game-xp {ledger.game_xp} · coins {ledger.currency}"
    if ledger.capabilities:
        reward += f" · caps {', '.join(ledger.capabilities)}"
    return [
        "─" * 52,
        "Session summary:",
        f"  quests completed: {ledger.quests_completed}",
        f"  actions taken:    {actions_taken}",
        f"  rewards banked:   {reward}",
        f"  audit records:    {len(sink.records)}",
        "May the trail be kind — thanks for playing!",
    ]


# ---------------------------------------------------------------------------
# One command → seam dispatch
# ---------------------------------------------------------------------------
@dataclass
class StepResult:
    """What running one input line produced."""

    lines: list[str] = field(default_factory=list)
    quit: bool = False
    acted: bool = False  # a bounded action (``act``) was routed to the seam
    completed: bool = False  # the action just completed (and banked) a quest


def _offer_and_echo(
    state: ew.ExplorationState,
    sink: InMemorySink,
    args: list[str],
    *,
    now: datetime | None,
) -> list[str]:
    """Handle ``offer <id> [tier]``: parse the bounded args, call the seam, echo."""
    if not args:
        return ["Usage: offer <id> [tier]  (see 'quests').", *quests_lines()]
    # Lower-case the quest id at the boundary (mirroring the mining/fishing CLIs'
    # ``args[0].lower()`` convention, PR #158): ``catalog.menu()`` ids are all
    # lowercase, so a capitalised ``offer Supply_Run`` a player naturally types
    # must resolve the same as ``offer supply_run`` — this only ever normalises
    # case, never meaning, and the audited quest seam is untouched.
    template_id = args[0].lower()
    tier = RewardTier.I
    if len(args) > 1:
        token = args[1].upper()
        if token not in _TIERS:
            return [f"Unknown tier {args[1]!r} — pick one of I / II / III."]
        tier = _TIERS[token]
    res = ew.offer(state, template_id, tier, sink=sink, now=now)
    if not res.ok:
        return [res.message, *quests_lines()]
    return [f"» {res.message}", "Type 'accept' to take it on."]


def step(
    state: ew.ExplorationState,
    sink: InMemorySink,
    line: str,
    *,
    now: datetime | None = None,
) -> StepResult:
    """Run one input *line* against *state*/*sink*; return its output + flags.

    Never raises on bad input — an empty line is a no-op; ``quests`` / ``status``
    / ``help`` are read-only; ``offer`` / ``accept`` / ``act`` dispatch to the
    seam. An off-menu quest id, an action off the bounded menu, or a too-tired
    action is surfaced gracefully by the seam (the valid menu is echoed) and
    records nothing. When an ``act`` completes a quest, its reward is banked
    automatically via the seam's :func:`~services.exploration_workflow.grant_rewards`.
    """
    tokens = line.strip().split()
    if not tokens:
        return StepResult()
    verb = tokens[0].lower()
    args = tokens[1:]

    if verb in _QUIT_VERBS:
        return StepResult(quit=True)
    if verb in _QUESTS_VERBS:
        return StepResult(lines=quests_lines())
    if verb in _STATUS_VERBS:
        return StepResult(lines=status_lines(state, sink))
    if verb in _HELP_VERBS:
        return StepResult(lines=help_lines())

    handler = _ACTIONS.get(verb)
    if handler is not None:
        return handler(state, sink, args, now=now)

    # Anything else is unknown input — surface the help, change nothing.
    return StepResult(lines=[f"Unknown command: {verb!r}.", *help_lines()])


def _do_offer(
    state: ew.ExplorationState,
    sink: InMemorySink,
    args: list[str],
    *,
    now: datetime | None,
) -> StepResult:
    return StepResult(lines=_offer_and_echo(state, sink, args, now=now))


def _do_accept(
    state: ew.ExplorationState,
    sink: InMemorySink,
    args: list[str],
    *,
    now: datetime | None,
) -> StepResult:
    res = ew.accept(state, sink=sink, now=now)
    return StepResult(lines=[f"» {res.message}" if res.ok else res.message])


def _do_act(
    state: ew.ExplorationState,
    sink: InMemorySink,
    args: list[str],
    *,
    now: datetime | None,
) -> StepResult:
    if not args:
        valid = ", ".join(ew.pending_actions(state.quest)) or "(none — accept a quest first)"
        return StepResult(lines=[f"Usage: act <action>. Valid now: {valid}."])
    # Lower-case the action token at the boundary (same #158 convention as
    # ``offer`` above): objective-action names are lowercase, so ``act Deliver_Crates``
    # must advance the objective exactly as ``act deliver_crates`` — normalises
    # case only, seam untouched.
    res = ew.apply_action(state, args[0].lower(), sink=sink, now=now)
    if not res.ok:
        return StepResult(lines=[res.message])
    out = [f"» {res.message}"]
    completed = res.completed
    if completed:
        grant = ew.grant_rewards(state, sink=sink, now=now)
        if grant.ok:
            out.append(f"  🏁 {grant.message}")
    return StepResult(lines=out, acted=True, completed=completed)


#: THE single source for the seam-action verb surface: verb → handler. The
#: step() route is this table's ``.get`` (so the gate and the routing cannot
#: drift), and the help-parity test pins ``help_lines()`` to it.
_ACTIONS = {
    "offer": _do_offer,
    "accept": _do_accept,
    "act": _do_act,
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

    actions_taken: int = 0  # bounded ``act`` picks routed to the seam
    quests_completed: int = 0  # quests completed + banked this session


def make_step_fn(
    state: ew.ExplorationState,
    sink: InMemorySink,
    *,
    now: datetime | None = None,
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
        res = step(state, sink, line, now=at)
        if res.acted:
            tally.actions_taken += 1
        if res.completed:
            tally.quests_completed += 1
        return res

    return step_fn, tally


# ---------------------------------------------------------------------------
# Scripted (non-interactive) driver — the testable entry point
# ---------------------------------------------------------------------------
@dataclass
class SessionResult:
    """The outcome of a scripted session (what a test asserts against)."""

    lines: list[str]
    state: ew.ExplorationState
    sink: InMemorySink
    actions_taken: int  # bounded ``act`` picks routed to the seam
    quests_completed: int  # quests that completed + banked this session

    @property
    def text(self) -> str:
        """The whole session transcript as one string."""
        return "\n".join(self.lines)


def run_commands(
    commands: list[str],
    *,
    sink: InMemorySink | None = None,
    state: ew.ExplorationState | None = None,
    now: datetime | None = None,
) -> SessionResult:
    """Drive a scripted, TTY-free session and return its :class:`SessionResult`.

    Feeds each string in *commands* through :func:`step` against a shared state +
    sink. Injectable *sink* / *state* / *now* make a run fully deterministic for
    tests. A ``quit`` (or the end of the list) closes the session and appends the
    summary. ``actions_taken`` counts every bounded ``act`` the player issued;
    ``quests_completed`` counts quests banked this session.
    """
    now = now if now is not None else datetime(2026, 7, 13, 12, 0, 0, tzinfo=timezone.utc)
    if state is None:
        state = new_state()
    if sink is None:
        sink = InMemorySink()

    step_fn, tally = make_step_fn(state, sink, now=now)

    lines = run_scripted(
        step_fn,
        commands,
        banner_lines=quests_lines(),
        closing_lines=lambda: summary_lines(
            state, sink, actions_taken=tally.actions_taken
        ),
    )
    return SessionResult(
        lines=lines,
        state=state,
        sink=sink,
        actions_taken=tally.actions_taken,
        quests_completed=tally.quests_completed,
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
            "🧭  Standalone Exploration — take a bounded quest, resolve encounters, survive.",
            "    Type 'help' for commands, 'quests' for the menu, 'quit' to leave.",
            *quests_lines(),
        ],
        closing_lines=lambda: summary_lines(
            state, sink, actions_taken=tally.actions_taken
        ),
    )


__all__ = [
    "PROMPT",
    "new_state",
    "quests_lines",
    "status_lines",
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
