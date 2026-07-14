"""Mining CLI verb-table/help parity — the gate, routing, and help agree.

The CLI's action-verb surface is single-sourced: ``_ACTION_VERBS`` is derived
from the ``_ACTIONS`` dispatch table, and ``help_lines()`` must name exactly
that surface plus the documented control verbs. A verb added to the table
without a help row (or a ghost help row) reddens here.
"""

from __future__ import annotations

from games.mining import cli

#: The read-only/control verbs help documents alongside the action verbs.
#: (The accepted-but-undocumented aliases — ``q``, ``inventory``, ``?`` —
#: are deliberately NOT in help; step() still accepts them.)
_DOCUMENTED_CONTROL = frozenset({"status", "inv", "help", "quit", "exit"})


def test_action_verbs_derived_from_dispatch_table() -> None:
    assert cli._ACTION_VERBS == frozenset(cli._ACTIONS)
    assert all(callable(handler) for handler in cli._ACTIONS.values())


def test_help_names_exactly_the_verb_surface(extract_help_verbs) -> None:
    named = extract_help_verbs(cli.help_lines())
    assert named == cli._ACTION_VERBS | _DOCUMENTED_CONTROL
