"""Shared fixtures for the tests/ tree.

Currently: the help-verb extractor the per-game CLI help-parity tests share
(``tests/<game>/test_help_parity.py``). Lives here — NOT in a suite dir — so
the four game suites can share one parser without creating a new registered
suite (``tests/`` itself contains no ``test_*.py``, so the floor guard does
not discover it as one).
"""

from __future__ import annotations

import re

import pytest


def _extract_help_verbs(help_lines: list[str]) -> frozenset[str]:
    """The set of verbs a CLI's ``help_lines()`` text names.

    Every game CLI renders command rows as two-space-indented lines whose
    command column leads with a lowercase verb, optionally aliased as
    ``verb / alias`` (e.g. ``quit / exit``). Placeholder rows (``<number>``)
    and prose/header lines (unindented) name no verb. Descriptions can
    contain slashes (``mining/combat/…``) or spaced slashes deeper in the
    line (``deeper / back``); only the LEADING ``verb / alias`` pattern is a
    verb group, so those never leak in.
    """
    verbs: set[str] = set()
    for line in help_lines:
        if not line.startswith("  ") or line.startswith("   "):
            continue  # header, blank, prose, or a continuation line
        match = re.match(r"([a-z]+)(?: / ([a-z]+))?", line.strip())
        if match:
            verbs.update(group for group in match.groups() if group)
    return frozenset(verbs)


@pytest.fixture
def extract_help_verbs():
    """The shared help-verb extractor (a plain callable, fixture-injected)."""
    return _extract_help_verbs
