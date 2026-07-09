"""Dependency-free deterministic RNG for the quest/encounter engine.

Determinism is a hard invariant (Q-0040): the deterministic core owns every
outcome the AI later narrates, so the engine must be PURE and SEEDABLE — no
wall-clock, no ``random`` module / global RNG, no I/O. Same seed -> byte-identical
sequence, across processes and across ``PYTHONHASHSEED`` values.

- ``DetRng`` is a splitmix64 generator seeded with a 64-bit int.
- ``derive_seed`` is an FNV-1a 64-bit hash over the ``str()`` bytes of its parts.
  We deliberately do NOT use Python's builtin ``hash()`` — it is salted by
  ``PYTHONHASHSEED`` and therefore not stable across processes.
"""

from __future__ import annotations

from typing import Sequence, TypeVar

_MASK64 = (1 << 64) - 1

_FNV_OFFSET_BASIS = 0xCBF29CE484222325
_FNV_PRIME = 0x100000001B3

T = TypeVar("T")


def _splitmix64(state: int) -> tuple[int, int]:
    """Advance a splitmix64 state; return (new_state, output_value)."""
    state = (state + 0x9E3779B97F4A7C15) & _MASK64
    z = state
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & _MASK64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & _MASK64
    z = z ^ (z >> 31)
    return state, z & _MASK64


def derive_seed(*parts: object) -> int:
    """FNV-1a 64-bit hash over the UTF-8 bytes of ``str(part)`` for each part.

    Stable across processes and independent of ``PYTHONHASHSEED``. Order-sensitive:
    a ``\\x1f`` unit separator is hashed between parts so ``("a", "bc")`` and
    ``("ab", "c")`` derive different seeds.
    """
    h = _FNV_OFFSET_BASIS
    for i, part in enumerate(parts):
        if i:
            h = ((h ^ 0x1F) * _FNV_PRIME) & _MASK64
        for byte in str(part).encode("utf-8"):
            h = ((h ^ byte) * _FNV_PRIME) & _MASK64
    return h & _MASK64


class DetRng:
    """Deterministic splitmix64 RNG. No global state, no wall-clock, no I/O."""

    __slots__ = ("_state",)

    def __init__(self, seed: int) -> None:
        self._state = seed & _MASK64

    def next_u64(self) -> int:
        """Return the next 64-bit unsigned integer and advance the state."""
        self._state, value = _splitmix64(self._state)
        return value

    def randint(self, lo: int, hi: int) -> int:
        """Return an integer in the inclusive range [lo, hi]."""
        if hi < lo:
            raise ValueError(f"randint: hi ({hi}) < lo ({lo})")
        span = hi - lo + 1
        return lo + (self.next_u64() % span)

    def choice(self, seq: Sequence[T]) -> T:
        """Return a deterministically-chosen element of a non-empty sequence."""
        if not seq:
            raise IndexError("choice: empty sequence")
        return seq[self.next_u64() % len(seq)]

    def weighted_choice(self, items: Sequence[T], weights: Sequence[int]) -> T:
        """Return an item chosen with probability proportional to its weight.

        Weights are non-negative integers; at least one must be positive.
        """
        if len(items) != len(weights):
            raise ValueError("weighted_choice: items/weights length mismatch")
        total = sum(weights)
        if total <= 0:
            raise ValueError("weighted_choice: weights must sum to a positive value")
        roll = self.next_u64() % total
        upto = 0
        for item, weight in zip(items, weights):
            upto += weight
            if roll < upto:
                return item
        # Unreachable when total > 0, but keeps type checkers satisfied.
        return items[-1]
