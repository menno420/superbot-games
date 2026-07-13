# 2026-07-13 · games hub registry + launcher (world spine · build)

> **Status:** 🚧 `in-progress`
>
> 📊 Model: Opus 4.8 · 2026-07-13T01:33:55Z · games hub registry + launcher

## 💡 Session idea

Give the two playable ladders (mining, fishing) a single, game-neutral front
door. Rung 1 shipped each game's pure core, rung 2 shipped each audited WORKFLOW
seam, and the standalone-CLI slices made each game playable on its own
(`python3 -m games.mining` / `python3 -m games.fishing`) — but there was no
UNIFIED entry: no way to see both games in one place and pick one, and no
in-repo registry a future game could dock into. This session builds that spine,
mirroring the oracle's shipped `world_registry` (disbot `WorldEntry` seam,
opener-as-OPAQUE-callable so there is NO services→game edge).

Two pieces land. First, `services/world_registry.py` — GAME-NEUTRAL and
stdlib-only: a frozen `WorldEntry(game_id, title, blurb, opener)` where the
`opener` is an opaque `Callable[..., int | None]` the registry never
introspects, plus a tiny registry API — `register(entry)`, `get(game_id)`,
`all_entries()` (stable insertion order), and `clear()` (for tests). The
registry NEVER imports `games.*`: the opener is supplied by the composition
root, exactly as the oracle's registry keeps no views→services edge. Second,
`games/__main__.py` — the HUB LAUNCHER (`python3 -m games`): at startup it wires
both games by constructing a `WorldEntry` for each with an opener that launches
that game's existing standalone CLI (`games.mining.cli.main` /
`games.fishing.cli.main`), then lists the registered games (id · title · blurb)
and prompts the player to pick one (`play <id>` or a number), dispatching to the
chosen entry's opener; `list`, `help`, `quit`, EOF and unknown-id are all
handled gracefully. The registration lives in a dedicated
`games/registry_wiring.py` the hub calls (the composition root — NOT at
`services/world_registry.py` import, keeping it neutral), made idempotent
(clear-then-register) so tests don't double-register. The player loop is
factored so a test drives it TTY-free via
`run_hub(commands, *, registry=None, launch=None)` — an injected fake launcher
lets a test assert "picking mining invoked mining's opener" without spawning an
interactive sub-session; `__main__`/`main()` wraps the `input()` loop around the
same dispatch. Tests land in `services/tests/test_world_registry.py` (+ hub
tests), bumping the `services/tests` floor 74 → 74+N. NO game balance number is
touched; the FULL host world-hub binding (into superbot-next's plugin host)
stays rung-3 (owner-queue).

## ⟲ Previous-session review

Builds directly on the two 2026-07-13 standalone-CLI cards
(`.sessions/2026-07-13-mining-standalone-cli.md`, #70;
`.sessions/2026-07-13-fishing-standalone-cli.md`, #71), each of which shipped a
testable `run_commands(...)` core plus an `input()` loop in `__main__` and left
each game reachable only via its own `python3 -m games.X`. Those cards
deliberately built per-game front doors and deferred any UNIFIED entry; this
session adds the smallest honest unifier — a neutral world registry + a hub
launcher that composes both games' openers at the root. It mirrors the oracle's
already-SHIPPED `disbot/services/world_registry.py` (buildability map §world
spine: "opener-as-opaque-callable so no services→views edge"), transposed to
this repo as "no services→games edge". The mining/fishing core purity guards
(`tests/mining/test_purity.py`, `tests/fishing/test_purity.py`) are unaffected —
they gate `games.*.core` against `services`, and this slice adds neither a
services→games edge nor a core→services edge. Only the `services/tests` floor is
bumped (its own suite); no other suite floor is touched.
