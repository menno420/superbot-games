"""Tests for the neutral world registry + the ``python -m games`` hub launcher.

Two layers are exercised, kept honest against the opener-as-OPAQUE-callable
discipline the oracle's ``world_registry`` established:

1. ``services/world_registry.py`` — the GAME-NEUTRAL registry: register / get /
   all_entries (stable order) / duplicate replacement / idempotent re-register /
   clear, and that a ``WorldEntry`` opener is an opaque callable the registry
   stores without inspecting. It must NOT import ``games.*`` (the neutrality
   guard).
2. ``games/__main__.py`` — the hub launcher: ``run_hub`` lists the wired games
   and dispatches ``play mining`` / ``play fishing`` (and a bare number) to the
   RIGHT entry's opener, proven via an INJECTED fake launcher (no real
   sub-session is ever spawned); unknown ids, quit, and EOF/end-of-list are
   handled cleanly.
"""

from __future__ import annotations

import sys

import pytest

from services import world_registry
from services.world_registry import WorldEntry

from games import __main__ as hub
from games.registry_wiring import wire_games


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


# ---------------------------------------------------------------------------
# services/world_registry.py — the neutral registry
# ---------------------------------------------------------------------------
def test_register_then_get_returns_the_same_entry() -> None:
    entry = _entry("mining")
    world_registry.register(entry)
    assert world_registry.get("mining") is entry


def test_get_unknown_id_returns_none() -> None:
    assert world_registry.get("nope") is None


def test_all_entries_preserves_registration_order() -> None:
    world_registry.register(_entry("mining"))
    world_registry.register(_entry("fishing"))
    world_registry.register(_entry("dnd"))
    assert [e.game_id for e in world_registry.all_entries()] == ["mining", "fishing", "dnd"]


def test_all_entries_returns_a_tuple() -> None:
    world_registry.register(_entry("mining"))
    assert isinstance(world_registry.all_entries(), tuple)


def test_duplicate_game_id_replaces_in_place_without_reordering() -> None:
    world_registry.register(_entry("mining"))
    world_registry.register(_entry("fishing"))
    replacement = WorldEntry("mining", "New", "New blurb", lambda: 7)
    world_registry.register(replacement)
    # Still two entries, mining kept its first position, but is the replacement.
    assert [e.game_id for e in world_registry.all_entries()] == ["mining", "fishing"]
    assert world_registry.get("mining") is replacement


def test_re_registering_same_id_is_idempotent_in_count() -> None:
    for _ in range(3):
        world_registry.register(_entry("mining"))
    assert len(world_registry.all_entries()) == 1


def test_clear_empties_the_registry() -> None:
    world_registry.register(_entry("mining"))
    world_registry.clear()
    assert world_registry.all_entries() == ()
    assert world_registry.get("mining") is None


def test_world_entry_opener_is_an_opaque_callable_the_registry_stores_verbatim() -> None:
    marker = object()
    entry = _entry("mining", opener=lambda: marker)
    world_registry.register(entry)
    stored = world_registry.get("mining")
    assert callable(stored.opener)
    # The registry never invokes or inspects the opener — calling it is the
    # composition root's job, and it round-trips whatever the root supplied.
    assert stored.opener() is marker


def test_world_registry_module_imports_no_games_package() -> None:
    # Neutrality guard: the services-layer registry must carry no services->games
    # edge. Importing it in a FRESH interpreter must not pull in games.* — run in
    # a subprocess so the check is hermetic and independent of what the rest of
    # this test session has already imported.
    import subprocess

    proc = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; import services.world_registry; "
                "leaked=[m for m in sys.modules if m=='games' or m.startswith('games.')]; "
                "assert leaked==[], leaked; print('NEUTRAL')"
            ),
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, f"world_registry pulled in games modules: {proc.stderr}"
    assert "NEUTRAL" in proc.stdout


# ---------------------------------------------------------------------------
# games/registry_wiring.py — the composition root binding
# ---------------------------------------------------------------------------
def test_wire_games_registers_both_playable_games_in_order() -> None:
    wire_games(world_registry)
    assert [e.game_id for e in world_registry.all_entries()] == ["mining", "fishing", "dnd"]


def test_wire_games_is_idempotent() -> None:
    wire_games(world_registry)
    wire_games(world_registry)
    assert [e.game_id for e in world_registry.all_entries()] == ["mining", "fishing", "dnd"]


def test_wired_openers_are_callable() -> None:
    wire_games(world_registry)
    for entry in world_registry.all_entries():
        assert callable(entry.opener)


# ---------------------------------------------------------------------------
# games/__main__.py — the hub launcher (fake launcher; no real sub-session)
# ---------------------------------------------------------------------------
def test_run_hub_lists_both_wired_games() -> None:
    launched: list[str] = []
    result = hub.run_hub(["list", "quit"], launch=lambda e: launched.append(e.game_id))
    assert "mining" in result.text
    assert "fishing" in result.text
    assert launched == []  # listing launches nothing


def test_play_mining_invokes_minings_opener_via_fake_launcher() -> None:
    launched: list[str] = []
    result = hub.run_hub(["play mining", "quit"], launch=lambda e: launched.append(e.game_id))
    assert launched == ["mining"]
    assert result.launched == ["mining"]


def test_play_fishing_invokes_fishings_opener_via_fake_launcher() -> None:
    launched: list[str] = []
    result = hub.run_hub(["play fishing", "quit"], launch=lambda e: launched.append(e.game_id))
    assert launched == ["fishing"]
    assert result.launched == ["fishing"]


def test_play_by_number_dispatches_to_the_listed_entry() -> None:
    launched: list[str] = []
    # Menu order is mining(1), fishing(2); "play 2" must launch fishing.
    hub.run_hub(["play 2", "quit"], launch=lambda e: launched.append(e.game_id))
    assert launched == ["fishing"]


def test_unknown_game_id_is_handled_gracefully_and_launches_nothing() -> None:
    launched: list[str] = []
    result = hub.run_hub(["play zorp", "quit"], launch=lambda e: launched.append(e.game_id))
    assert launched == []
    assert "Unknown game" in result.text


def test_quit_ends_the_session_before_later_commands_run() -> None:
    launched: list[str] = []
    hub.run_hub(["quit", "play mining"], launch=lambda e: launched.append(e.game_id))
    assert launched == []  # the command after quit never dispatched


def test_end_of_command_list_closes_cleanly_like_eof() -> None:
    # No explicit quit: the hub closes at end-of-list without raising and still
    # prints the sign-off (the EOF-equivalent path).
    result = hub.run_hub(["list"], launch=lambda e: None)
    assert "Thanks for playing" in result.text


def test_run_hub_reads_from_an_injected_registry() -> None:
    world_registry.register(_entry("solo"))
    launched: list[str] = []
    result = hub.run_hub(
        ["list", "play solo", "quit"],
        registry=world_registry,
        launch=lambda e: launched.append(e.game_id),
    )
    assert "solo" in result.text
    assert launched == ["solo"]
