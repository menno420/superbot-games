# Shared encounter seam

The **public shared** encounter-resolution seam (claim-first per `docs/lanes.md`).
Both lanes consume it; **mining owns the production resolver**, exploration consumes
it via the Protocol. One resolution core serves all three Q-0186 triggers
(grid roaming, explore actions, chat activity).

## Modules

| Module | What it is |
|---|---|
| `interface.py` | `EncounterTrigger`, `EncounterRequest`, `EncounterOutcome`, and the `EncounterResolver` Protocol. |
| `reference.py` | `ReferenceEncounterResolver` — a deterministic, dependency-free reference impl. |

## Public API

```python
from games.shared.encounter.interface import (
    EncounterRequest, EncounterTrigger, EncounterResolver,
)
from games.shared.encounter.reference import ReferenceEncounterResolver

resolver: EncounterResolver = ReferenceEncounterResolver()
outcome = resolver.resolve(EncounterRequest(
    trigger=EncounterTrigger.GRID_ROAM,
    player_id="p1", world_seed="world-42", context={"zone": "north"},
))
# outcome.kind in {"none", "creature", "cache", "event"}
```

## Invariants

- **Determinism** — the outcome is a pure function of
  `(world_seed, player_id, trigger, sorted context items)`, seeded through the
  engine's own `DetRng`.
- **Reference, replaceable** — `reference.py` exists so exploration is unblocked
  now. Mining's production core replaces it via the `EncounterResolver` Protocol
  without touching consumers.
- **Interface changes are announced in BOTH lanes' status files** in the same
  session they ship (`docs/lanes.md`).
