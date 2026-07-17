# 2026-07-17 · current-state truth — docs: correct docs/current-state.md merge doctrine (auto-merge, not human-gated) (docs-only)

> **Status:** `in-progress`
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
code. Only `docs/current-state.md` plus this card and its claim; the Status
badge stays within the first ~12 lines untouched.

## ✅ Close-out — Verification

_(pending flip-to-complete)_
