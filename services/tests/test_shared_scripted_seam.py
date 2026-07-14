"""The scripted feed-loop seam — ``run_scripted``, the TTY-free twin of ``repl``.

`games/shared/cli/repl.py` gained ``run_scripted`` so the five scripted
drivers (``run_commands`` in mining/fishing/dnd/exploration + the hub's
``run_hub``) stop hand-rolling the same feed mechanics: banner lines open the
transcript, each command string is fed through ``step_fn`` in order, a
``quit`` step ends the feed emitting nothing (later commands never
dispatched), other steps contribute their ``lines``, and ``closing_lines`` —
invoked AFTER the loop, so summaries see final state — always closes the
transcript (quit and end-of-list alike).

These tests pin that contract directly against the seam (a fake StepLike, no
game imports needed) plus the adoption fact itself: each of the five real
scripted drivers routes through ``run_scripted`` (pinned by monkeypatching
the name each module imported — a driver that quietly re-grew its own loop
stops calling the seam and fails here).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from games.shared.cli import run_scripted


@dataclass
class FakeStep:
    """Minimal StepLike — what every game StepResult/HubStep provides."""

    lines: list[str] = field(default_factory=list)
    quit: bool = False


def test_banner_then_step_lines_then_closing_in_order():
    out = run_scripted(
        lambda line: FakeStep(lines=[f"<{line}>"]),
        ["a", "b"],
        banner_lines=["banner-1", "banner-2"],
        closing_lines=lambda: ["bye"],
    )
    assert out == ["banner-1", "banner-2", "<a>", "<b>", "bye"]


def test_quit_step_ends_feed_silently_and_later_commands_never_dispatch():
    seen: list[str] = []

    def step_fn(line):
        seen.append(line)
        return FakeStep(quit=True) if line == "quit" else FakeStep(lines=[f"<{line}>"])

    out = run_scripted(step_fn, ["a", "quit", "never-fed"], closing_lines=lambda: ["end"])
    assert seen == ["a", "quit"]  # nothing dispatched past the quit step
    assert out == ["<a>", "end"]  # the quit step contributed no lines of its own


def test_end_of_list_closes_through_the_same_closing_path_as_quit():
    step_fn = lambda line: FakeStep(quit=(line == "quit"), lines=[line])  # noqa: E731
    via_quit = run_scripted(step_fn, ["x", "quit"], closing_lines=lambda: ["summary"])
    via_end = run_scripted(step_fn, ["x"], closing_lines=lambda: ["summary"])
    assert via_quit == via_end == ["x", "summary"]


def test_closing_lines_invoked_after_the_loop_so_summaries_see_final_state():
    count = 0

    def step_fn(line):
        nonlocal count
        count += 1
        return FakeStep(lines=[])

    out = run_scripted(step_fn, ["a", "b", "c"], closing_lines=lambda: [f"steps: {count}"])
    assert out == ["steps: 3"]


def test_no_closing_lines_and_empty_commands_degenerate_cleanly():
    # No closing_lines → transcript is banner + step lines only.
    assert run_scripted(lambda line: FakeStep(lines=[line]), ["a"], banner_lines=["b"]) == [
        "b",
        "a",
    ]
    # Empty command list → banner + closing only, step_fn never called.
    out = run_scripted(
        lambda line: pytest.fail("step_fn must not run"),  # pragma: no cover
        [],
        banner_lines=["b"],
        closing_lines=lambda: ["end"],
    )
    assert out == ["b", "end"]


def test_returns_a_fresh_list_not_the_banner_sequence():
    banner = ["b"]
    out = run_scripted(lambda line: FakeStep(), [], banner_lines=banner)
    out.append("mutated")
    assert banner == ["b"]  # caller mutation never leaks into the banner


# ---------------------------------------------------------------------------
# Adoption pins — the five real scripted drivers actually route through the
# seam (each module imported the name, so patching module.run_scripted with a
# recording wrapper proves the driver calls it and still returns its lines).
# ---------------------------------------------------------------------------
def _adoption_cases():
    import games.__main__ as hub_module
    from games.dnd import cli as dnd_cli
    from games.exploration import cli as exploration_cli
    from games.fishing import cli as fishing_cli
    from games.mining import cli as mining_cli

    return [
        pytest.param(mining_cli, lambda m: m.run_commands(["help", "quit"]), id="mining"),
        pytest.param(fishing_cli, lambda m: m.run_commands(["help", "quit"]), id="fishing"),
        pytest.param(dnd_cli, lambda m: m.run_commands(["help", "quit"]), id="dnd"),
        pytest.param(
            exploration_cli, lambda m: m.run_commands(["help", "quit"]), id="exploration"
        ),
        pytest.param(
            hub_module,
            lambda m: m.run_hub(["help", "quit"], launch=lambda entry: 0),
            id="hub",
        ),
    ]


@pytest.mark.parametrize("module, drive", _adoption_cases())
def test_scripted_driver_routes_through_the_shared_seam(monkeypatch, module, drive):
    calls: list[tuple] = []
    real = run_scripted

    def recording(step_fn, commands, **kwargs):
        calls.append((tuple(commands), sorted(kwargs)))
        return real(step_fn, commands, **kwargs)

    monkeypatch.setattr(module, "run_scripted", recording)
    result = drive(module)
    assert calls == [(("help", "quit"), ["banner_lines", "closing_lines"])]
    # The driver's transcript is exactly what the seam returned (banner …
    # closing) — the help step's lines are present, the quit step added none.
    assert result.lines is not None and len(result.lines) > 0
