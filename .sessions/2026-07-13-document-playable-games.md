# 2026-07-13 · document the playable game entrypoints (README · docs)

> **Status:** ✅ `complete`
>
> 📊 Model: Opus 4.8 · 2026-07-13 · document playable game entrypoints

## 💡 Session idea

The night run made three things playable that the README never mentions: the
game hub (`python3 -m games`, `games/__main__.py`) and the two standalone CLIs
it wires (`python3 -m games.mining` / `python3 -m games.fishing`,
`games/mining/cli.py` + `games/fishing/cli.py`). A player reading the repo has no
pointer to any of them. This session adds ONE concise "## Playing the games"
section to the EXISTING `README.md` (edited in place — no new doc file, to avoid
docs-gate orphan/reachability findings). The copy is captured from the real,
headless runs (`printf 'list\nhelp\nquit\n' | python3 -m games`, and each CLI's
`help`/`quit`) so the documented command sets are verbatim: the hub's
`play <id>`/number, `list`, `help`, `quit`; mining's
mine/harvest/sell/buy/repair/descend/ascend/build/vault/skill/status/help/quit;
fishing's cast/spot/spots/status(haul)/help/quit. A closing one-liner points at
the rung-2 audited workflow seams (`services/mining_workflow.py` /
`services/fishing_workflow.py`) with an in-memory audit sink, and defers
balance/persistence/host-hub items to `control/outbox.md`. Docs-only: no code, no
balance number, no test-floor change.

## ⟲ Previous-session review

Builds directly on the three 2026-07-13 playability cards — the two standalone
CLIs (`.sessions/2026-07-13-mining-standalone-cli.md`,
`.sessions/2026-07-13-fishing-standalone-cli.md`) and the hub registry
(`.sessions/2026-07-13-games-hub-registry.md`, which wired both games into the
neutral `services/world_registry.py`). Those cards shipped the playable loops but
left them undocumented in the README; this session closes only that gap. It keeps
the same discipline they set — no economy number is invented here, and the
open persistence/balance/host-hub questions stay routed to `control/outbox.md`
rather than being answered in passing.
