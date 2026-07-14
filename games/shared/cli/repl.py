"""The ONE interactive REPL loop shared by every game CLI ``main()``.

Before this seam existed, five entrypoints — ``games/{mining,fishing,dnd,
exploration}/cli.py`` and the hub ``games/__main__.py`` — each hand-rolled the
same ``while True: input(PROMPT)`` mechanics: print a banner, read a line,
close cleanly on EOF (Ctrl-D) or KeyboardInterrupt (Ctrl-C) with a bare
newline, stop on a quit step, print the step's output lines, and finish with a
sign-off (a session summary or a thanks line) before returning exit code 0.
That loop was written five times and could only be tested five times (each
``main()`` needed its own ``builtins.input`` monkeypatch choreography).

:func:`repl` is that loop written ONCE. Everything game-specific stays with
the game and arrives as parameters:

* ``step_fn`` — one input line in, a :class:`StepLike` out. The game closes
  over its own state/sink/bookkeeping (action counters, scenes visited, …)
  inside this callable; the loop only reads ``.quit`` and ``.lines``. Every
  game's existing ``StepResult`` (and the hub's ``HubStep``) already conforms.
* ``banner_lines`` — the greeting + opening header, emitted before the loop.
* ``closing_lines`` — a CALLABLE returning the sign-off lines, invoked after
  the loop ends (quit, EOF, or ^C alike) so a summary reflects final state.
* ``prompt`` / ``source`` / ``sink`` — where lines come from and go to.
  Defaults are resolved LAZILY to the live ``input`` / ``print`` builtins so
  the established test choreography (monkeypatching ``builtins.input``,
  capturing stdout) keeps working unchanged.

Behavior contract (byte-identity with the five hand-rolled loops, pinned by
before/after transcript SHA-256s on the adopting PR): EOF and
KeyboardInterrupt from ``source`` emit one empty line (the clean newline after
^D / ^C) and end the loop; a step with ``quit=True`` ends the loop emitting
nothing; every other step has its ``lines`` emitted in order; the closing
lines always print; the return value is always exit code ``0``.
"""

from __future__ import annotations

from typing import Callable, Iterable, Protocol, Sequence

__all__ = ["StepLike", "repl"]


class StepLike(Protocol):
    """What the loop needs from one dispatched step — quit flag + output lines.

    Structural: every game's ``StepResult`` dataclass and the hub's
    ``HubStep`` already satisfy it without importing this module.
    """

    quit: bool
    lines: list[str]


def repl(
    step_fn: Callable[[str], StepLike],
    *,
    prompt: str,
    source: Callable[[str], str] | None = None,
    sink: Callable[[str], object] | None = None,
    banner_lines: Sequence[str] = (),
    closing_lines: Callable[[], Iterable[str]] | None = None,
) -> int:
    """Run the interactive loop; return the process exit code (always ``0``).

    *source* is called with *prompt* for each line (default: the live
    ``input`` builtin, resolved at call time so monkeypatched tests work);
    *sink* receives every output line (default: the live ``print``). EOF /
    KeyboardInterrupt from *source* close the session with a clean newline;
    a ``step_fn`` result with ``quit=True`` closes it silently. Bounded by
    its input: the loop ends when *source* signals EOF or a step quits.
    """
    read = source if source is not None else (lambda p: input(p))
    emit = sink if sink is not None else (lambda line: print(line))

    for line in banner_lines:
        emit(line)

    while True:
        try:
            raw = read(prompt)
        except (EOFError, KeyboardInterrupt):
            emit("")  # clean newline after ^D / ^C
            break
        step = step_fn(raw)
        if step.quit:
            break
        for out in step.lines:
            emit(out)

    if closing_lines is not None:
        for out in closing_lines():
            emit(out)
    return 0
