"""Game-neutral audit types for the services (WORKFLOW) layer.

The audit record shape + the sink port are deliberately **game-agnostic** so
every game's audited seam reuses them without coupling to another game: the
mining seam (``services/mining_workflow.py``) and the next-slice fishing seam
(``services/fishing_workflow.py``) both ``from services.audit import
AuditRecord, Sink, InMemorySink`` — importing them from a game module instead
would weld two games together through the audit types.

:class:`AuditRecord` is the oracle's 11-field structural ``audit.action_recorded``
schema, adopted verbatim (D1 in ``docs/design/mining-workflow-seam.md`` §5).
Structural fields (mutation id, timestamps, ids, ``scope``, ``target``) are
constructed by a seam; the ``mutation_type`` / economy tokens come verbatim from
each game's pure core. Stdlib-only, so CI stays hermetic.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class AuditRecord:
    """One structural audit row — the 11-field ``audit.action_recorded`` schema.

    Copied field-for-field from the oracle's ``emit_audit_action`` contract
    (``docs/design/mining-workflow-seam.md`` §3a). Game-neutral: ``subsystem``
    names which game emitted it.
    """

    mutation_id: str  # uuid4 hex — links this record to its (future) audit row
    subsystem: str  # high-level area token (e.g. "mining", "fishing")
    mutation_type: str  # verb / reason token for the change
    target: str  # human-resolvable id of the thing changed
    scope: str  # "global" | "guild" — kept open for future scopes
    guild_id: int | None  # discord guild id, or None for global scope
    prev_value: str | None  # string-rendered prior value (None = first write)
    new_value: str | None  # string-rendered new value (None = delete / clear)
    actor_id: int | None  # actor id, or None for system / backfill
    actor_type: str  # capability-resolver actor-type token
    occurred_at: datetime  # commit timestamp, at emit


@runtime_checkable
class Sink(Protocol):
    """The injected audit port a seam commits to (D3/D4).

    A seam depends only on this ``record`` shape; the real DB / EventBus binding
    is deferred to the host-adapter rung. A production binding should be
    failure-safe (a dropped audit event is non-fatal — the oracle's "DB state is
    authoritative" property), but the Protocol keeps that a binding concern.
    """

    def record(self, record: AuditRecord) -> None:  # pragma: no cover - protocol
        ...


class InMemorySink:
    """A :class:`Sink` that just collects records in a list (for tests / dry runs)."""

    def __init__(self) -> None:
        self.records: list[AuditRecord] = []

    def record(self, record: AuditRecord) -> None:
        self.records.append(record)


__all__ = ["AuditRecord", "Sink", "InMemorySink"]
