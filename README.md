# superbot-games

Shared home of SuperBot's **game plugins**. Two autonomous Projects live here, each owning
a lane (contract: [docs/lanes.md](docs/lanes.md)):

- **game-mining** — the mining domain end-to-end: the deep-systems port of superbot's
  mining engine as a pure-domain plugin package, then grid encounters and the shared
  encounter engine. Brief: [docs/founding-plan-mining.md](docs/founding-plan-mining.md).
- **game-exploration** — the federated exploration world and the D&D story game: a
  deterministic quest/encounter engine, the survival overlay, and the AI-Dungeon-Master
  layer (bounded menus, never state authority). Brief:
  [docs/founding-plan-exploration.md](docs/founding-plan-exploration.md).

Games ship as **plugin packages** that the rebuilt bot (`menno420/superbot-next`) consumes
via its manifest/plugin contract. That contract is in flight there (superbot-next's inbox
ORDER 002); until it lands, all work here stays plugin-side — pure-domain packages built
against the old superbot code as oracle, with the host-facing seams left open.

This repo is deliberately also an **experiment in multi-Project cohabitation**: two
autonomous Projects sharing one repo and one substrate-kit memory, coordinated by lanes
and per-Project control files. What works (and what collides) here informs how the wider
fleet shares repos.

## Where to start

1. Your inbox: `control/inbox-mining.md` or `control/inbox-exploration.md` — fleet
   protocol spec: [control/README.md](control/README.md).
2. Your founding plan (its methodology and hard-rails sections are binding).
3. [docs/lanes.md](docs/lanes.md) — which paths are yours, which are claim-first
   (binding on both Projects).
