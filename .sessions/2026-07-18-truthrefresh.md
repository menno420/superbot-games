# 2026-07-18 · truthrefresh — docs: truth-refresh current-state (tonight's 6 PRs) + queue owner-input decisions

> **Status:** `complete`
>
> 📊 Model: Claude Opus 4.x · high · docs/records

⚑ Self-initiated: truthful-records slice (owner night order 2026-07-18 — land
small self-initiated slices on green via auto-merge). This is the records slice
that follows tonight's six-PR improvement loop: refresh the living ledger so it
tells the truth about what landed, and queue the owner-input decisions the deep
hunt surfaced for the owner's morning review. Docs-only (+ this card); no code,
and `control/inbox.md` is untouched. Executed at branch base `d85227d` (#163,
main HEAD).

**What this slice records (all verified on main before citing).** Six PRs
landed 2026-07-17 → 18 under the owner's overnight forward-work order, each a
contained, tested, independently-landable slice merged on green via the live
auto-merge apparatus:

- **Three real bug fixes.** #158 (`0a00733`) made the standalone mining CLI's
  item/branch/structure tokens case-insensitive (`sell Iron` / `buy Torch` /
  `skill Mining` had silently no-op'd); #159 (`b0a9cfe`) made
  `energy.seconds_until` return `math.inf` for an unreachable target instead of
  a misleading `0`; #163 (`d85227d`) fixed a broken-tool re-announce bug in
  `services/mining_workflow.py::_apply_wear` (a broken tool was re-emitted in
  `broke` on every subsequent `mine` / `explore` / `duel`, spamming the break
  message — now announced once, on the tick it breaks).
- **Coverage + hardening.** #160 (`b205c79`) pinned a cross-CLI
  case-normalisation invariant and, in doing so, fixed a latent exploration CLI
  bug (its `offer` / `act` verbs didn't lowercase) and xfail'd the dnd off-menu
  case-fold gap; #161 (`bcaf032`) pinned fishing CLI non-integer-qty +
  multi-word-display-name handling (no bug); #162 (`30d56b8`) pinned mining CLI
  negative / non-int-qty rejection across sell / build / skill (no bug).

Suite at this HEAD: **849 passed, 1 xfailed** (`python3 -m pytest -q`) — up from
827 as the six slices added coverage. The refresh updates the ledger's
`In flight` section and stability-baseline suite count, and queues six
owner-input decisions the deep hunt surfaced into `docs/NEXT-TASKS.md`.

Scope: `docs/current-state.md` (In-flight record + baseline count),
`docs/NEXT-TASKS.md` (a new `## Owner-input decisions queued (2026-07-18
overnight loop)` section), `control/claims/claude-truthrefresh-0718.md`, and
this card. The standing wind-down facts are preserved intact: the auto-merge
apparatus stays **live** (green agent PRs auto-merge — NOT human-gated),
routines remain **un-armed** pending the owner's per-seat go (this was a
one-night forward-work resume by owner order, not a re-arming or a cancellation
of the wind-down), and the Projects EAP read-only cutover is 2026-07-21.

## 💡 Session idea

⚑ Self-initiated. The six owner-input decisions this slice queues are the
BALANCE- and CONTRACT-judgment residue of tonight's deep hunt — findings that
are real but not a clear no-balance correctness fix, so they are owner calls,
not agent slices. Two of them (exploration `_scale_amount` still on the retired
runaway ore curve; broken gear staying equipped and fully effective at
durability 0) are the deferred findings the #163 card already logged as
owner-input backlog; queuing them in `NEXT-TASKS.md` moves them from a single
card's tail into the durable, owner-facing decision list where the morning
review actually looks. The broader idea: a records slice should not just
re-stamp the ledger — it should HARVEST the judgment-call findings that the
build slices deliberately deferred into the one place the owner triages, so a
deferred decision never dies in a merged card's footnotes.

## ⟲ Previous-session review

Target: games PR #163 (`d85227d`, "Fix: a broken tool is announced once, not on
every dig after it breaks") — this branch's base and main's current HEAD (`git
fetch origin main && git reset --hard origin/main` → `d85227d`, confirmed; the
merge commit is titled `…(#163)` and `git log --oneline` lists #158–#163 as the
six most recent squashes). Its load-bearing claim — the mining WORKFLOW seam's
`_apply_wear` re-reported an already-broken tool (durability already `0`, never
cleared by the seam) in `broke` on every subsequent wearing action, so a host
rendering `broke` would spam "your iron pickaxe broke!" on every dig after the
first, and the fix skips an already-broken (`durability <= 0`) slot so a break
is announced exactly once — re-checks TRUE from this session's own reading:
`services/mining_workflow.py::_apply_wear` skips `durability <= 0` slots, the
regression test `test_mine_reports_break_only_on_the_tick_it_breaks` is present
in `services/tests/test_mining_workflow.py`, the `services/tests` floor reads
217, and `docs/balance.md`'s Test-suite-floors section carries the matching
row. No balance/economy number was touched. Green baseline this HEAD:
`849 passed, 1 xfailed` (re-run this session before any edit).

## ✅ Landed (PR #164)

Shipped in PR [#164](https://github.com/menno420/superbot-games/pull/164)
(`claude/truthrefresh-0718`). Two documentation surfaces refreshed, plus this
card + claim:

- `docs/current-state.md` — new `OVERNIGHT FORWARD-WORK LOOP` banner at the top
  of "In flight" records the six-PR loop (#158–#163) with per-PR SHAs and the
  three-real-fixes / three-coverage split, and updates the stability-baseline
  suite count to `849 passed, 1 xfailed`. The standing wind-down facts are kept
  intact (auto-merge apparatus LIVE — not human-gated; routines un-armed pending
  the owner's per-seat go; one-night forward-work resume by owner order, not a
  cancellation; Projects EAP read-only 2026-07-21). Status badge untouched in
  the first ~12 lines.
- `docs/NEXT-TASKS.md` — new `## Owner-input decisions queued (2026-07-18
  overnight loop)` section listing the six owner-input decisions the deep hunt
  surfaced, each a crisp question with its file pointer and tradeoff, none
  duplicating the existing "Owner decisions to unblock" entries.

Docs-only; no code, `control/inbox.md` untouched. **Suite green:** `python3 -m
pytest -q` = `849 passed, 1 xfailed`. **`bootstrap.py check --strict`** pre-flip
= exit 1 SOLELY on this card's designed born-red hold (`HOLD (by design): …
declares an in-progress Status`); this flip-to-complete commit clears the hold
and the gate goes green so the live auto-merge apparatus lands the squash.
