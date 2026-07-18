# 2026-07-18 · unstale-human-gated — docs: correct stale human-gated merge claim in NEXT-TASKS

> **Status:** `complete`
>
> 📊 Model: Claude Opus 4.x · high · docs/records

⚑ Order-driven: coordinator-ordered docs-truth fix (slice 1 of a queued
docs-truth queue). `docs/NEXT-TASKS.md`'s `## Context` section still carried a
stale, false claim — "Merges are **human-gated**: open a PR ready and stop; the
owner reviews and lands it." — which directly contradicts the living ledger.
`docs/current-state.md` records the CI auto-merge apparatus as **live** (a green
agent PR lands itself via `.github/workflows/auto-merge-enabler.yml` the moment
the required `substrate-gate` check passes, no owner click), and the standing
owner order is that **no doc may claim merges are human-gated**. This slice
corrects only that one false sentence to the truth. Docs-only (+ this card); no
code, and `control/inbox.md` is untouched.

**What this slice records (verified against `current-state.md` before citing).**
The `## Context` section's closing sentence is replaced with the truthful
version: merges are **not** human-gated — a green `claude/*` PR auto-lands via
the live auto-merge apparatus once CI (`substrate-gate`) passes, and the owner
reviews already-merged PRs asynchronously. This is consistent with the "In
flight" and "Stability baseline" records in `current-state.md` (#67 `dd867c8`
installed the auto-merge-enabler; the wind-down banner explicitly notes "Merges,
however, are **NOT human-gated**: the CI auto-merge apparatus is still
**live**"). The edit is minimal: the surrounding `## Context` narrative (content
depth, inventory unification, superbot-next wiring; the wound-down autonomy
apparatus) is left intact.

Scope: `docs/NEXT-TASKS.md` (one sentence in `## Context`) and this card.

## 💡 Session idea

⚑ Order-driven. A stale line that flatly contradicts the living ledger is worse
than a missing one — it hands the next reader a false operating rule ("open a PR
and stop") that the standing owner order has already retired. The durable idea:
truth-refresh slices should sweep the reference docs (`NEXT-TASKS.md`) for
operating-rule claims that drift out of sync with the ledger (`current-state.md`)
whenever the ledger is the one that moved, so a reference doc never silently
teaches a retired workflow.

## ⟲ Previous-session review

Predecessor: the 2026-07-18 truth-refresh session (card
`.sessions/2026-07-18-truthrefresh.md`, PR #164) which landed the overnight
forward-work loop's records slice on top of PRs #158–#164 — refreshing
`current-state.md`'s "In flight" banner and queuing six owner-input decisions in
`NEXT-TASKS.md`. That refresh re-stamped the ledger truth (auto-merge LIVE, not
human-gated) but did not sweep `NEXT-TASKS.md`'s own `## Context` section, which
still carried the contradicting human-gated line this slice now flags and fixes.

## ✅ Landed (PR #165)

Shipped in PR [#165](https://github.com/menno420/superbot-games/pull/165)
(`claude/docs-unstale-human-gated`). One documentation surface corrected, plus
this card:

- `docs/NEXT-TASKS.md` — the `## Context` section's stale closing sentence
  ("Merges are **human-gated**: open a PR ready and stop; the owner reviews and
  lands it.") is replaced with the truth: merges are **not** human-gated — a
  green `claude/*` PR auto-lands via the live auto-merge apparatus once CI
  (`substrate-gate`) passes, and the owner reviews already-merged PRs
  asynchronously. Consistent with `docs/current-state.md` (auto-merge apparatus
  LIVE — not human-gated; #67 `dd867c8`). The surrounding `## Context` narrative
  is left intact.

Docs-only; no code, `control/inbox.md` untouched. **Suite green:** `python3 -m
pytest -q` = `849 passed, 1 xfailed`; floors pass. **`bootstrap.py check
--strict`** pre-flip = exit 1 SOLELY on this card's designed born-red hold
(`HOLD (by design): … declares an in-progress Status`); this flip-to-complete
commit clears the hold so the live auto-merge apparatus lands the squash on
green.
