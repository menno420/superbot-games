"""Standalone D&D CLI — a playable text session over the audited resolver seam.

This is the *player loop* the D&D walking skeleton was missing: rung 1 shipped the
pure core (``games/dnd/core/`` — the bounded-menu ``resolve``, the pre-priced
``EFFECTS`` registry, the ``models`` schema) plus its 3-scene data catalog
(``games/dnd/data/scenes.py``), and this session adds the audited WORKFLOW seam
(``services/dnd_workflow.py``, the single :func:`~services.dnd_workflow.choose`
action) — but nothing actually *drove* the seam. This module is that driver: a
text REPL that holds one mutable :class:`~services.dnd_workflow.DnDState`, an
in-memory :class:`~services.audit.InMemorySink`, and dispatches player commands to
the one seam action (``choose``) plus the read-only navigation verbs (``look`` /
``status``).

The HUMAN occupies the AI Dungeon Master's EXACT seat: the loop shows the current
scene's prose + its bounded numbered menu, and a number or an option id picks ONE
option — nothing more. There is NO generative narration and NO model anywhere in
the loop: every player-visible string is read VERBATIM from ``data/scenes.py`` via
the seam, and every reward number is the engine's tier-capped bundle (this module
invents no balance number). Its only additions are UX / orchestration — a status
header, a clear help screen, an off-menu hint (the resolver clamps to the safe
default), and an end-of-session summary (scenes visited, total reward, audit rows).

Testability: the loop is factored so a test can drive a scripted session with no
TTY — :func:`run_commands` takes a list of command strings (plus an optional
injected sink / state / clock / id factory) and returns a :class:`SessionResult`.
The ``__main__`` module wraps an ``input()`` loop around the same :func:`step`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from services import dnd_workflow as dw
from services.audit import InMemorySink

from games.dnd.data.scenes import get_scene, text_for
from games.shared.cli import repl, run_scripted

PROMPT = "dnd> "

#: The command words that are NOT a story choice (everything else on the prompt
#: is dispatched to the seam as the DM's one-id pick).
_QUIT_VERBS = frozenset({"quit", "exit", "q"})
_LOOK_VERBS = frozenset({"look", "l"})
_STATUS_VERBS = frozenset({"status", "state"})
_HELP_VERBS = frozenset({"help", "?"})
_RESERVED = _QUIT_VERBS | _LOOK_VERBS | _STATUS_VERBS | _HELP_VERBS


# ---------------------------------------------------------------------------
# Fresh-player state — the walking-skeleton start scene, no invented numbers
# ---------------------------------------------------------------------------
def new_state() -> dw.DnDState:
    """A fresh D&D session at the skeleton's start scene (``waystation_road``).

    Every field is a core default — the start scene id, a zero seed, empty reward
    totals. Nothing here is a new balance number.
    """
    return dw.DnDState()


# ---------------------------------------------------------------------------
# Rendering — pure string builders (no printing), so tests can assert on them
# ---------------------------------------------------------------------------
def scene_lines(state: dw.DnDState) -> list[str]:
    """The current scene's prose + its bounded numbered menu (the DM's seat).

    The menu shown is exactly the width-capped set the resolver ACCEPTS
    (:func:`services.dnd_workflow.surfaced_options`), so a numbered pick always
    lands on a real, in-bounds option; anything else clamps to the safe default.
    All copy is read VERBATIM from ``data/scenes.py``.
    """
    scene = get_scene(state.scene_id)
    options = dw.surfaced_options(scene, xp=state.xp)
    lines = ["", text_for(scene.context_key), ""]
    for idx, opt in enumerate(options, start=1):
        lines.append(f"  {idx}. {text_for(opt.text_key)}")
    lines.append("  (Type a number or an option name; anything off-menu keeps you safe.)")
    return lines


def status_lines(state: dw.DnDState, sink: InMemorySink) -> list[str]:
    """The status header: current scene, accumulated reward totals, audit rows."""
    scene = get_scene(state.scene_id)
    reward = f"xp {state.global_xp} · game-xp {state.game_xp} · coins {state.currency}"
    if state.capability is not None:
        reward += f" · capability {state.capability}"
    return [
        "─" * 44,
        f"  scene:    {state.scene_id}",
        f"  here:     {text_for(scene.context_key)}",
        f"  reward:   {reward}",
        f"  audited:  {len(sink.records)} record(s)",
        "─" * 44,
    ]


def help_lines() -> list[str]:
    """The command reference printed by ``help`` (and on an unknown command)."""
    return [
        "Commands:",
        "  <number>             pick a menu option by its number (the DM's seat)",
        "  <option name>        pick a menu option by its id (e.g. advance_escort)",
        "  look                 re-read the current scene and its menu",
        "  status               show the scene, your reward totals, and audit rows",
        "  help                 show this list",
        "  quit / exit          end the session (prints a summary)",
        "",
        "You occupy the Dungeon Master's seat: pick ONE option from the bounded",
        "menu. Anything off-menu safely clamps to the scene's default (no harm).",
    ]


def summary_lines(
    state: dw.DnDState,
    sink: InMemorySink,
    *,
    scenes_visited: list[str],
    choices_made: int,
) -> list[str]:
    """The friendly end-of-session recap printed on quit."""
    reward = f"xp {state.global_xp} · game-xp {state.game_xp} · coins {state.currency}"
    if state.capability is not None:
        reward += f" · capability {state.capability}"
    lines = [
        "─" * 44,
        "Session summary:",
        f"  choices made:    {choices_made}",
        f"  scenes visited:  {len(scenes_visited)} ({', '.join(scenes_visited)})",
        f"  total reward:    {reward}",
        f"  audit records:   {len(sink.records)}",
        "May your escort reach the waystation — thanks for playing!",
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
    is_choice: bool = False  # routed to the state-changing ``choose`` seam verb
    ended: bool = False  # the chosen option concluded the beat (no successor scene)


def _resolve_choice_id(state: dw.DnDState, token: str) -> str:
    """Map a menu number to a surfaced option id; pass any other token through.

    A digit within the surfaced range resolves to that option's id; a digit out
    of range or any non-digit token is passed to the seam VERBATIM — the resolver
    then clamps it (off-menu) to the scene's deterministic safe default. The CLI
    never re-implements that clamp.
    """
    scene = get_scene(state.scene_id)
    options = dw.surfaced_options(scene, xp=state.xp)
    if token.isdigit():
        idx = int(token)
        if 1 <= idx <= len(options):
            return options[idx - 1].id
    return token


def step(
    state: dw.DnDState,
    sink: InMemorySink,
    line: str,
    *,
    story_over: bool = False,
    now: datetime | None = None,
) -> StepResult:
    """Run one input *line* against *state*/*sink*; return its output + flags.

    Never raises on bad input — an empty line is a no-op, ``look`` / ``status`` /
    ``help`` are read-only, and any other token is the DM's pick dispatched to the
    seam's :func:`~services.dnd_workflow.choose`. An off-menu pick is clamped by
    the resolver to the safe default and surfaced with a friendly hint. Once the
    story beat has concluded (*story_over*), a further pick is gently refused
    rather than re-resolved (so a terminal beat is not farmed).
    """
    tokens = line.strip().split()
    if not tokens:
        return StepResult()
    verb = tokens[0].lower()

    if verb in _QUIT_VERBS:
        return StepResult(quit=True)
    if verb in _STATUS_VERBS:
        return StepResult(lines=status_lines(state, sink))
    if verb in _LOOK_VERBS:
        return StepResult(lines=scene_lines(state))
    if verb in _HELP_VERBS:
        return StepResult(lines=help_lines())

    # Anything else is a story choice (the DM's one-id pick).
    if story_over:
        return StepResult(
            lines=[
                "The story beat has concluded — type 'quit' for your summary,",
                "or 'look' to re-read the final scene.",
            ]
        )

    option_id = _resolve_choice_id(state, tokens[0])
    result = dw.choose(state, option_id, sink=sink, now=now)

    out: list[str] = []
    if result.resolution.clamped:
        out.append(
            f"(off-menu — your guide holds to the safe path: {result.message})"
        )
    else:
        out.append(f"» {result.message}")
    if result.reward is not None:
        r = result.reward
        out.append(
            f"  reward: xp {r.global_xp} · game-xp {r.game_xp} · coins {r.currency}"
        )
    if result.ended:
        out.append("🏁 The beat concludes here.")
    else:
        out.extend(scene_lines(state))
    return StepResult(lines=out, is_choice=True, ended=result.ended)


# ---------------------------------------------------------------------------
# Scripted (non-interactive) driver — the testable entry point
# ---------------------------------------------------------------------------
@dataclass
class SessionResult:
    """The outcome of a scripted session (what a test asserts against)."""

    lines: list[str]
    state: dw.DnDState
    sink: InMemorySink
    choices_made: int  # ``choose`` picks routed to the seam
    scenes_visited: list[str]  # distinct scenes entered, in first-seen order

    @property
    def text(self) -> str:
        """The whole session transcript as one string."""
        return "\n".join(self.lines)


def run_commands(
    commands: list[str],
    *,
    sink: InMemorySink | None = None,
    state: dw.DnDState | None = None,
    now: datetime | None = None,
) -> SessionResult:
    """Drive a scripted, TTY-free session and return its :class:`SessionResult`.

    Feeds each string in *commands* through :func:`step` against a shared state +
    sink. Injectable *sink* / *state* / *now* make a run fully deterministic for
    tests. A ``quit`` (or the end of the list) closes the session and appends the
    summary. ``choices_made`` counts every ``choose`` pick the player issued;
    ``scenes_visited`` records the distinct scenes entered in order.
    """
    now = now if now is not None else datetime(2026, 7, 13, 12, 0, 0, tzinfo=timezone.utc)
    if state is None:
        state = new_state()
    if sink is None:
        sink = InMemorySink()

    scenes_visited: list[str] = [state.scene_id]
    choices_made = 0
    story_over = False

    def step_fn(line: str) -> StepResult:
        nonlocal choices_made, story_over
        res = step(state, sink, line, story_over=story_over, now=now)
        if res.is_choice:
            choices_made += 1
            if state.scene_id not in scenes_visited:
                scenes_visited.append(state.scene_id)
            if res.ended:
                story_over = True
        return res

    lines = run_scripted(
        step_fn,
        commands,
        banner_lines=scene_lines(state),
        closing_lines=lambda: summary_lines(
            state, sink, scenes_visited=scenes_visited, choices_made=choices_made
        ),
    )
    return SessionResult(
        lines=lines,
        state=state,
        sink=sink,
        choices_made=choices_made,
        scenes_visited=scenes_visited,
    )


# ---------------------------------------------------------------------------
# Interactive loop — thin input() wrapper over step(); handles EOF/quit cleanly
# ---------------------------------------------------------------------------
def main() -> int:
    """Run the interactive REPL. Returns a process exit code."""
    sink = InMemorySink()
    state = new_state()
    scenes_visited: list[str] = [state.scene_id]
    choices_made = 0
    story_over = False

    def step_fn(line: str) -> StepResult:
        nonlocal choices_made, story_over
        res = step(state, sink, line, story_over=story_over, now=datetime.now(timezone.utc))
        if res.is_choice:
            choices_made += 1
            if state.scene_id not in scenes_visited:
                scenes_visited.append(state.scene_id)
            if res.ended:
                story_over = True
        return res

    return repl(
        step_fn,
        prompt=PROMPT,
        banner_lines=[
            "🐉  Standalone D&D — you are the Dungeon Master's seat.",
            "    Type 'help' for commands, 'quit' to leave.",
            *scene_lines(state),
        ],
        closing_lines=lambda: summary_lines(
            state, sink, scenes_visited=scenes_visited, choices_made=choices_made
        ),
    )


__all__ = [
    "PROMPT",
    "new_state",
    "scene_lines",
    "status_lines",
    "help_lines",
    "summary_lines",
    "StepResult",
    "step",
    "SessionResult",
    "run_commands",
    "main",
]
