"""Exploration CLI verb-table/help parity — the gate, routing, and help agree.

``_ACTION_VERBS`` (offer / accept / act) is derived from the ``_ACTIONS``
dispatch table step() routes through; ``help_lines()`` must name exactly that
surface plus the documented read-only/control verbs.
"""

from __future__ import annotations

from games.exploration import cli

#: The read-only/control verbs help documents alongside the action verbs.
#: (The accepted-but-undocumented aliases — ``menu``, ``state``, ``?``,
#: ``q`` — are deliberately NOT in help; step() still accepts them.)
_DOCUMENTED_CONTROL = frozenset({"quests", "status", "help", "quit", "exit"})


def test_action_verbs_derived_from_dispatch_table() -> None:
    assert cli._ACTION_VERBS == frozenset(cli._ACTIONS)
    assert all(callable(handler) for handler in cli._ACTIONS.values())


def test_help_names_exactly_the_verb_surface(extract_help_verbs) -> None:
    named = extract_help_verbs(cli.help_lines())
    assert named == cli._ACTION_VERBS | _DOCUMENTED_CONTROL
