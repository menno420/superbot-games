"""Fishing game plugin.

Three layers (mirrors ``games.mining`` — design: ``docs/design/fishing-catch-skeleton.md``):

* ``core`` — the pure domain (this package): stdlib-only, no Discord / DB / IO,
  injectable RNG, unit-tested. The catch resolver, its species data table, and the
  deterministic seed helper. Deterministic code owns every outcome — **no LLM
  anywhere** in the loop.
* ``workflow`` — (named-next) the audited op seam: read host state → call ``core`` to
  decide the cast → one transaction to commit (debit energy, add the caught fish).
* host-adapter — (named-next) the superbot-next ``SubsystemManifest`` binding
  (commands / panels / stores) — the swappable boundary.

Only ``core`` (+ its ``sim`` harness) ships in this first walking-skeleton slice. It
**reuses** the shipped cross-game substrate rather than duplicating it: the energy
engine (``games.mining.core.energy``) for the cost of a cast, and the ``EffectiveStats``
gear model (``games.mining.core.equipment`` — its ``fishing_power`` / ``bite_luck``
fields, Q-0175) for the gear knobs. It **extends** the determinism convention with its
own independent per-spot splitmix64 stream (``core.rng``), mirroring mining's
per-subsystem salt pattern.
"""
