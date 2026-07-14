# 2026-07-14 · night docs — docs: truth-stamp — record the night improvement wave (#120–#134)

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-14T05:07:01Z · night-truth-stamp-closeout

Docs slice, executed at branch base `4330559`: `docs/current-state.md`'s
anchor sat at `fdea103` (#119) with fifteen PRs landed since. Groomed the
ledger: fifteen new "Recently shipped" bullets — #120 `51590c6`,
#121 `fefe16c`, #122 `f3fd346`, #123 `b5cf597`, #124 `91ee62f`,
#125 `e196b85`, #126 `9f48f7c`, #127 `94a396c`, #128 `1d38230`,
#129 `e2cc40f`, #130 `2b55e43`, #131 `8703481`, #132 `b7b1062`,
#133 `bc85689`, #134 `4330559` — every SHA verified against
`git log fdea103..4330559` (first-parent) before writing. "In flight"
re-stamped at `4330559`: watermark #119 → #134, suite **695 → 810
passed** across the wave (verified by running `python3
tools/preflight.py` at this HEAD), the improvement-wave narrative in its
clusters (tripwire registries #119/#122/#123/#126/#129/#132 · tooling
seams #125/#127/#128/#130/#131/#133/#134 · generator pins + fix
#121/#124 · docs #118/#120, with the prior wave's #115/#116/#117 fixes
as context), coverage line re-attributed to the #120 groom, anchor
comment moved `fdea103…` → `4330559589197a5638e30f25adcdf00367910f3c`.

**Dogfood note**: the bullet skeletons were generated with
`python3 tools/stamp_scaffold.py` (#120's deliverable, its first
production groom). It worked as designed — all fifteen PR numbers/dates/
SHAs machine-derived from the anchor, zero `#?` placeholders on the
merge-commit range — and the groom's hand-work reduced to prose + the
suite/floor numbers quoted from each PR's session card. Suite deltas
cross-checked card-by-card (695→703→716→727→736→736→744→749→760→766→
773→784→788→794→798→810, telescoping cleanly to the preflight-verified
810). No code/test changes; preflight green pre-push. Claim
`control/claims/night-truth-stamp-closeout.md` self-released here.

## 💡 Session idea

The scaffold made citations mechanical, but this groom's remaining
hand-work was COUNTS: suite deltas and floor moves were still copied by
eye from fifteen session cards into fifteen bullets (and the telescoping
check above was done by hand) — the numbers are now the groom's only
typo surface left. Add **scaffold enrichment**:
`stamp_scaffold.py --enrich` maps each squash commit to its session card
(the squash body already carries `Head-ref: claude/<slug>` → 
`.sessions/<date>-<slug>.md`), extracts the card's recorded
`suite A → B passed` and `floor X → Y` spans, and appends them to the
emitted bullet skeleton — plus a telescoping lint (each bullet's suite
start must equal the previous bullet's end) so a mis-copied count fails
at authoring time instead of living in the ledger. Dedupe check against
all 2026-07-14 cards' 💡 lines: the night-wave card's idea WAS the
scaffold (built, #120); the telemetry-outcome backfill targets
`model-usage.jsonl`, not the ledger; the #89 ledger-drift KIT-ASK is a
kit-side staleness DETECTOR, not an authoring aid; this run's slice
ideas are the `--cards-from-diff` bootstrap lane and the CLI clock seam.
No card touches card-count enrichment or a telescoping lint.

## ⟲ Previous-session review

Previous slice is this run's own #134
(`claude/night-stepfn-factory-parity`, born-red `11c74f6`,
implementation `640c7d0`, flip `71e55dc`, squash `4330559` — this
branch's base). Same-session review, discount accordingly; external
evidence: at the flip SHA, tests run `29307640681`, substrate-gate run
`29307640639`, and enabler run `29307640641` all success; the born-red
(`29307117691`) and mid-slice (`29307517348`) substrate-gate failures
were the designed HOLD while tests stayed green (`29307117645`,
`29307517356`) — green on every push, first try. The byte-identity
table (10 transcripts, double-run determinism proof, before/after
SHA-256 equality) is the strongest evidence class this repo runs for
refactors, and the 12 in-repo parity tests improve on #130's
scratchpad-only evidence by re-deriving the transcript relation on
every CI run. Two honest dings: (1) the parity tests freeze the
interactive clock by swapping each cli module's `datetime` attribute —
module-attribute surgery that works only by import-shape accident; the
card's own 💡 (clock seam) is the admission. (2) the hub's parity test
deliberately avoids the launch path (non-launch commands only): the
announce modes are pinned on the factory directly, but a piped hub
`main()` through a REAL sub-session exists only in the scratchpad
capture (`hub_main` transcript, SHA `ca868f4…`), so the one genuinely
novel interleaving — banner before a synchronous sub-REPL — is not
re-proven in-repo per run.
