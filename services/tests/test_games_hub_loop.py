"""Coverage pins for ``games/__main__.py`` — the hub's dark seams.

The existing hub tests (``test_world_registry.py``) prove ``run_hub``'s
list/play/quit dispatch through the scripted driver with an injected fake
launcher. This module pins everything that suite left dark:

* ``_default_launch`` — the opener-return normalisation (``None`` -> 0, an
  int exit code passed through) and that ``run_hub`` falls back to it when no
  launcher is injected;
* the EMPTY-registry menu line and the ``help`` command reference;
* the invalid-input paths — out-of-range list number, blank line, bare
  ``play`` with no argument, unknown command;
* the bare-number / bare-id shortcuts (a known token without ``play``);
* the interactive ``main()`` REPL — banner + menu on entry, step output
  printing, quit and EOF closing cleanly with the sign-off, exit code 0 —
  driven TTY-free via monkeypatched ``builtins.input`` + capsys;
* the ``python -m games`` module guard, via ``runpy``;
* the launch-banner ORDER — "Launching X…" is emitted BEFORE the opener's
  synchronous game session runs (``main()`` prints it, ``run_hub`` records it
  in the transcript, ``hub_step`` no longer returns it as a post-launch line).

Tests only; every asserted string is an EXISTING constant of the module.
"""

from __future__ import annotations

import runpy

import pytest

from services import world_registry
from services.world_registry import WorldEntry

from games import __main__ as hub


@pytest.fixture(autouse=True)
def _clean_registry():
    """Every test starts and ends with an empty module-global registry."""
    world_registry.clear()
    yield
    world_registry.clear()


def _entry(game_id: str, opener=None) -> WorldEntry:
    """A minimal WorldEntry; opener defaults to a no-op returning None."""
    return WorldEntry(
        game_id=game_id,
        title=f"Title {game_id}",
        blurb=f"Blurb {game_id}",
        opener=opener if opener is not None else (lambda: None),
    )


def _feed_input(monkeypatch: pytest.MonkeyPatch, lines: list[str]) -> None:
    """Monkeypatch builtins.input to replay *lines*, then raise EOFError."""
    replay = iter(lines)

    def fake_input(prompt: str = "") -> str:
        assert prompt == hub.PROMPT  # main() always prompts with PROMPT
        try:
            return next(replay)
        except StopIteration:
            raise EOFError

    monkeypatch.setattr("builtins.input", fake_input)


# ---------------------------------------------------------------------------
# _default_launch — opener return normalised to a process-style exit code
# ---------------------------------------------------------------------------
def test_default_launch_normalises_a_none_return_to_zero() -> None:
    assert hub._default_launch(_entry("solo", opener=lambda: None)) == 0


def test_default_launch_passes_an_int_exit_code_through() -> None:
    assert hub._default_launch(_entry("solo", opener=lambda: 7)) == 7


def test_run_hub_without_a_launcher_runs_the_entrys_opener() -> None:
    # No *launch* injected: run_hub falls back to _default_launch, which
    # calls the entry's opaque opener.
    opened: list[str] = []
    world_registry.register(_entry("solo", opener=lambda: opened.append("solo")))
    result = hub.run_hub(["play solo", "quit"], registry=world_registry)
    assert opened == ["solo"]
    assert result.launched == ["solo"]


# ---------------------------------------------------------------------------
# Rendering — the empty menu and the help reference
# ---------------------------------------------------------------------------
def test_listing_lines_with_no_entries_says_none_registered() -> None:
    assert hub.listing_lines(()) == ["No games are registered."]


def test_help_command_prints_the_command_reference() -> None:
    world_registry.register(_entry("solo"))
    result = hub.run_hub(["help", "quit"], registry=world_registry, launch=lambda e: None)
    for line in hub.help_lines():
        assert line in result.lines
    assert "quit / exit          leave the hub" in result.text


# ---------------------------------------------------------------------------
# Invalid input + shortcut dispatch
# ---------------------------------------------------------------------------
def test_out_of_range_number_is_reported_as_unknown_game() -> None:
    world_registry.register(_entry("solo"))
    launched: list[str] = []
    result = hub.run_hub(
        ["play 99", "quit"], registry=world_registry, launch=lambda e: launched.append(e.game_id)
    )
    assert launched == []
    assert "Unknown game: '99'. Valid games: solo." in result.text


def test_blank_line_is_a_noop() -> None:
    world_registry.register(_entry("solo"))
    step = hub.hub_step("   ", (world_registry.get("solo"),), launch=lambda e: None)
    assert step.lines == []
    assert step.quit is False
    assert step.launched is None


def test_bare_play_without_an_argument_prints_usage() -> None:
    world_registry.register(_entry("solo"))
    launched: list[str] = []
    result = hub.run_hub(
        ["play", "quit"], registry=world_registry, launch=lambda e: launched.append(e.game_id)
    )
    assert launched == []
    assert "Usage: play <id> (or a number)." in result.text


