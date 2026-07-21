# 2026-07-21 · final-closeout — superbot-games project closeout

> **Status:** `in-progress`
>
> 📊 Model: opus-4.8 · medium · docs-only — superbot-games project closeout

Close-out session for the superbot-games seat at the end of its autonomous
agent sessions. Ship a single plain-language wrap-up doc
(`docs/PROJECT-CLOSEOUT.md`) written for two readers who know nothing about
these sessions — the non-coder owner and a fresh future session — then true up
the living ledger and retire this seat's terminal claims. No code changes; the
game packages and their 940-test suite are untouched.

## What happened

- **Wrote `docs/PROJECT-CLOSEOUT.md`** (badge `reference`): what shipped with
  verified PR/commit citations, the current true state, the open threads in
  priority order with exact resume steps, an owner walkthrough (how to run the
  games CLI + key docs), and a fresh-session boot guide. Every PR number was
  confirmed against its merge-commit subject in `git log` at HEAD `a9a7dcc`
  before writing — exploration engine live (#178 `e0cbbc7`); bridge slices 1–3
  gated OFF (#180 `9d8b22a` / #181 `4afb915` / #182 `9326694`) framed by design
  #179 (`cb1b546`); the #171–#175 owner-decision wave; kit v1.20.1 (#183
  `a9a7dcc` = HEAD) + gate-green follow-up #184 (`63f880d`).
- **Confirmed the bridge enabler from code, not the directive's guess:**
  `services/inventory_bridge.py` → `BRIDGE_ENABLED_ENV =
  "GAMES_INVENTORY_BRIDGE_ENABLED"`, default OFF, truthy set `{1,true,yes,on}`;
  the exchange is 1:1 at the canonical V043 price (owner decisions 4+5, V043 made
  canonical by #174).
- **Reachability:** added a pointer to the new doc near the top of
  `docs/current-state.md` and in `docs/AGENT_ORIENTATION.md` (both read-path
  roots) so `check --strict` does not red with a `[reachable]` orphan.
- **True-up:** added a 2026-07-21 close-out truth-stamp banner to
  `docs/current-state.md` (suite 868 → **940**; the engine/bridge/kit PRs since
  the 2026-07-19 sweep; zero open PRs) and retired this seat's nine terminal
  claim files under `control/claims/` (all PRs merged / zero-open).
- Verify: `python3 -m pytest -q` → **940 passed**; `python3 bootstrap.py check
  --strict` → **exit 0** with the new doc present (no `[reachable]`/badge red).

💡 Session idea: a closeout doc is only as durable as its reachability edge — an
orphaned wrap-up is invisible to the strict gate AND to the next session's boot
route. The kit could treat a `# <project> — project closeout` doc as a
first-class read-path root (auto-seeded into `readpath_docs` on creation), so a
project's final artifact can never silently orphan when a later regen rewrites
the ledger line that linked it.

⟲ Previous-session review: the prior card
(`2026-07-20-order-012-kit-games-dewall`, complete) landed the kit v1.20.1
substrate-gate green by reading the live CI log rather than the nudge summary —
a correct, robust fix. Its own close-out note (ORDER 012 done-when met: gate
green, auto-merge landed #183 at `a9a7dcc`) is confirmed still true at this
HEAD; the only residue is the stale `status: new` line for ORDER 012 in
`control/inbox.md`, surfaced to the owner as the first checklist item in the new
closeout doc.
