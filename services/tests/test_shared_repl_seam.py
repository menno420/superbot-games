"""The shared REPL seam — loop mechanics written once, tested once.

`games/shared/cli/repl.py` owns the interactive-loop mechanics all five CLI
``main()``s adopted (hub + mining/fishing/dnd/exploration): banner, prompt
render, EOF/^C sign-off newline, quit detection, per-step line emission,
closing lines, exit code. These tests pin that contract directly against the
seam (a fake source/sink, no TTY, no monkeypatching), plus the two lazy-default
behaviours the adopting mains rely on: ``source=None`` resolves the LIVE
``builtins.input`` (so the established main()-test choreography keeps working)
and ``closing_lines`` is invoked AFTER the loop so summaries see final state.
"""

from __future__ import annotations

import builtins
from dataclasses import dataclass, field

import pytest

from games.shared.cli import repl


@dataclass
class FakeStep:
    """Minimal StepLike — what every game StepResult/HubStep provides."""

    lines: list[str] = field(default_factory=list)
    quit: bool = False


def make_source(lines):
    """A scripted source: yields *lines*, then raises EOFError (Ctrl-D)."""
    feed = list(lines)

    def source(prompt):
        if not feed:
            raise EOFError
        item = feed.pop(0)
        if item is KeyboardInterrupt:
            raise KeyboardInterrupt
        return item

    return source


def test_quit_step_ends_loop_silently_and_returns_zero():
    seen = []
    out = []

    def step_fn(line):
        seen.append(line)
        return FakeStep(quit=True) if line == "quit" else FakeStep(lines=[f"<{line}>"])

    code = repl(
        step_fn,
        prompt="p> ",
        source=make_source(["a", "quit", "never-read"]),
        sink=out.append,
    )
    assert code == 0
    assert seen == ["a", "quit"]  # nothing read past the quit step
    assert out == ["<a>"]  # the quit step emitted no lines of its own


def test_eof_close_emits_one_clean_newline_then_closing_lines():
    out = []
    code = repl(
        lambda line: FakeStep(lines=[line.upper()]),
        prompt="p> ",
        source=make_source(["hi"]),
        sink=out.append,
        closing_lines=lambda: ["bye"],
    )
    assert code == 0
    # step output, then the "" that renders the clean newline after ^D, then sign-off
    assert out == ["HI", "", "bye"]


def test_keyboard_interrupt_closes_exactly_like_eof():
    out_kbi, out_eof = [], []
    step_fn = lambda line: FakeStep(lines=[line])  # noqa: E731
    repl(step_fn, prompt="p> ", source=make_source(["x", KeyboardInterrupt]), sink=out_kbi.append)
    repl(step_fn, prompt="p> ", source=make_source(["x"]), sink=out_eof.append)
    assert out_kbi == out_eof == ["x", ""]


def test_banner_lines_emit_before_any_prompt_read():
    events = []

    def source(prompt):
        events.append(("read", prompt))
        raise EOFError

    repl(
        lambda line: FakeStep(),
        prompt="game> ",
        source=source,
        sink=lambda s: events.append(("out", s)),
        banner_lines=["welcome", "menu row"],
    )
    assert events[:2] == [("out", "welcome"), ("out", "menu row")]
    assert ("read", "game> ") in events  # the prompt string reaches the source verbatim


def test_step_lines_emit_in_order_across_steps():
    out = []
    steps = {"one": FakeStep(lines=["1a", "1b"]), "two": FakeStep(lines=["2a"])}
    repl(
        lambda line: steps[line],
        prompt="p> ",
        source=make_source(["one", "two"]),
        sink=out.append,
    )
    assert out == ["1a", "1b", "2a", ""]  # both steps' lines in order, then the EOF newline


def test_closing_lines_called_after_loop_sees_final_state():
    out = []
    count = 0

    def step_fn(line):
        nonlocal count
        count += 1
        return FakeStep(quit=(line == "quit"))

    repl(
        step_fn,
        prompt="p> ",
        source=make_source(["a", "b", "quit"]),
        sink=out.append,
        closing_lines=lambda: [f"steps={count}"],
    )
    assert out == ["steps=3"]  # closing reflects bookkeeping accumulated by step_fn


def test_closing_lines_emit_on_quit_and_on_eof_alike():
    out_quit, out_eof = [], []
    closing = lambda: ["summary"]  # noqa: E731
    repl(lambda l: FakeStep(quit=True), prompt="p> ", source=make_source(["quit"]), sink=out_quit.append, closing_lines=closing)
    repl(lambda l: FakeStep(), prompt="p> ", source=make_source([]), sink=out_eof.append, closing_lines=closing)
    assert out_quit == ["summary"]
    assert out_eof == ["", "summary"]


def test_default_source_resolves_live_builtins_input(monkeypatch, capsys):
    """The seam's ``source=None`` default must look up ``input`` at CALL time —
    the five mains are driven in tests via monkeypatched ``builtins.input``."""
    feed = ["hello", "quit"]

    def fake_input(prompt):
        assert prompt == "live> "
        if not feed:
            raise EOFError
        return feed.pop(0)

    monkeypatch.setattr(builtins, "input", fake_input)
    code = repl(
        lambda line: FakeStep(quit=(line == "quit"), lines=[f"got {line}"]),
        prompt="live> ",
    )
    assert code == 0
    assert capsys.readouterr().out == "got hello\n"  # default sink is the live print


def test_fishing_main_runs_on_the_seam(monkeypatch, capsys):
    """Adoption pin: fishing's ``main()`` is now a thin ``repl(...)`` call —
    drive it TTY-free and assert banner, cast bookkeeping, summary, exit 0."""
    from games.fishing import cli as fishing_cli

    feed = ["cast", "quit"]
    monkeypatch.setattr(builtins, "input", lambda prompt: feed.pop(0) if feed else (_ for _ in ()).throw(EOFError()))
    code = fishing_cli.main()
    out = capsys.readouterr().out
    assert code == 0
    assert out.startswith("🎣  Standalone Fishing — type 'help' for commands, 'quit' to leave.\n")
    assert "  casts made:      1" in out  # step_fn bookkeeping reached the summary
    assert out.rstrip().endswith("Tight lines — thanks for playing!")


def test_exploration_main_runs_on_the_seam(monkeypatch, capsys):
    """Adoption pin: exploration's ``main()`` on the seam — a real
    offer/accept/act flow so the ``acted`` bookkeeping branch runs, then EOF."""
    from games.exploration import cli as exploration_cli

    feed = ["offer supply_run", "accept", "act deliver_crates"]
    monkeypatch.setattr(builtins, "input", lambda prompt: feed.pop(0) if feed else (_ for _ in ()).throw(EOFError()))
    code = exploration_cli.main()
    out = capsys.readouterr().out
    assert code == 0
    assert out.startswith("🧭  Standalone Exploration")
    assert "  actions taken:    1" in out  # the acted bookkeeping reached the summary
    assert out.rstrip().endswith("May the trail be kind — thanks for playing!")


def test_empty_session_eof_immediately_still_signs_off():
    out = []
    calls = []
    code = repl(
        lambda line: calls.append(line) or FakeStep(),
        prompt="p> ",
        source=make_source([]),
        sink=out.append,
        banner_lines=["hi"],
        closing_lines=lambda: ["done"],
    )
    assert code == 0
    assert calls == []  # step_fn never invoked
    assert out == ["hi", "", "done"]
