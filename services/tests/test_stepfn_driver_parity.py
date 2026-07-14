"""Driver parity — main() and run_commands share ONE step-closure construction.

#130 unified the feed LOOPS (`repl` / `run_scripted`) but left each game
writing its per-step BOOKKEEPING CLOSURE twice: ``main()`` and
``run_commands`` (and the hub's ``run_hub``) each hand-rolled a
near-identical ``step_fn``. A drift between the twins — interactive counting
differently than scripted — was invisible to both suites, because each
driver was only ever tested against itself.

Every ``games/*/cli.py`` (and the hub ``games/__main__.py``) now builds its
closure through ONE ``make_step_fn`` factory. These tests pin two facts per
entrypoint pair:

* **adoption** — BOTH drivers construct their closure via the module's
  ``make_step_fn`` (pinned by monkeypatching the factory with a recording
  wrapper; a driver that quietly re-grew its own closure stops calling it);
* **parity** — the SAME command list through a piped ``main()`` (frozen
  module clock, seeded global rng, replayed ``builtins.input``) and through
  the scripted driver produces the pinned transcript relation:
  ``main()``'s stdout is exactly its greeting line(s) followed by the
  scripted transcript, byte for byte.

Determinism notes: the clock is frozen by swapping the cli module's
``datetime`` attribute (both drivers then stamp FIXED_NOW); mining/fishing's
``rng=None`` path falls back to seed-derived or global-``random`` streams,
so ``random.seed(...)`` immediately before EACH side makes the two streams
identical. All loops are bounded by their finite command lists.
"""

from __future__ import annotations

import random
from datetime import datetime, timezone

import pytest

from games import __main__ as hub_cli
from games.dnd import cli as dnd_cli
from games.exploration import cli as exploration_cli
from games.fishing import cli as fishing_cli
from games.mining import cli as mining_cli

FIXED_NOW = datetime(2026, 7, 13, 12, 0, 0, tzinfo=timezone.utc)
SEED = 99


class FrozenDatetime(datetime):
    """datetime whose ``now()`` is pinned to FIXED_NOW (module-injectable)."""

    @classmethod
    def now(cls, tz=None):  # noqa: D102 — test double
        if tz is not None:
            return FIXED_NOW.astimezone(tz)
        return FIXED_NOW.replace(tzinfo=None)


MINING_CMDS = ["help", "status", "mine", "mine", "harvest", "sell stone", "descend", "bogus", "quit"]
FISHING_CMDS = ["help", "status", "cast", "cast", "cast", "sell minnow", "bogus", "quit"]
DND_CMDS = ["help", "look", "1", "status", "1", "1", "2", "bogus", "quit"]
EXPLORATION_CMDS = [
    "help", "quests", "offer supply_run I", "accept", "act",
    "act deliver_crates", "act deliver_crates", "act deliver_crates",
    "status", "bogus", "quit",
]
HUB_CMDS = ["help", "list", "play bogus", "7", "quit"]  # no launch — pure hub UX

#: (cli module, command list, greeting-line count, a token the greeting must
#: carry) — the greeting is the ONLY main()-extra over the scripted banner.
GAME_CASES = [
    pytest.param(mining_cli, MINING_CMDS, 1, "Standalone Mining", id="mining"),
    pytest.param(fishing_cli, FISHING_CMDS, 1, "Standalone Fishing", id="fishing"),
    pytest.param(dnd_cli, DND_CMDS, 2, "Standalone D&D", id="dnd"),
    pytest.param(exploration_cli, EXPLORATION_CMDS, 2, "Standalone Exploration", id="exploration"),
]


def _feed_input(monkeypatch: pytest.MonkeyPatch, lines: list[str]) -> None:
    """Monkeypatch builtins.input to replay *lines*, then raise EOFError."""
    replay = iter(lines)

    def fake_input(prompt: str = "") -> str:
        try:
            return next(replay)
        except StopIteration:
            raise EOFError

    monkeypatch.setattr("builtins.input", fake_input)


def _spy_factory(monkeypatch: pytest.MonkeyPatch, module):
    """Wrap module.make_step_fn with a call recorder (delegates to the real one)."""
    real = module.make_step_fn
    calls: list[dict] = []

    def spy(*args, **kwargs):
        calls.append(kwargs)
        return real(*args, **kwargs)

    monkeypatch.setattr(module, "make_step_fn", spy)
    return calls


