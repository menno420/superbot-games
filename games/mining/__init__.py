"""Mining game plugin.

Three layers (design: ``docs/design/mining-plugin-layout.md``):

* ``core`` — the pure domain (this package): stdlib-only, no Discord / DB / IO,
  injectable RNG/clock, unit-tested against the oracle's shipped behaviour. The
  port target from ``menno420/superbot`` ``disbot/utils/mining/*`` +
  ``disbot/utils/equipment.py``.
* ``workflow`` — (named-next) the audited op seam mirroring the oracle's
  ``services/mining_workflow.py``: read host state → call ``core`` to decide →
  one transaction to commit.
* host-adapter — (named-next) the superbot-next ``SubsystemManifest`` binding
  (commands / panels / stores / handlers) — the swappable boundary.

Only ``core`` ships in the first slice.
"""
