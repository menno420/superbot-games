"""Coverage pins for ``games/mining/cli.py`` — the seams test_cli.py left dark.

The existing ``tests/mining/test_cli.py`` drives scripted sessions through
:func:`~games.mining.cli.run_commands` (economy legs, blocked actions, help /
quit ergonomics). This module pins everything that suite left uncovered:

* the status gear-line fallback branches — durability without a max cap,
  no durability entry at all — and the equipped-light suffix;
* the ``harvest`` and ``ascend`` dispatch legs;
* the malformed-command usage paths (``sell``/``buy``/``repair``/``build``/
  ``skill`` with no arguments);
* the ``build`` leg — explicit level and the default-level-from-structures
  read — including a committed build with the seam's verbatim cost paid;
* ``_dispatch_action``'s None tail for a verb outside the dispatch table;
* ``run_commands``' fresh default state when none is injected;
* the interactive ``main()`` REPL — banner + status on entry, step output
  printing, the committed-action counter, quit and EOF closing with the
  summary, exit code 0 — driven TTY-free via monkeypatched
  ``builtins.input`` + capsys (the games-hub pattern from #111).

Tests only; every asserted string/number is an EXISTING constant of the
module, the seam, or the core.
"""

from __future__ import annotations

import random
from datetime import datetime, timezone

import pytest

from games.mining import cli
from games.mining.core import equipment, structures
from services.audit import InMemorySink

FIXED_NOW = datetime(2026, 7, 13, 12, 0, 0, tzinfo=timezone.utc)


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
# Status gear line — fallback branches + the equipped-light suffix
# ---------------------------------------------------------------------------
def test_gear_line_durability_without_a_cap_shows_bare_durability() -> None:
    # An item off the core's MAX_DURABILITY table: dur is tracked, cap is None.
    state = cli.new_state(now=FIXED_NOW)
    state.equipped = {equipment.TOOL: "heirloom"}
    state.durability = {"heirloom": 5}
    assert equipment.max_durability("heirloom") is None  # really off-table
    text = "\n".join(cli.status_lines(state, now=FIXED_NOW))
    assert "gear:   heirloom (5)" in text


def test_gear_line_without_a_durability_entry_shows_just_the_tool() -> None:
    state = cli.new_state(now=FIXED_NOW)
    state.durability = {}  # equipped pickaxe, but no tracked durability
    text = "\n".join(cli.status_lines(state, now=FIXED_NOW))
    assert f"gear:   {cli.STARTER_TOOL}\n" in text + "\n"
    assert "(" not in text.split("gear:")[1].splitlines()[0]


def test_gear_line_appends_the_equipped_light_with_its_durability() -> None:
    cap = equipment.max_durability("torch")
    assert cap  # torch is on the core's durability table
    state = cli.new_state(now=FIXED_NOW)
    state.equipped[equipment.LIGHT] = "torch"
    state.durability["torch"] = cap
    text = "\n".join(cli.status_lines(state, now=FIXED_NOW))
    assert f"· light: torch ({cap}/{cap})" in text
    # Without a tracked durability the suffix is the bare light name.
    del state.durability["torch"]
    text2 = "\n".join(cli.status_lines(state, now=FIXED_NOW))
    assert "· light: torch" in text2
    assert f"({cap}/{cap})" not in text2


# ---------------------------------------------------------------------------
# Dispatch legs test_cli.py never routed — harvest, ascend, build
# ---------------------------------------------------------------------------
def test_harvest_chops_wood_and_audits_one_row() -> None:
    result = cli.run_commands(
        ["harvest", "quit"], now=FIXED_NOW, rng=random.Random(3),
        state=cli.new_state(now=FIXED_NOW),
    )
    assert "Harvested" in result.text and "wood" in result.text
    assert result.state.inventory.get("wood", 0) > 0
    assert result.ok_actions == 1 and len(result.sink.records) == 1


