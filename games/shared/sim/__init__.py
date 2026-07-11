"""Shared / cross-domain sims — pure, seeded harnesses (no Discord / DB / IO).

Where the per-domain sims (``games.mining.sim``, ``games.fishing.sim``,
``games.dnd.sim``, ``games.exploration.survival``) each pin ONE game's balance
numbers in isolation, the sims here enumerate the WHOLE economy at once: they
import and drive the shipped resolvers/catalogs of every world game and assert
the cross-domain invariants no single-game sim can see. Same discipline as the
per-domain lanes — drive the real shipped code, read the aggregate back out,
re-pin it as a fast test — applied one level up. Run a sim directly
(``python3 -m games.shared.sim.<name>``); the pinned bounds it produces are
re-asserted by a matching fast test in ``tests/shared/sim/``.
"""
