# 2026-07-13 · D&D finalization (walking skeleton → playable · build)

> **Status:** ✅ `complete`
>
> 📊 Model: Opus 4.8 · 2026-07-13T02:17:46Z · dnd finalization

## 💡 Session idea

Finalize the D&D walking skeleton so it is actually PLAYABLE, mirroring the
fishing finalization EXACTLY (seam → CLI → hub). Rung 1 shipped the pure core
(`games/dnd/core/` — the bounded-menu `resolve`, the pre-priced `EFFECTS`
registry, the `models` schema) plus its 3-scene data catalog
(`games/dnd/data/scenes.py`: `waystation_road` → `waystation_gate` /
`treeline_watch`), but nothing DROVE the resolver — D&D was pure functions with
no way to sit down and play. This session adds the smallest honest driver:

1. **`services/dnd_workflow.py`** — the audited WORKFLOW seam. A mutable
   `DnDState` (current `scene_id`, running reward totals, `player_id`, `seed`,
   `xp`) and one audited action, `choose(state, option_id, *, sink, ...)`: load
   the current scene via `get_scene`, build a `DMChoice(option_id)`, call the
   pure `resolve(...)` (which already clamps any off-menu id to the deterministic
   safe default — relied on, never re-implemented), fold the code-owned reward
   into the running totals, advance `state.scene_id` to the resolved option's
   pre-defined `next_scene_id` (`None` ⇒ the beat concludes / stays), and emit
   exactly ONE 11-field `AuditRecord` (subsystem `"dnd"`, `mutation_type`
   `"dnd:choose"`) via the injected `Sink` as the last step. It REUSES the
   game-neutral `services/audit.py` types VERBATIM (no new audit schema) — the
   third game to share that one contract without welding to another's seam.
2. **`games/dnd/cli.py` + `games/dnd/__main__.py`** — `python3 -m games.dnd`, a
   text REPL that shows the current scene's prose + its bounded numbered menu and
   dispatches a number / option-id to the seam (the HUMAN occupies the DM's exact
   one-id seat). Read-only `look` / `status` / `help` / `quit`, off-menu clamps
   with a friendly hint, and a session summary (scenes visited, total reward,
   audit-record count). Mirrors `games/fishing/cli.py` structure/voice.
3. **Hub registration** — one row added to `games/registry_wiring.py` `_GAMES`
   so `python3 -m games` lists and launches D&D alongside mining + fishing.

HARD-SKELETON discipline: ZERO new scenes / effects / mechanics / content; NO
AI-DM, NO generative narration, NO `dungeon_master` profile — all text is
verbatim from `data/scenes.py`; NO save/resume persistence (ephemeral in-memory
state only); NO invented balance numbers (every reward/number/noun quoted from
the resolver/effects/scenes). The escort-bundle DOUBLE-MINT (both
`advance_escort` and `signal_escort` fire `escort_step`, so one traversal mints
`safe_passage` 2×) is filed as a SIM-REQUEST in `control/outbox.md`, NOT patched
or capped (that is a balance/owner call, no invented cap). Tests land in
`services/tests/test_dnd_workflow.py` + `tests/dnd/test_cli.py`, each bumping
only its OWN suite floor.

## ⟲ Previous-session review

Builds directly on the fishing finalization arc — the WORKFLOW seam card
(`.sessions/2026-07-13-fishing-workflow-seam.md`, #69), the standalone CLI card
(`.sessions/2026-07-13-fishing-standalone-cli.md`, #71), and the hub-registry
card (`.sessions/2026-07-13-games-hub-registry.md`, #72) — which together are the
EXACT pattern mirrored here: a top-level `services/<game>_workflow.py` seam
reusing the game-neutral `services/audit.py`, a testable
`run_commands(commands, *, sink, state)` CLI with an `input()` loop in
`__main__`, and one `_GAMES` row wiring the CLI `main` into the neutral world
registry as an opaque opener. D&D differs from fishing in ONE honest way worth
stating: fishing's seam records NOTHING on a no-op (too-tired) cast, whereas the
D&D seam records EVERY `choose` — the audited event is the DM's bounded DECISION
itself (option chosen, transition, any minted reward), so an off-menu clamp to
the safe default STILL records the default resolution. This slice adds no new
scene/effect/content and no AI anywhere in the resolution loop — the resolver
core the fuzzer pinned (`.sessions/2026-07-11-dnd-clamp-fuzz.md`) is driven
unchanged. `control/status.md` / `control/inbox.md` are untouched; the outbox
APPENDS one dated SIM-REQUEST beneath the existing entries (one-writer lane).
