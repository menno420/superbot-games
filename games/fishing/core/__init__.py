"""Fishing domain — pure, self-contained game logic (no Discord, no DB, no views).

This is **new design, sim-pinned in-repo** (``docs/design/fishing-catch-skeleton.md``) —
not an oracle port. It reuses the shipped cross-game substrate directly:

* ``games.mining.core.energy`` — the passive-regen energy "fuel" model; a cast spends
  :data:`catch.CAST_COST` through it, so fishing shares the one energy economy.
* ``games.mining.core.equipment`` — the cross-game ``EffectiveStats`` gear model; the
  resolver reads its ``fishing_power`` / ``bite_luck`` fields (Q-0175) as the only
  advantage levers (gear earned in-domain, never bought).

Modules:
    species  — THE THEME DATA: the species table (every player-visible noun lives here
               as data rows keyed on neutral string ids; Q-0267 theme-readiness).
    rng      — deterministic per-spot seed helper (independent splitmix64 stream).
    catch    — THE RESOLVER: ``resolve_cast`` → a frozen ``CastOutcome``. Deterministic
               by default, injectable rng for live variance. NO LLM anywhere.
"""
