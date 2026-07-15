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

Close-out is written at flip time; this card holds the substrate-gate
red by design until then.
