# 2026-07-17 · current-state truth — docs: correct docs/current-state.md merge doctrine (auto-merge, not human-gated) (docs-only)

> **Status:** `complete`
>
> 📊 Model: Claude Opus 4.x · high · docs/records

Documentation accuracy fix, executed at branch base `cf825d9` (#156). The
living ledger `docs/current-state.md` carried an internally contradictory
record of how agent PRs land. Its "Stability baseline" section already
states the truth — the CI **auto-merge-enabler** (#67 `dd867c8`) supersedes
the post-#40 manual-merge doctrine and lands PRs on green — but the newer
"In flight" FRESH-START CLEANUP banner claimed the opposite: "Merge doctrine
is now **human-gated** — an agent opens a PR ready and STOPS; the merge is
landed server-side / by the owner, never by the agent on CI status alone."
That is factually wrong: `.github/workflows/auto-merge-enabler.yml` is LIVE
(arms GitHub-native auto-merge at PR open, gated on the required
`substrate-gate` check) and auto-landed green PRs — it landed #156 today.
The banner even listed "the auto-merge apparatus" among the things "standing
down," conflating the still-live CI enabler with the genuinely-un-armed
session wake routines.

Scope (deliberately narrow): ONE passage in `docs/current-state.md` — the
"Autonomy is being wound down" bullet in the In-flight banner — rewritten to
state the truth (green agent PRs auto-merge via
`.github/workflows/auto-merge-enabler.yml`, required check `substrate-gate`,
no owner click; it landed #156). All other facts left intact: autonomy
winding down, `control/` bus + heartbeats + wake routines standing down,
routines still **un-armed**, Projects EAP going read-only 2026-07-21. No
code. The Status badge stays within the first ~12 lines untouched.

Per owner order (2026-07-17) this slice ALSO PLANNED a `## CORRECTION`
append to the END of `control/inbox.md` — append-only, no existing text
rewritten — retracting the same "human-gated" language from the inbox
RETIREMENT NOTICE and recording that auto-merge stays ON (required check
`substrate-gate`) and the owner never reviews an unmerged PR. That inbox
append was **NOT included** in this PR: writes to `control/inbox.md` were
blocked by the auto-mode permission classifier (being handled separately).
So the slice as SHIPPED touches `docs/current-state.md` + this card only.
Still no code.

## ✅ Close-out — Verification

Shipped in PR [#157](https://github.com/menno420/superbot-games/pull/157)
(`claude/current-state-truth-0717`). ONE documentation surface corrected,
removing the false "human-gated" claim:

- `docs/current-state.md` — the "Autonomy is being wound down" In-flight
  bullet rewritten: merges are NOT human-gated; a green agent PR merges
  itself via `.github/workflows/auto-merge-enabler.yml` (required check
  `substrate-gate`, landed #156), aligning the banner with the file's own
  "Stability baseline" note (#67 `dd867c8`). Every other fact intact.

The planned `control/inbox.md` `## CORRECTION` append (retracting the same
"human-gated" language from the inbox RETIREMENT NOTICE) was **NOT
included** in this PR — writes to `control/inbox.md` were blocked by the
auto-mode permission classifier. That inbox correction is being handled
separately and is intentionally left out of this commit.

**Suite — green.** `python3 -m pytest -q` = **827 passed** (docs only; no
code). **`bootstrap.py check --strict`** pre-flip = exit 1 SOLELY on this
card's designed born-red hold (`HOLD (by design): … declares an
in-progress Status`); this flip-to-complete commit clears the hold and
`check --strict` then exits 0.
