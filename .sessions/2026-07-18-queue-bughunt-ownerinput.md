# 2026-07-18 · queue-bughunt-ownerinput — docs: queue two fresh-angle bug-hunt owner-input findings for morning review

> **Status:** `in-progress`
>
> 📊 Model: Claude Opus 4.x · high · docs/records

⚑ Self-initiated: records slice. Tonight's fresh-angle bug-hunt (economy-
conservation + audit-log angles) surfaced two findings that are LATENT /
design-level — they need the owner's balance / design judgment, not an
autonomous fix. This slice records them in `docs/NEXT-TASKS.md` as two new
clearly-marked entries in the existing `## Owner-input decisions queued
(2026-07-18 overnight loop)` section, so a deferred judgment call lands in the
one place the owner triages rather than dying in a card footnote. Docs-only
(+ this card); no code, no balance value, `control/inbox.md` untouched. Executed
at branch base `ba78870` (#167, main HEAD).

**What this slice records (all verified on main before citing).** Two findings,
appended as entries 7–8 without touching the 6 existing queued decisions:

- **[balance] Cross-game fish valuation gap (latent, unreachable today).**
  `games/mining/core/items.py::register_fish_species` (~lines 282–304) folds
  each fish into the mining market as a RESOURCE worth `max(1, size_rank)`
  (1–4 coins), while `games/fishing/core/economy.py` (~line 35) sells the same
  species on the V043 curve at 8 / 13 / 27 / 80 — a ~20× gap. Unreachable today
  (`register_fish_species` is called only from a test; no seam routes a caught
  fish into `MiningState.inventory`), but a future shared-inventory host rung
  would sell the same fish at two prices. Owner decides which valuation is
  canonical.
- **[design] `economy_audit_log` is not a complete coin ledger.** `sell` /
  `buy` / `repair` audit `target="coins"`, but `build_structure` /
  `vault_upgrade` audit `structure:<key>` / `vault` with LEVELS — so a wallet
  reconstructed purely from the log under-counts build / vault coin sinks (a
  500-coin vault upgrade is invisible to a log-derived balance). The live wallet
  is correct; arguably one-primary-target-per-op is by-design. Owner decides
  whether the log is meant to be a complete coin ledger.

Suite unchanged at this HEAD: **852 passed, 1 xfailed** (`python3 -m pytest -q`)
— docs-only change, no test delta, no floor bump.

Scope: `docs/NEXT-TASKS.md` (two new entries + a short note in the existing
Owner-input-decisions section) and this card. The standing wind-down facts are
preserved intact: the auto-merge apparatus stays **live** (green agent PRs
auto-merge — NOT human-gated), routines remain **un-armed** pending the owner's
per-seat go, and the Projects EAP read-only cutover is 2026-07-21.

## 💡 Session idea

⚑ Self-initiated. A fresh-angle bug-hunt run on a DIFFERENT axis than the
build loop (economy conservation: does every coin sink leave a trace? and: is
the audit log a ledger you can re-derive a wallet from?) finds a different
finding class than a diff-hardening sweep does — here, two latent gaps that only
bite once a future host rung wires the games onto a shared inventory / a
log-derived ledger. The broader idea: the value of a records slice after a hunt
is HARVESTING the judgment-call residue into the owner's durable decision list;
an auto-fixable find ships as a PR, but a balance / design call must be queued
where the morning review looks, or it dies in a merged card's footnotes.

## ⟲ Previous-session review

Tonight's fresh-angle hunt sits behind three squashes already on main HEAD
(`git fetch origin main && git reset --hard origin/main` → `ba78870`, confirmed;
`git log --oneline` lists them as the three most recent): **#165** (`8bd5da4`,
"docs: correct stale human-gated merge claim in NEXT-TASKS") corrected a
doc-truth drift; **#166** (`1745846`, "fix: restore hashable invariant on quest
Objective/QuestTemplate") restored a hashable invariant; **#167** (`ba78870`,
"fix(mining): build_structure derives its level from state, not the caller's
claim") closed the `build_structure` caller-level exploit. #166 and #167 are the
auto-fixable finds of tonight's hunt; the two findings this slice queues are the
latent / design-level residue that is NOT auto-fixable. No balance / economy
number was touched by any of them. Green baseline this HEAD: `852 passed,
1 xfailed` (re-run this session before any edit).

## ✅ Landed
