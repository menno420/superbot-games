"""Mining sims — pure, seeded balance harnesses (no Discord / DB / IO).

Each module here runs a pure ``games.mining.core`` model over many seeds and
aggregates the outcome distributions, so a new balance number is *justified by a
committed simulation* (the founding sim-pin discipline) rather than guessed. Run
a sim directly (``python3 -m games.mining.sim.<name>``); the pinned bounds it
produces are re-asserted by a matching fast test in ``tests/mining/``.
"""
