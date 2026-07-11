"""Fishing sims — pure, seeded balance harnesses (no Discord / DB / IO).

Mirrors ``games.mining.sim``: runs the pure ``games.fishing.core`` resolver over many
seeds/spots × gear tiers and aggregates the catch distribution, so every balance number
in ``core.catch`` is *justified by a committed simulation* rather than guessed. Run a sim
directly (``python3 -m games.fishing.sim.catch_sim``); the pinned bounds it produces are
re-asserted by a matching fast test in ``tests/fishing/``.
"""
