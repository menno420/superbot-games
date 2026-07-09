"""REFERENCE encounter resolver — deterministic, dependency-free.

Mining owns the PRODUCTION encounter core (``games/shared/`` is claim-first);
this reference implementation exists so the exploration lane is unblocked NOW.
Replace it via the ``EncounterResolver`` Protocol without touching consumers.

Determinism: the outcome is a pure function of ``(world_seed, player_id, trigger,
sorted context items)`` seeded through the engine's own ``DetRng``. No wall-clock,
no ``random`` module, no I/O.
"""

from __future__ import annotations

from games.exploration.quest.rng import DetRng, derive_seed

from .interface import EncounterOutcome, EncounterRequest, EncounterResolver

# Weighted table over encounter kinds. Ordered; weights sum to 100.
_KINDS: tuple[str, ...] = ("none", "creature", "cache", "event")
_WEIGHTS: tuple[int, ...] = (50, 25, 15, 10)

# The allowed outcome-kind set (public, for consumers/tests).
ALLOWED_KINDS: frozenset[str] = frozenset(_KINDS)


class ReferenceEncounterResolver(EncounterResolver):
    """A seedable reference resolver satisfying the ``EncounterResolver`` Protocol."""

    def resolve(self, request: EncounterRequest) -> EncounterOutcome:
        context_items = tuple(
            f"{k}={request.context[k]}" for k in sorted(request.context)
        )
        seed = derive_seed(
            request.world_seed,
            request.player_id,
            request.trigger.value,
            *context_items,
        )
        rng = DetRng(seed)
        kind = rng.weighted_choice(_KINDS, _WEIGHTS)
        # A second draw gives the outcome a stable intensity/detail value.
        intensity = rng.randint(1, 5)
        encounter_id = f"enc-{request.trigger.value}-{seed & ((1 << 32) - 1):08x}"
        payload: dict[str, object] = {
            "trigger": request.trigger.value,
            "intensity": intensity,
        }
        return EncounterOutcome(
            encounter_id=encounter_id,
            kind=kind,
            payload=payload,
            seed=seed,
        )
