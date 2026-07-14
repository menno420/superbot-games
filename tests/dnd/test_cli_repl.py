"""Coverage pins for ``games/dnd/cli.py`` — the seams test_cli.py left dark.

The existing ``tests/dnd/test_cli.py`` drives scripted sessions through
:func:`~games.dnd.cli.run_commands` (the arc, the off-menu clamp, the
read-only verbs, the quit summary). This module pins what that suite left
uncovered:

* the capability suffix in the status and summary reward lines;
* the ``help`` verb dispatch inside :func:`~games.dnd.cli.step`;
* ``run_commands``' fresh default state when none is injected;
* the interactive ``main()`` REPL — banner + opening scene, choice output
  printing, the choices/scenes counters, the concluded-beat refusal, quit
  and EOF closing with the summary, exit code 0 — driven TTY-free via
  monkeypatched ``builtins.input`` + capsys (the #111/#113 pattern).

Tests only; every asserted string is an EXISTING constant of the module,
the seam, or the scene catalog.
"""

from __future__ import annotations

import pytest

from games.dnd import cli
from services.audit import InMemorySink


def _feed_input(monkeypatch: pytest.MonkeyPatch, lines: list[str]) -> None:
    """Monkeypatch builtins.input to replay *lines*, then raise EOFError."""
    replay = iter(lines)

    def fake_input(prompt: str = "") -> str:
        assert prompt == cli.PROMPT  # main() always prompts with PROMPT
        try:
            return next(replay)
        except StopIteration:
            raise EOFError

    monkeypatch.setattr("builtins.input", fake_input)


# ---------------------------------------------------------------------------
# The capability suffix — status + summary reward lines
# ---------------------------------------------------------------------------
def test_status_reward_line_appends_a_granted_capability() -> None:
    state = cli.new_state()
    state.capability = "waystation_map"
    text = "\n".join(cli.status_lines(state, InMemorySink()))
    assert "· capability waystation_map" in text
    # And the suffix is absent while no capability has been granted.
    fresh = "\n".join(cli.status_lines(cli.new_state(), InMemorySink()))
    assert "capability" not in fresh


def test_summary_reward_line_appends_a_granted_capability() -> None:
    state = cli.new_state()
    state.capability = "waystation_map"
    text = "\n".join(
        cli.summary_lines(
            state, InMemorySink(), scenes_visited=[state.scene_id], choices_made=0
        )
    )
    assert "· capability waystation_map" in text


# ---------------------------------------------------------------------------
# The help verb — dispatched inside step(), same copy as help_lines()
# ---------------------------------------------------------------------------
def test_help_verb_prints_the_command_reference() -> None:
    sink = InMemorySink()
    state = cli.new_state()
    for verb in ("help", "?"):
        out = cli.step(state, sink, verb)
        assert out.lines == cli.help_lines()
        assert not out.is_choice and not out.quit
    assert len(sink.records) == 0  # read-only: nothing audited


# ---------------------------------------------------------------------------
# run_commands with no injected state — a fresh default player
# ---------------------------------------------------------------------------
def test_run_commands_defaults_to_a_fresh_state_at_the_start_scene() -> None:
    result = cli.run_commands(["quit"])
    assert result.state.scene_id == cli.new_state().scene_id
    assert result.scenes_visited == [result.state.scene_id]
    assert result.choices_made == 0
    assert "Session summary:" in result.text


# ---------------------------------------------------------------------------
# main() — the interactive REPL, driven via monkeypatched builtins.input
# ---------------------------------------------------------------------------
def test_main_full_arc_counts_choices_and_refuses_after_the_end(monkeypatch, capsys) -> None:
    # Two picks conclude the walking-skeleton beat; a third is gently refused.
    _feed_input(monkeypatch, ["1", "1", "1", "quit"])
    assert cli.main() == 0
    out = capsys.readouterr().out
    assert "Standalone D&D — you are the Dungeon Master's seat." in out
    assert "🏁 The beat concludes here." in out
    assert "The story beat has concluded — type 'quit' for your summary," in out
    assert "choices made:    2" in out  # the refused pick never reaches the seam
    assert "May your escort reach the waystation — thanks for playing!" in out


def test_main_eof_closes_cleanly_with_the_summary(monkeypatch, capsys) -> None:
    _feed_input(monkeypatch, [])  # first input() raises EOFError (^D)
    assert cli.main() == 0
    out = capsys.readouterr().out
    assert "choices made:    0" in out
    assert "scenes visited:  1" in out
    assert "May your escort reach the waystation — thanks for playing!" in out
