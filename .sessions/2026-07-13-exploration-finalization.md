# 2026-07-13 · Exploration finalization (three green islands → playable · build)

> **Status:** ✅ `complete`
>
> 📊 Model: Opus 4.8 · 2026-07-13T02:41:46Z · exploration finalization

## 💡 Session idea

Finalize the EXPLORATION game so it is actually PLAYABLE, mirroring the D&D /
fishing finalizations EXACTLY (seam → CLI → hub). The exploration lane shipped
THREE independently green islands with no driver: the deterministic quest engine
(`games/exploration/quest/` — the bounded-menu `catalog`, the `engine` lifecycle
`offer → accept → apply_event → grant_rewards`, the frozen `models`, the
`predicates`), the survival Energy axis (`games/exploration/survival/` —
`difficulty` `TUNABLES` scaling the *shipped* mining bar per D-0004), and the
shared encounter resolver (`games/shared/encounter/` — the dependency-free
`ReferenceEncounterResolver`). Nothing wired them together. This session adds the
smallest honest driver:

1. **`services/exploration_workflow.py`** — the audited WORKFLOW seam. A mutable
   `ExplorationState` (current `QuestInstance`, survival difficulty + energy,
   accumulated `RewardLedger`, `player_id`, `world_seed`) and four audited ops:
   `offer(state, template_id, tier, *, sink)` (engine mints the OFFERED
   instance), `accept(state, *, sink)` (OFFERED → ACTIVE), `apply_action(state,
   action, *, sink)` (maps a BOUNDED action — one of the active quest's pending
   objective keys — to the objective-advancing `GameEvent` the engine already
   defines, resolves an `EXPLORE_ACTION` encounter, debits the difficulty's
   survival `cost`, and calls `engine.apply_event`), and `grant_rewards(state,
   *, sink)` (banks the tier-capped bundle on COMPLETED). Each STATE-CHANGING op
   emits exactly ONE 11-field `AuditRecord` (subsystem `"exploration"`) via the
   injected `Sink`; an honest no-op (unknown template, no offered/active/
   completed quest, off-menu action, too-tired action) records NOTHING and
   returns `ok=False`. It REUSES the game-neutral `services/audit.py` types
   VERBATIM (no new audit schema) — the fourth game to share that one contract.
2. **`games/exploration/cli.py` + `games/exploration/__main__.py`** —
   `python3 -m games.exploration`, a bounded-menu text REPL: `quests` (show
   `catalog.menu()`), `offer <id> [tier]` / `accept`, `act <bounded-action>`,
   `status`, `help`, `quit`. The HUMAN picks from the fixed catalog + the active
   quest's bounded action menu; a completed quest banks automatically. Read-only
   verbs, graceful off-menu handling (the seam surfaces the valid menu — never a
   silent clamp), and a session summary (quests completed, rewards banked, audit
   rows). Mirrors `games/dnd/cli.py` structure/voice.
3. **Hub registration** — one row added to `games/registry_wiring.py` `_GAMES`
   so `python3 -m games` lists and launches Exploration as game 4 alongside
   mining + fishing + D&D.

HARD-SCOPE discipline: NO AI-DM, NO generative narration, NO DM policy for
choosing quests — the human picks from the bounded menus, never a generative
loop. NO message-XP faucet / `leverage.menu_width` progression / `CHAT_ACTIVITY`
chat-bus trigger wired (left in the owner queue). ZERO new quest
templates/objectives/content — the seam drives ONLY the existing 5-template
catalog + survival tunables + the shared encounter resolver. NO invented balance
numbers (every reward/cap/cost/noun quoted VERBATIM from the engine/catalog/
survival modules). The `catalog.py` `TIER_CAPS` placeholder bands (D-0008,
pending Q-0087 reconciliation) and the survival Medium/Hard "first-candidate
gradient" are filed as a SIM-REQUEST in `control/outbox.md`, NOT tuned or
invented. Tests land in `services/tests/test_exploration_workflow.py` (30) +
the NEW `tests/exploration/test_cli.py` (15) suite, each bumping only its OWN
floor; the engine suite `games/exploration/tests` (55) is untouched.

## ⟲ Previous-session review

Builds directly on the D&D finalization (`.sessions/2026-07-13-dnd-finalization.md`,
#75), which is the EXACT pattern mirrored here: a top-level
`services/<game>_workflow.py` seam reusing the game-neutral `services/audit.py`,
a testable `run_commands(commands, *, sink, state)` CLI with an `input()` loop in
`__main__`, and one `_GAMES` row wiring the CLI `main` into the neutral world
registry as an opaque opener. Exploration differs from D&D in ONE honest way
worth stating: D&D audits EVERY `choose` (including a clamp to the safe default —
the audited event is the DM's bounded DECISION), whereas exploration has NO clamp
— an off-menu action, a too-tired action, or an op with no eligible quest is
simply an honest NO-OP that records NOTHING (mirroring fishing's
no-op-skips-audit rule). This slice adds no new quest content and no AI anywhere
in the loop — the engine, survival tunables, and reference resolver that the
existing `games/exploration/tests` suite (55) pins are driven unchanged.
`control/status.md` / `control/inbox.md` are untouched; the outbox APPENDS one
dated SIM-REQUEST beneath the existing entries (one-writer lane).
