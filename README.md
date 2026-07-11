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
via its manifest/plugin contract. That contract is in flight there (superbot-next's inbox
ORDER 002); until it lands, all work here stays plugin-side — pure-domain packages built
against the old superbot code as oracle, with the host-facing seams left open.

Player-visible nouns (names, flavor, emoji) stay isolated in **data, not code**, so the
fleet's core/skin split can reach the world games later — build the mechanics against
neutral identifiers and keep the theme in swappable data (theme-readiness, directive
Q-0267).

## Where to start

1. The unified bus: `control/inbox.md` (orders to this seat) + `control/status.md` (this
   seat's heartbeat) — fleet protocol spec: [control/README.md](control/README.md).
2. Your founding plans (their methodology and hard-rails sections are binding).
3. [docs/lanes.md](docs/lanes.md) — the archived gen-1 cohabitation contract; read it as
   history for how `games/**` came together, not as a live lane boundary.
