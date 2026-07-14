"""DND CLI reserved-verb/help parity — help names the reserved surface.

The DND CLI deliberately has NO action-verb dispatch table: every
non-reserved token IS the story pick (the DM's one-id choice), and the
reserved control surface is already single-sourced as the union
``_RESERVED = _QUIT | _LOOK | _STATUS | _HELP``. What CAN drift is the help
text, so this pins the actual relation: help names exactly one spelling per
reserved group (plus the ``quit / exit`` alias pair), every named verb is
reserved, and no group is undocumented.
"""

from __future__ import annotations

from games.dnd import cli

#: The verbs help documents — the primary spelling of each reserved group
#: plus the ``exit`` alias. (``l`` / ``state`` / ``?`` / ``q`` are accepted
#: but deliberately undocumented.)
_DOCUMENTED = frozenset({"look", "status", "help", "quit", "exit"})


def test_help_names_exactly_the_documented_reserved_verbs(extract_help_verbs) -> None:
    named = extract_help_verbs(cli.help_lines())
    assert named == _DOCUMENTED
    assert named <= cli._RESERVED  # help never invents a non-reserved verb


def test_every_reserved_group_is_documented(extract_help_verbs) -> None:
    named = extract_help_verbs(cli.help_lines())
    for group in (cli._QUIT_VERBS, cli._LOOK_VERBS, cli._STATUS_VERBS, cli._HELP_VERBS):
        assert named & group, f"reserved group {sorted(group)} has no help row"
