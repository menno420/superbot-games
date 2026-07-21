# superbot-games — project closeout

> **Status:** `reference`
>
> The single, plain-language wrap-up of the superbot-games seat at the end of
> its autonomous agent sessions. Written for two readers who know nothing about
> those sessions: the non-coder owner, and a fresh future agent session picking
> this repo back up. Source code and merged git history always win over this
> file; every claim below is cited to a PR/commit or a file you can open.

## What this project is & what was accomplished

**superbot-games** is the shared home of SuperBot's game plugins — one seat owns
the whole game world: **mining**, **fishing**, the **D&D** story game, and
**exploration**, plus the shared world systems they draw on (inventory, tools,
locations, resources, encounters). Everything lives under `games/**`. The games
are pure-domain, stdlib-only Python packages: each game's outcomes come from a
deterministic, seedable core, and a thin text CLI drives it. Nothing here talks
to Discord or a live bot directly — these packages are built to be consumed
later by the rebuilt bot (`menno420/superbot-next`) through its plugin contract.

What the autonomous agent sessions shipped, with verified citations (each PR
number confirmed against the merge-commit subject in `git log` at this repo's
HEAD):

- **Exploration engine went live on a real command.** The deterministic
  quest/encounter engine was wired onto a live `explore` verb so a player can
  actually take a bounded quest, resolve encounters, and bank the reward —
  **#178** (`e0cbbc7`, *feat(mining): wire the exploration engine onto a live
  `explore` verb*).
- **Fishing → mining inventory bridge, built in three gated slices (currently
  OFF by design).** A caught fish can be valued and sold into the mining economy
  at the canonical price, but the whole path ships **disabled by default** and
  only turns on when an env var is set (see the Continuation section):
  - **#180** (`9d8b22a`, *feat(inventory): config-gated fishing→mining bridge
    service seam (Option B, slice 1)*) — the service seam, gated off.
  - **#181** (`4afb915`, *feat(inventory): wire gated fishing→mining exchange
    onto an audited verb (Option B, slice 2)*) — the exchange on an audited verb.
  - **#182** (`9326694`, *feat(inventory): CLI surface + read-only value preview
    for the fishing→mining bridge (Option B, slice 3)*) — the CLI surface + a
    read-only value preview.
  - Design/planning that framed the bridge first: **#179** (`cb1b546`, *docs:
    shared cross-game inventory — design/planning doc (fishing → mining
    market)*), captured in
    [design-shared-cross-game-inventory.md](design-shared-cross-game-inventory.md).
- **Owner-input decisions resolved and merged (the #171–#175 wave).** A deep
  bug-and-design hunt surfaced eight owner decisions; the fixes landed as:
  - **#171** (`99cbc59`, *fix(mining): build_structure derives level from state
    + complete coin ledger in economy_audit_log*).
  - **#172** (`11e1451`, *feat(mining-cli): add 'Quantity must be a number'
    diagnostic*).
  - **#173** (`729694c`, *fix(mining): consume gear on break (durability 0)*).
  - **#174** (`e0b8123`, *balance(mining): flatten exploration ore-scaling +
    make fishing V043 curve canonical for fish valuation*) — this is the ruling
    that makes **V043** the one canonical fish-valuation curve the bridge reuses.
  - **#175** (`10d7aa3`, *feat(cli): case-fold dnd option ids + resolve
    multi-word display names to ids*).
- **Merge-on-green landing is installed.** Green agent PRs merge themselves:
  `.github/workflows/auto-merge-enabler.yml` arms GitHub-native auto-merge at PR
  open and lands the squash the moment the required `substrate-gate` check
  passes — no manual click on CI. (This install predates this repo's shallow
  clone window; the ledger records it as PR #67, but the authoritative evidence
  is the workflow file itself, present at HEAD.)
- **Workflow kit upgraded to the current line.** substrate-kit was upgraded
  v1.17.0 → **v1.20.1** — **#183** (`a9a7dcc`, *chore(kit): upgrade
  substrate-kit v1.17.0 -> v1.20.1 (distribution only)*), this repo's HEAD — with
  a follow-up that turned its red gate green: **#184** (`63f880d`, *control:
  ORDER 012 — fix red substrate-gate on kit v1.20.1 upgrade PR #183*).

