# 2026-07-15 · truth refresh — docs: re-stamp docs/current-state.md at HEAD (docs-only)

> **Status:** `in-progress`
>
> 📊 Model: fable-5 · high · docs-only

Truth-refresh slice, executed at branch base `446a84e` (#145). The
ledger's anchor sits at `4330559` (#134) with eleven squash merges
landed since (#135–#145, excluding the unmerged-number gap; enumerated
from `git log 4330559..446a84e`). Scope: re-verify every existing claim
in `docs/current-state.md` live at HEAD, correct what moved (kit
v1.15.0 → v1.17.0 via #141/#144; the host card-guard split out of the
kit enabler in #142; the `scripts/preflight.py` plant in #143; ORDER
009 EAP closeout #136–#140; ORDER 010 EAP extension #145; the #102
fleet-cleanup audit finally merged via #102's own head), then re-stamp
"In flight" with the new anchor + `date -u` date. No code changes.

Close-out. Groomed at HEAD `446a84e`: twelve new "Recently shipped"
bullets — #135 `34c5b98`, #102 `1c323c1`, #136 `ed2fabb`, #137
`e3930f1`, #138 `41e8a5b`, #139 `2969034`, #140 `717e36c`, #141
`688cbf1`, #142 `8c9c320`, #143 `d7595aa`, #144 `42a31c5`, #145
`446a84e` — every SHA verified against `git log 4330559..446a84e`
before writing (skeletons via `tools/stamp_scaffold.py` from the #134
anchor). Corrections to claims that had MOVED: kit engagement
v1.15.0 → **v1.17.0** (verified live: `bootstrap.py` `KIT_VERSION =
"1.17.0"`, `substrate.config.json` `kit_version`); the #67 enabler
bullet now records the #142 split (verified live:
`.github/workflows/automerge-card-guard.yml` host-owned reconciler +
kit-owned `auto-merge-enabler.yml` + 17 `automerge.branch_patterns` in
config); #102 open/NEEDS-CHANGES → MERGED `1c323c1` (zero open PRs at
this scan, API-verified 2026-07-15); both fishing SIM-REQUESTs
`open` → `routed` (verified in `control/outbox.md` at HEAD, lines
358–366/430–436); ORDER 008 recorded ACKED-not-done per the heartbeat;
ORDER 009 closeout and ORDER 010 EAP-extension-to-2026-07-21 added
(verified in `control/inbox.md`). Anchor comment moved `4330559…` →
`446a84e654abdb06a75c8ad637fabbdf779a2771`; Status badge stays in the
first 12 lines. Suite claim re-verified by running it: `python3 -m
pytest -q` = **810 passed** at baseline (30.16s) and post-edit
(29.95s); `bootstrap.py check --strict` exits 1 pre-flip SOLELY on
this card's designed born-red hold (advisory-only warnings otherwise
— 18 model-line payload findings on the historical 2026-07-14 night
cards plus one owner-action-fields nudge, both pre-existing at
baseline). NOT verified, flagged instead of guessed: sim-lab's side of
the SIM-REQUEST routing (cross-repo read denied on this seat per the
#138 heartbeat's recorded wall) — the routing citation remains the
at-HEAD ORDER 009. Coordinator scope change mid-session: pushes and PR
creation denied by the platform classifier for dispatched sessions, so
this branch is LOCAL-ONLY (no PR, no gate run); the claim file rides
the branch un-deleted since no close-out lands on main.

## 💡 Session idea

The stale facts this groom fixed were mostly VERSION tokens: the
ledger's stamp line said `substrate-kit v1.15.0` two upgrades late, and
`control/status.md`'s `kit:` segment STILL says v1.15.0 at HEAD (written
at #138, pre-#141/#144 — left alone here; heartbeat is out of this
slice's scope). Version drift is machine-checkable today: add a
check-time advisory (`[kit-version-drift]`) that greps committed
stamp/heartbeat surfaces — the ledger's truth-stamp paragraph and the
heartbeat's `kit:` line — for the `substrate-kit vX.Y.Z` token and
compares each against `engine.grammar`'s `KIT_VERSION`, advisory on
mismatch, so every kit upgrade surfaces its stale version claims in one
finding instead of waiting for a human groom (this session found the
heartbeat drift only by reading the file end-to-end). Dedupe against
recent cards' ideas: the #89 ledger-drift KIT-ASK compares the ledger's
highest CITED PR to main's squash subjects (watermark axis, same file,
different field); the #139 block-sync idea pins byte-identical prose
blocks; the #142 idea pins config→rendered-expression equivalence; the
#143 idea pins `preflight_scripts` path EXISTENCE. None compares a
version token to the kit's own constant.

## ⟲ Previous-session review

Target: games PR #143 (`claude/preflight-path-fix`, squash `d7595aa`,
the newest prior card). Its load-bearing claims re-verified from this
session's own evidence, not its card's word: (1) "check --strict stops
skipping the preflight leg" HOLDS at `446a84e` — this session's two
full strict runs emitted NO `preflight script … not found` NOTE and no
`[preflight-script]` finding, and `scripts/preflight.py` exists
delegating to `tools/preflight.py` exactly as described; (2) its "810
passed" suite claim REPRODUCES twice at this HEAD (30.16s / 29.95s vs
its 42.50s); (3) its claim-file discipline verifies — `control/claims/`
contains only the README at HEAD, so its flip-commit claim release
landed. One ding: its 💡 (a `tests/tools` pin that every
`preflight_scripts` config entry EXISTS as a file, plus the
delegation-stays test) is still unbuilt — `grep -rl preflight_scripts
tests/` is empty at HEAD, so the silent-skip class it named has no
in-repo tripwire yet; two kit upgrades (#141/#144) have already regen-
touched adjacent surfaces since, which is exactly the churn that idea
guards against. One observation: its card's model segment reads
`Fable-class` — passes the exact-ID lint (correctly: family-level), but
the taught examples use the `fable-5` shape; the payload lint's model
segment has no taxonomy, so this drift class is invisible to it.