# ---------------------------------------------------------------------------
# Parity — main() stdout == greeting + the scripted transcript, byte for byte
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("cli, commands, greeting_count, greeting_token", GAME_CASES)
def test_main_stdout_is_greeting_plus_the_scripted_transcript(
    cli, commands, greeting_count, greeting_token, monkeypatch, capsys
):
    # Scripted side: fixed now, rng=None (the seam's seed-derived/global-random
    # fallback), global stream pinned by the seed.
    random.seed(SEED)
    scripted = cli.run_commands(commands, now=FIXED_NOW)

    # Interactive side: SAME wall-clock (frozen module datetime), SAME rng
    # stream (same seed), SAME lines via replayed input.
    monkeypatch.setattr(cli, "datetime", FrozenDatetime)
    _feed_input(monkeypatch, commands)
    random.seed(SEED)
    assert cli.main() == 0
    out = capsys.readouterr().out

    greeting = out.split("\n")[:greeting_count]
    assert greeting_token in "\n".join(greeting)
    # The load-bearing byte-for-byte relation: greeting, then the exact
    # scripted transcript.
    assert out == "\n".join([*greeting, *scripted.lines]) + "\n"


def test_hub_main_stdout_is_greeting_plus_the_scripted_transcript(monkeypatch, capsys):
    scripted = hub_cli.run_hub(HUB_CMDS)  # real registry, no launch in HUB_CMDS
    _feed_input(monkeypatch, HUB_CMDS)
    assert hub_cli.main() == 0
    out = capsys.readouterr().out
    greeting = out.split("\n")[0]
    assert "Superbot Games — the hub" in greeting
    assert out == "\n".join([greeting, *scripted.lines]) + "\n"


# ---------------------------------------------------------------------------
# Adoption — BOTH drivers build their closure via the ONE factory
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("cli, commands, greeting_count, greeting_token", GAME_CASES)
def test_both_drivers_construct_their_closure_via_make_step_fn(
    cli, commands, greeting_count, greeting_token, monkeypatch, capsys
):
    calls = _spy_factory(monkeypatch, cli)

    random.seed(SEED)
    cli.run_commands(commands, now=FIXED_NOW)
    assert len(calls) == 1
    assert calls[0].get("now") == FIXED_NOW  # scripted pins its fixed clock

    monkeypatch.setattr(cli, "datetime", FrozenDatetime)
    _feed_input(monkeypatch, commands)
    random.seed(SEED)
    assert cli.main() == 0
    capsys.readouterr()  # drain
    assert len(calls) == 2
    assert calls[1].get("now") is None  # interactive keeps the live wall clock


def test_hub_both_drivers_construct_their_closure_via_make_step_fn(monkeypatch, capsys):
    calls = _spy_factory(monkeypatch, hub_cli)
    hub_cli.run_hub(HUB_CMDS)
    assert len(calls) == 1
    assert calls[0].get("announce") is None  # scripted buffers into the transcript

    _feed_input(monkeypatch, HUB_CMDS)
    assert hub_cli.main() == 0
    capsys.readouterr()
    assert len(calls) == 2
    assert calls[1].get("announce") is print  # interactive announces immediately


# ---------------------------------------------------------------------------
# The hub factory's two announce modes — buffered vs immediate
# ---------------------------------------------------------------------------
def _fake_entries():
    from services.world_registry import WorldEntry

    return (
        WorldEntry(game_id="probe", title="Probe", blurb="a fake", opener=lambda: 0),
    )


def test_hub_factory_buffers_the_launch_banner_ahead_of_step_lines():
    entries = _fake_entries()
    step_fn, launched = hub_cli.make_step_fn(entries, launch=lambda entry: 0)
    step = step_fn("play probe")
    assert step.lines[0] == hub_cli.launching_line("probe")
    assert launched == ["probe"]


def test_hub_factory_announce_callable_emits_instead_of_buffering():
    entries = _fake_entries()
    announced: list[str] = []
    step_fn, launched = hub_cli.make_step_fn(
        entries, launch=lambda entry: 0, announce=announced.append
    )
    step = step_fn("play probe")
    assert announced == [hub_cli.launching_line("probe")]
    assert hub_cli.launching_line("probe") not in step.lines
    assert launched == ["probe"]