## Current true state

Verified live at close, at HEAD **`a9a7dcc`**:

- **Test suite: 940 passed** — `python3 -m pytest -q`.
- **`python3 bootstrap.py check --strict` passes** (exit 0; only advisory
  claims-format / model-line warnings remain, none exit-affecting).
- **Zero open PRs / all shipped work merged.** HEAD `a9a7dcc` is PR #183; the
  bridge, exploration-engine, and decision-wave PRs above are all on `main`.
- The inventory bridge is **built but OFF** — it does nothing until the enabler
  env var is set (next section).

## Continuation — open threads (priority order)

These are the only live threads at close. Each has exact resume steps.

### 1. Flip the fishing → mining inventory bridge ON (owner steer + one env var)

The bridge (slices 1–3, PRs #180/#181/#182) is fully built and tested but
**disabled by default**. It reads its flag live from the environment on every
call.

- **Exact enabler:** environment variable **`GAMES_INVENTORY_BRIDGE_ENABLED`**
  (confirmed in code: `services/inventory_bridge.py`, `BRIDGE_ENABLED_ENV =
  "GAMES_INVENTORY_BRIDGE_ENABLED"`, read by `bridge_enabled()`). Unset or any
  value outside `{1, true, yes, on}` (case-insensitive) ⇒ bridge stays OFF.
- **To turn it on for a run:**
  ```
  GAMES_INVENTORY_BRIDGE_ENABLED=1 python3 -m games.fishing
  ```
- **The rate ruling to respect:** the exchange is **1:1 at the shared V043
  price** (owner decisions 4 + 5). Fish are valued on the canonical **V043**
  fishing sell curve — made canonical by **#174** — and sold into mining coins
  at parity, one-directionally (fishing → mining). No currency/XP conversion, no
  second rate. That ruling is documented in `services/inventory_bridge.py` and
  in [design-shared-cross-game-inventory.md](design-shared-cross-game-inventory.md).
- **Still-open product forks before a wide flip** (owner calls, captured in the
  design doc §6/§next): is a fish sellable-at-all, and is 1:1 the intended
  long-run rate.

### 2. Bridge slice 4 — bidirectional / shared-inventory-core fork (unbuilt BY DESIGN)

Slices 1–3 deliberately shipped **Option B** (a one-directional bridge between
two separate per-game holds), designed so it *can* graduate to **Option A** (one
unified shared inventory core both games depend on). **Slice 4 was intentionally
not built** — it is the bidirectional flow and/or the promotion of the bridge
toward a shared inventory core, and it waits on an explicit owner product call
(one unified hold vs. two bridged holds; one-directional vs. bidirectional).

- **Resume steps:** get the owner's product call on the two forks above; then
  read [design-shared-cross-game-inventory.md](design-shared-cross-game-inventory.md)
  (Option A vs. Option B, §"OWNER PRODUCT CALL" notes) and extend the existing
  `services/inventory_bridge.py` seam — do **not** rebuild it. Keep the new
  direction gated behind the same env flag until the owner signs off.

> **Fleet context.** Fleet-wide and field-parity threads (the shared inventory /
> economy story across sibling repos) live in the MASTER closeout —
> superbot-mineverse, https://github.com/menno420/superbot-mineverse
> (`docs/PROJECT-CLOSEOUT.md`). Read that for anything spanning more than this
> repo.

## Owner walkthrough

Plain-language, no coding needed.

**What this repo is.** Four playable text games (mining, fishing, D&D,
exploration) plus the shared systems behind them. They run in a terminal today
as pure text sessions; the "hook it into the live bot" step is a later rung.

**How to run the games** (from the repo root, `superbot-games/`):

- **The hub** — lists every game and launches the one you pick:
  ```
  python3 -m games
  ```
  (entry point: `games/__main__.py`. Type `list`, then `play mining` /
  `play 1`, `help`, `quit`.)
- **Play one game directly:**
  ```
  python3 -m games.mining
  python3 -m games.fishing
  python3 -m games.dnd
  python3 -m games.exploration
  ```
  (entry points: `games/mining/cli.py`, `games/fishing/cli.py`,
  `games/dnd/cli.py`, `games/exploration/cli.py`.)
- **Check everything still works** (should print `940 passed`):
  ```
  python3 -m pytest -q
  ```

**Key docs** (all under `docs/`, links open the file):

- [current-state.md](current-state.md) — the living status ledger; the single
  "what's true right now" page.
- [NEXT-TASKS.md](NEXT-TASKS.md) — the forward-work backlog for the next builder.
- [decisions.md](decisions.md) — the numbered decision log (D-00xx).
- [design-shared-cross-game-inventory.md](design-shared-cross-game-inventory.md)
  — the inventory-bridge design (the thread most likely to resume).
- Root `README.md` — how to play each game, in the owner's own words.

**Sibling closeouts (plain URLs):**

- superbot-idle — https://github.com/menno420/superbot-idle
  (`docs/PROJECT-CLOSEOUT.md`).
- superbot-mineverse — https://github.com/menno420/superbot-mineverse
  (`docs/PROJECT-CLOSEOUT.md`) — **the MASTER** fleet-wide closeout.

**Owner checklist — quickest first:**

- [ ] **Close the ORDER 012 status line** in `control/inbox.md` — it still reads
      `status: new`, but its done-when is already met (PR #183's substrate-gate
      went green and auto-merge landed the v1.20.1 upgrade on main at HEAD
      `a9a7dcc`, via #184). Flip it to `status: done`.
- [ ] Decide the two bridge product forks (fish sellable-at-all? 1:1 the right
      rate?) — thread #1 above.
- [ ] Decide the slice-4 fork (one unified hold vs. two bridged holds;
      one-directional vs. bidirectional) — thread #2 above.
- [ ] When ready, flip the bridge on with
      `GAMES_INVENTORY_BRIDGE_ENABLED=1` and try
      `GAMES_INVENTORY_BRIDGE_ENABLED=1 python3 -m games.fishing`.

## Working this repo with a fresh session

For a future agent session.

**Boot route (in order):** `CONSTITUTION.md` (the working agreement) →
`HANDOFF.md` at repo root *if present* (untracked, regenerated at boot; read it
before re-deriving history from git) → [current-state.md](current-state.md) (the
living ledger). `docs/AGENT_ORIENTATION.md` is the task reading-router; it also
lists `docs/CAPABILITIES.md` (verified can/cannot ledger) — check that before
declaring any wall.

**Verify commands** (run both before every push):

```
python3 -m pytest -q            # expect 940 passed at this HEAD
python3 bootstrap.py check --strict   # expect exit 0
```

**How PRs land here:**

- Branch as `claude/*` (an auto-merge-allowed prefix in
  `substrate.config.json` → `automerge.branch_patterns`).
- **First commit** must be a born-red `.sessions/<date>-<slug>.md` card with
  `> **Status:** ` `in-progress`. The host card-guard
  (`.github/workflows/automerge-card-guard.yml`) DISARMS auto-merge while any
  in-progress/drafted card is in the diff — this holds the PR red on purpose.
- The card must carry four markers or the strict gate reds: a Status badge, a
  `💡` idea, a `📊 Model:` line (family-level model · effort · a valid PL-004
  task class — see `.sessions/README.md`), and a previous-session review.
- **Last commit** flips the card Status to `complete` — that releases the
  enabler, and on green `substrate-gate` the auto-merge-enabler lands the squash
  server-side.

**Gotchas (measured, not theoretical):**

- The **born-red substrate-gate HOLD is designed**, not a failure — a PR whose
  card is still `in-progress` is *supposed* to sit red until the flip.
- **A Bash `git` write may be refused by the harness on a given call** — treat
  that as a per-call, momentary condition (re-attempt on a fresh call), not a
  standing block. When it happens, land via the GitHub MCP `push_files` with raw
  file text instead of git.
- **MCP PR/CI reads can lag ~25 minutes** behind reality — cross-check the live
  PR/checks page before concluding a PR is red or unmerged.
