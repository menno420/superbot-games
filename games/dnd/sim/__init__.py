"""D&D sims — pure, seeded balance harnesses (no LLM / Discord / DB / IO).

Mirrors ``games.fishing.sim`` and ``games.exploration.survival.sim``: drives the
shipped, deterministic D&D ``core`` resolver over every scene in the data catalog
and aggregates the reward each menu option yields, so the **bounded-menu economy**
(Q-0040 / D-0007) is *justified by a committed simulation* rather than asserted by
design alone. Run a sim directly
(``python3 -m games.dnd.sim.menu_sim``); the pinned bounds it produces are
re-asserted by a matching fast test in ``tests/dnd/``.
"""
