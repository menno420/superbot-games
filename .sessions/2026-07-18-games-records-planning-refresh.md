# 2026-07-18 · games-records-planning-refresh — docs: refresh current-state truth-stamp + post-freeze forward plan after the 2026-07-19 decision sweep

> **Status:** 🚧 `in-progress`
>
> 📊 Model: opus-4.8 · high · docs/records

⚑ Self-initiated: records + planning refresh (owner-authorized — "if you run
out of executable work start planning"; the concrete owner-input backlog is now
dry). Docs-only (+ this card + claim); no code, and `control/inbox.md` is
untouched. Executed at branch base `07c0ad3` (#176, main HEAD).

**Why this slice.** Today's (2026-07-19) decision sweep drained the concrete
executable backlog: ORDER 011 was recorded (#170) and all eight owner-input
decisions the 2026-07-18 deep hunt queued in `NEXT-TASKS.md` were resolved and
merged to main, plus the reconcile-race card-guard fix landed. The living
ledger (`docs/current-state.md`) still carries a truth-stamp from **before**
today's sweep, and the owner-input queue in `NEXT-TASKS.md` is fully resolved
but not yet closed out with a forward plan. A records slice re-stamps the truth
and — per the owner's "start planning" direction — lays down the
genuinely-open next steps today's work surfaced, so the next session boots onto
a current ledger and a triaged forward plan rather than a dry backlog.

**What this slice records (all verified on main before citing).**

- **ORDER 011** recorded via **#170** (`1039e8a`, control/inbox + docs).
- **Eight owner-input decisions resolved** across five PRs, all on main:
  **#171** (`99cbc59`) — `build_structure` reads level from state (decision #3,
  already landed by #167 `ba78870` and re-verified) + complete-coin-ledger
  audit rows for build/vault (decision #8); **#172** (`11e1451`) — mining CLI
  "Quantity must be a number" diagnostic with catalog-aware disambiguation
  (decision #6); **#173** (`729694c`) — consume gear on break at durability 0
  (decision #2); **#174** (`e0b8123`) — flatten exploration ore-scaling onto
  the live faucet curve (decision #1) + fishing V043 curve canonical for fish
  valuation (decision #7); **#175** (`10d7aa3`) — case-fold dnd option ids
  (decision #4) + display-name→id resolver for fishing species (decision #5).
- **Reconcile-race card-guard fix** via **#176** (`07c0ad3`) — the provenance-
  stamp disarm made tolerant so a GitHub-native auto-merge landing inside the
  TOCTOU window no longer fails the reconcile job.

Suite at this HEAD: **868 passed** (`python3 -m pytest -q`) — up from the
849 passed / 1 xfailed the 2026-07-18 overnight loop recorded, as the eight
decision PRs added pins and converted the dnd case-fold xfail to a passing
assertion. The refresh updates the ledger's truth-stamp + adds a today's-work
line, and closes out the `NEXT-TASKS.md` owner-input queue with a CLEARED note
plus a forward-plan subsection.

Scope: `docs/current-state.md` (truth-stamp + today's-work line),
`docs/NEXT-TASKS.md` (queue-CLEARED note + "Next session" forward plan),
`control/claims/2026-07-18-games-records-planning-refresh.md`, and this card.
The standing wind-down facts are preserved intact: routines remain **un-armed**
pending the owner's per-seat go, the auto-merge apparatus stays **live** (green
agent PRs auto-merge — NOT human-gated), and the Projects EAP read-only cutover
is 2026-07-21.

## 💡 Session idea

⚑ Self-initiated. A backlog going dry is itself a signal worth stamping, not a
silent stop. The eight decisions this queue held were the balance/design/
contract residue the build slices deliberately deferred; resolving them all in
one sweep means the owner-facing decision list is now empty — but "empty" is
ambiguous between "nothing left to do" and "the remaining work is latent behind
a seam that doesn't exist yet." Two of today's fixes (the flattened exploration
curve #1, the canonical fish valuation #7) are LATENT by construction: each is
correct but unreachable until a host rung wires the exploration engine onto a
live command path, or routes a caught fish into a shared `MiningState`
inventory. The recipe for the next adopter: when a decision sweep empties the
queue, don't leave the ledger reading "backlog dry" — HARVEST the latent
seams the fixes now wait behind into a forward-plan subsection, so the next
session sees the real shape of the remaining work (owner-triage seams, not
agent slices) instead of an empty list it might misread as "done."

## ⟲ Previous-session review

Target: games PR **#176** (`07c0ad3`, "ci(card-guard): tolerate auto-merge
landing before the provenance stamp (port idle #142)") — this branch's base and
main's current HEAD (`git fetch origin main && git reset --hard origin/main` →
`07c0ad3`, confirmed; `git log --oneline` lists #170–#176 as the seven most
recent squashes). Its load-bearing claim — the reconcile job's provenance-stamp
branch disarmed GitHub-native auto-merge on a `fatal=True` helper, so an
auto-merge landing inside the read→disarm TOCTOU window errored
`GraphQL: Can't disable auto-merge for this pull request` and failed the whole
reconcile job (benign, since provenance stamping is a survey aid not a merge
gate), and the fix makes ONLY that disarm `fatal=False` + re-checks the PR's
merged state and exits 0 either way — is consistent with this session's read of
`.github/workflows/automerge-card-guard.yml` and the #176 card/claim already on
main. The eight decision PRs #171–#175 are likewise verified on main by
`git log` (SHAs cited above). No code touched this session; this is a
docs/records slice, so the review is a citation-integrity check, not a
regression re-audit. Green baseline this HEAD: **868 passed** (re-run this
session before any edit).
