"""Fishing CLI verb-table/help parity — the gate, routing, and help agree.

``_ACTION_VERBS`` (cast + the V043 sell leg) is derived from the ``_ACTIONS``
dispatch table; ``help_lines()`` must name exactly that surface plus the
documented navigation/control verbs (``spot`` mutates only the current spot
and is routed separately — it is navigation, not a seam action).
"""

from __future__ import annotations

from games.fishing import cli

#: The navigation/control/read-only verbs help documents alongside the action
#: verbs. ``value`` is the read-only V043 market-value preview (slice 3) — pure
#: information, routed separately from the mutating ``_ACTIONS`` and always in
#: help. (The accepted-but-undocumented alias ``q`` is deliberately NOT in help.)
_DOCUMENTED_CONTROL = frozenset(
    {"value", "spot", "spots", "status", "haul", "help", "quit", "exit"}
)


def test_action_verbs_derived_from_dispatch_table() -> None:
    assert cli._ACTION_VERBS == frozenset(cli._ACTIONS)
    assert all(callable(handler) for handler in cli._ACTIONS.values())


def test_help_names_exactly_the_verb_surface(extract_help_verbs) -> None:
    named = extract_help_verbs(cli.help_lines())
    assert named == cli._ACTION_VERBS | _DOCUMENTED_CONTROL
