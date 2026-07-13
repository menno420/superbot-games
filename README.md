# superbot-games

Shared home of SuperBot's **game plugins**. **One seat** owns SuperBot's entire game
world: mining, exploration, the D&D story game, fishing, and the shared world systems they
all draw on (inventory, tools, locations, resources, encounters). One seat, one world,
`games/**`.

The gen-1 two-Project lane split (game-mining and game-exploration as separate autonomous
Projects) is **history** — see [docs/lanes.md](docs/lanes.md), now marked GEN-1 HISTORY.
The single seat owns all of `games/**` and coordinates through the unified `control/` bus
(`control/inbox.md` + `control/status.md`); the per-lane `inbox-*.md` / `status-*.md` files
are archived alongside the lanes contract.

Games ship as **plugin packages** that the rebuilt bot (`menno420/superbot-next`) consumes
via its manifest/plugin contract. That contract is now **defined and binding** —
`menno420/superbot-next docs/game-plugin-contract.md@d3dba9b` (ledger D-0056, owner decision
2026-07-09). Work here still stays plugin-side: pure-domain packages built against the
superbot economy as oracle, with the host-facing adapters left as a later ladder rung. What
changed is that those seams can now be built against a concrete, versioned contract rather
than waiting for one to land.

Player-visible nouns (names, flavor, emoji) stay isolated in **data, not code**, so the
fleet's core/skin split can reach the world games later — build the mechanics against
neutral identifiers and keep the theme in swappable data (theme-readiness, directive
Q-0267).

## Playing the games

Two of the world games are playable right now as pure-domain text sessions. Run
them from the repo root:

**The hub — `python3 -m games`** (`games/__main__.py`) lists every registered
game and launches the one you pick. It is the composition root for the neutral
in-repo world registry (`services/world_registry.py`), which each game's
standalone CLI wires itself into. Commands: `list` (show the games), `play <id>`
or `play <n>` (or a bare id / number) to launch, `help`, and `quit`.

```
$ printf 'list\nhelp\nquit\n' | python3 -m games
🎮  Superbot Games — the hub. Type 'help' for commands, 'quit' to leave.
Available games (type 'play <id>' or a number):
  1. mining     ⛏️  Mining — Dig, descend, and sell your haul over the audited mining seam.
  2. fishing    🎣  Fishing — Cast a line across biomes and land a haul over the audited cast seam.
```

**Mining standalone — `python3 -m games.mining`** (`games/mining/cli.py`) is a
dig / descend / sell loop over the audited mining seam. Commands: `mine`,
`harvest`, `sell`, `buy`, `repair`, `descend`, `ascend`, `build`, `vault`,
`skill`, `status` (alias `inv`), `help`, `quit`.

**Fishing standalone — `python3 -m games.fishing`** (`games/fishing/cli.py`)
casts a line across biomes over the audited cast seam. Commands: `cast`,
`spot <id>`, `spots`, `status` (alias `haul`), `help`, `quit`.

Each standalone is a pure-domain session driving the rung-2 audited workflow
seams (`services/mining_workflow.py` / `services/fishing_workflow.py`) through an
in-memory audit sink (`services/audit.py`) — every price, cost, weight and gate
is read verbatim from the seam/core, so these loops invent no economy number.
The remaining balance-tuning, save/load persistence and host-hub items are
tracked as owner-facing entries in [control/outbox.md](control/outbox.md).

## Where to start

1. The unified bus: `control/inbox.md` (orders to this seat) + `control/status.md` (this
   seat's heartbeat) — fleet protocol spec: [control/README.md](control/README.md).
2. Your founding plans (their methodology and hard-rails sections are binding).
3. [docs/lanes.md](docs/lanes.md) — the archived gen-1 cohabitation contract; read it as
   history for how `games/**` came together, not as a live lane boundary.