def test_bare_number_is_a_shortcut_for_play_that_number() -> None:
    world_registry.register(_entry("solo"))
    world_registry.register(_entry("duet"))
    launched: list[str] = []
    hub.run_hub(["2", "quit"], registry=world_registry, launch=lambda e: launched.append(e.game_id))
    assert launched == ["duet"]


def test_bare_known_id_is_a_shortcut_for_play_that_id() -> None:
    world_registry.register(_entry("solo"))
    launched: list[str] = []
    hub.run_hub(
        ["solo", "quit"], registry=world_registry, launch=lambda e: launched.append(e.game_id)
    )
    assert launched == ["solo"]


def test_unknown_command_prints_the_help_reference() -> None:
    world_registry.register(_entry("solo"))
    launched: list[str] = []
    result = hub.run_hub(
        ["frobnicate", "quit"], registry=world_registry, launch=lambda e: launched.append(e.game_id)
    )
    assert launched == []
    assert "Unknown command: 'frobnicate'." in result.text
    assert "Commands:" in result.text


# ---------------------------------------------------------------------------
# main() — the interactive REPL, driven via monkeypatched builtins.input
# ---------------------------------------------------------------------------
def test_main_banner_menu_help_then_quit(monkeypatch, capsys) -> None:
    _feed_input(monkeypatch, ["help", "quit"])
    code = hub.main()
    out = capsys.readouterr().out
    assert code == 0
    assert "Superbot Games — the hub." in out
    # The wired menu and the help reference were both printed through the loop.
    assert "Available games (type 'play <id>' or a number):" in out
    assert "mining" in out and "fishing" in out
    assert "Commands:" in out
    assert out.rstrip().endswith("Thanks for playing — see you at the hub!")


def test_main_eof_closes_cleanly_with_the_sign_off(monkeypatch, capsys) -> None:
    _feed_input(monkeypatch, [])  # first input() raises EOFError (^D)
    code = hub.main()
    out = capsys.readouterr().out
    assert code == 0
    assert "Thanks for playing — see you at the hub!" in out


# ---------------------------------------------------------------------------
# Launch-banner order — "Launching X…" precedes the game session (the fix's pin)
# ---------------------------------------------------------------------------
def test_main_prints_the_launch_banner_before_the_game_session(monkeypatch, capsys) -> None:
    # END-TO-END order: the opener prints its own session output; main()'s banner
    # must land on stdout BEFORE it (regression: the banner used to trail the
    # whole game because hub_step returned it as a post-launch line).
    monkeypatch.setattr(
        hub,
        "wire_games",
        lambda registry: registry.register(
            _entry("solo", opener=lambda: print("SOLO SESSION OUTPUT"))
        ),
    )
    _feed_input(monkeypatch, ["play solo", "quit"])
    code = hub.main()
    out = capsys.readouterr().out
    assert code == 0
    assert out.index(hub.launching_line("solo")) < out.index("SOLO SESSION OUTPUT")


def test_hub_step_no_longer_returns_the_banner_as_a_post_launch_line() -> None:
    # hub_step's contract: it dispatches (launched set) but the banner is the
    # CALLER's pre-launch announcement, not a line rendered after the session.
    world_registry.register(_entry("solo"))
    step = hub.hub_step("play solo", (world_registry.get("solo"),), launch=lambda e: None)
    assert step.launched == "solo"
    assert step.lines == []


def test_run_hub_transcript_records_the_banner_on_the_fallback_launch_path() -> None:
    # The scripted driver still shows "Launching solo…" in its transcript (now
    # appended by run_hub itself before the opener runs), on both launch paths.
    opened: list[str] = []
    world_registry.register(_entry("solo", opener=lambda: opened.append("solo")))
    result = hub.run_hub(["play solo", "quit"], registry=world_registry)
    assert opened == ["solo"]
    assert hub.launching_line("solo") in result.lines


def test_run_hub_transcript_records_the_banner_with_an_injected_launcher() -> None:
    launched: list[str] = []
    world_registry.register(_entry("solo"))
    result = hub.run_hub(
        ["play solo", "quit"],
        registry=world_registry,
        launch=lambda e: launched.append(e.game_id),
    )
    assert launched == ["solo"]
    assert hub.launching_line("solo") in result.lines


@pytest.mark.filterwarnings("ignore::RuntimeWarning")  # runpy re-executes an already-imported module
def test_python_dash_m_games_exits_zero(monkeypatch, capsys) -> None:
    # The `python -m games` entry guard: runpy executes the module as
    # __main__, whose sys.exit(main()) must surface exit code 0 on EOF.
    monkeypatch.setattr("builtins.input", lambda prompt="": (_ for _ in ()).throw(EOFError()))
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_module("games", run_name="__main__", alter_sys=True)
    assert excinfo.value.code == 0
    assert "Thanks for playing — see you at the hub!" in capsys.readouterr().out
