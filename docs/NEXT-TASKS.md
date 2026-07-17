# superbot-games — Next Tasks

> **Status:** `reference`
>
> Truth-stamped 2026-07-17 (fresh-start cleanup). Successor to the retired
> `control/` message-bus backlog (inbox/outbox). Top next steps for the games
> program when the recreated Project resumes work. Sources: the fleet recon
> digest (2026-07-17), `docs/design/`, and `docs/planning/`. Each item cites
> where its detail lives.

## Context

The four games — mining · fishing · dnd · exploration — are playable and
production-hardened (~97% coverage, sim-pinned) behind one hub
(`python3 -m games`). What remains is **content depth**, the **shared
inventory unification**, and **wiring the games into `superbot-next`** as a
game plugin. The autonomy apparatus (auto-merge bus, per-seat heartbeats,
self-arm wake routines) has been wound down — see `CONSTITUTION.md` and
`current-state.md`. Merges are **human-gated**: open a PR ready and stop; the
owner reviews and lands it.

## Headline feature — D&D story game (P4)

**Ship the D&D story game P4:** build the `dungeon_master` orchestration
profile + Story Action menu toolset over the already-built, sim-pinned
deterministic quest/engine. Full design + spec:
[`planning/dnd-story-game-plan.md`](planning/dnd-story-game-plan.md) — a
complete P3→P4 plan and the single largest buildable feature. Gated only on
the one-line ⚑ Q-0040 bounded-authority owner sign-off (the plan recommends
**APPROVE**).

## Top next steps

1. **Fishing full-roster economy.** Pin + wire the ~29 unpinned legacy fish
   species (fishing ships 4 vs the original's ~21) — the biggest
   player-visible gap and the standing target of the (retired) ORDER 008
   "production-grade all games". The full-roster SIM-REQUEST content is
   captured in the retired `control/outbox.md`
   (`SIM-REQUEST · fishing-full-roster-economy`); supply the constants and
   wire them verbatim — no numbers invented until pinned.
2. **Wire `games/shared/inventory/` into mining/fishing/exploration.** The
   pure-domain foundation exists (migration PR-1) but nothing consumes it —
   build PRs 2–6 of the world-inventory-resource-contract to unify
   item / quantity / reward handling across all four games. Detail:
   `docs/design/world-inventory-resource-contract.md`.
3. **Build the rung-3 host-adapter** so these games actually run inside
   `superbot-next`, against `docs/game-plugin-contract.md`. Blocked on the
   owner packaging/hermeticity + persistence-format decisions — surface those
   as a single decision set. Detail: `docs/design/mining-host-adapter.md`.
4. **Standalone-CLI save/load persistence.** Resolve the persistence
   format-governance decision (`docs/design/persistence-design.md`) and
   implement save/load so the CLIs are replayable across sessions.
5. **Clear the 4 standing owner decisions** into `docs/decisions.md` so future
   work is unblocked without the message-bus (see below).

## Owner decisions to unblock the above

Extracted from the retired `control/outbox.md` (all ↩️ reversible replies, no
destructive click owed):

- **Q-0040** — D&D bounded-authority sign-off → unblocks the headline feature
  (plan recommends **APPROVE**).
- **D2 audit-grants ratification** — ratify (or reverse) auditing item grants
  through the mining seam (`control/outbox.md` § DECISION-NOTE · D1/D2;
  recommendation: **ratify as built**, reversal stays a one-line toggle).
- **Rung-3 packaging / hermeticity** — approve packaging sbg as an installable
  distribution → unblocks the host-adapter (item 3).
- **Persistence format-governance** (3 sub-decisions: contract-impl vs
  flat-local · field→namespace mapping · load-vs-audit rule) → unblocks
  save/load (item 4).
- **Transfer-policy source model** — true source-debit vs seeded-credit
  (`docs/design/persistence-design.md` §5).

_Deeper backlog: `docs/planning/2026-07-16-overnight-menu.md` is an unfiltered
60-idea owner-triage menu (candidates, not approved work)._