def test_ascend_at_the_surface_is_blocked_and_records_nothing() -> None:
    result = cli.run_commands(
        ["ascend", "quit"], now=FIXED_NOW, state=cli.new_state(now=FIXED_NOW)
    )
    assert "You are already at the Surface." in result.text
    assert result.ok_actions == 0 and len(result.sink.records) == 0


def test_build_with_an_explicit_level_quotes_the_seam_cost() -> None:
    cost = structures.build_cost("campfire", 0)
    result = cli.run_commands(
        ["build campfire 0", "quit"], now=FIXED_NOW,
        state=cli.new_state(now=FIXED_NOW),  # 0 coins — honest block
    )
    assert f"Not enough coins — Campfire costs {cost.coins}." in result.text
    assert len(result.sink.records) == 0


def test_build_default_level_is_read_from_current_structures() -> None:
    # No level given and no campfire built → the CLI supplies level 0.
    cost = structures.build_cost("campfire", 0)
    result = cli.run_commands(
        ["build campfire", "quit"], now=FIXED_NOW,
        state=cli.new_state(now=FIXED_NOW),
    )
    assert f"Not enough coins — Campfire costs {cost.coins}." in result.text


def test_funded_build_commits_at_the_seam_cost_and_audits() -> None:
    cost = structures.build_cost("campfire", 0)
    state = cli.new_state(now=FIXED_NOW)
    state.coins = cost.coins
    state.materials = dict(cost.materials)
    result = cli.run_commands(["build campfire", "quit"], now=FIXED_NOW, state=state)
    assert result.state.structures.get("campfire") == 1
    assert result.state.coins == 0
    assert result.ok_actions == 1 and len(result.sink.records) == 1


# ---------------------------------------------------------------------------
# Malformed commands — the usage line, never a crash, never an audit row
# ---------------------------------------------------------------------------
def test_argless_action_verbs_print_the_usage_line() -> None:
    sink = InMemorySink()
    state = cli.new_state(now=FIXED_NOW)
    for verb in ("sell", "buy", "repair", "build", "skill"):
        out = cli.step(state, sink, verb, now=FIXED_NOW)
        assert out.lines == [f"Usage — see 'help' for how to use '{verb}'."]
        assert not out.ok
    assert len(sink.records) == 0


def test_dispatch_action_returns_none_for_a_verb_off_the_table() -> None:
    # Unreachable via step() (which gate-checks _ACTION_VERBS) — pinned so the
    # defensive tail stays a None, not a raise.
    result = cli._dispatch_action(
        cli.new_state(now=FIXED_NOW), InMemorySink(), "dance", [],
        now=FIXED_NOW, rng=None,
    )
    assert result is None


# ---------------------------------------------------------------------------
# run_commands with no injected state — a fresh default player
# ---------------------------------------------------------------------------
def test_run_commands_defaults_to_a_fresh_player_state() -> None:
    result = cli.run_commands(["quit"], now=FIXED_NOW)
    assert result.state.coins == 0 and result.start_coins == 0
    assert result.state.equipped == {equipment.TOOL: cli.STARTER_TOOL}
    assert "Session summary:" in result.text


# ---------------------------------------------------------------------------
# main() — the interactive REPL, driven via monkeypatched builtins.input
# ---------------------------------------------------------------------------
def test_main_banner_action_quit_and_summary(monkeypatch, capsys) -> None:
    _feed_input(monkeypatch, ["harvest", "quit"])
    assert cli.main() == 0
    out = capsys.readouterr().out
    assert "Standalone Mining — type 'help' for commands, 'quit' to leave." in out
    assert "Harvested" in out and "wood" in out
    assert "actions taken:   1" in out  # the committed harvest was counted
    assert "Thanks for playing!" in out


def test_main_eof_closes_cleanly_with_the_summary(monkeypatch, capsys) -> None:
    _feed_input(monkeypatch, [])  # first input() raises EOFError (^D)
    assert cli.main() == 0
    out = capsys.readouterr().out
    assert "Session summary:" in out
    assert "actions taken:   0" in out
    assert "Thanks for playing!" in out
