"""Host-facing service layer for superbot-games (rung 2 of the mining ladder).

This package lives **outside** ``games/mining/core/`` on purpose: the mining
purity guard (``tests/mining/test_purity.py``) forbids the core importing any
``services`` module and hard-asserts the core stays exactly 19 stdlib-only
modules. The seam may import ``games.mining.core.*`` freely (a one-way
dependency, core never imports back), so building it here keeps the guard
intact. See ``docs/design/mining-workflow-seam.md``.
"""
