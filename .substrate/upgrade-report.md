# substrate-kit upgrade report — v1.13.0 → v1.14.0

> Generated 2026-07-12 by `bootstrap.py upgrade`. Rollback: `python3 bootstrap.py upgrade --rollback`.

**Docs:** consumer-edited: 6 · diverged: 1 · template-improved: 5 · unchanged: 10

| planted doc | class | note |
|---|---|---|
| CONSTITUTION.md | template-improved | consumer-untouched + template improved — safe to apply with `upgrade --apply-docs` |
| docs/decisions.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| docs/architecture.md | unchanged | template identical across versions |
| docs/ownership.md | unchanged | template identical across versions |
| docs/runtime_contracts.md | unchanged | template identical across versions |
| docs/repo-navigation-map.md | unchanged | template identical across versions |
| docs/helper-policy.md | unchanged | template identical across versions |
| docs/collaboration-model.md | template-improved | consumer-untouched + template improved — safe to apply with `upgrade --apply-docs` |
| docs/ai-project-workflow.md | unchanged | template identical across versions |
| docs/owner-profile.md | unchanged | template identical across versions |
| docs/AGENT_ORIENTATION.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| docs/current-state.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| docs/question-router.md | template-improved | consumer-untouched + template improved — safe to apply with `upgrade --apply-docs` |
| docs/CAPABILITIES.md | template-improved | consumer-untouched + template improved — safe to apply with `upgrade --apply-docs` |
| docs/SKILLS.md | template-improved | consumer-untouched + template improved — safe to apply with `upgrade --apply-docs` |
| docs/ideas/README.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| .session-journal.md | unchanged | template identical across versions |
| control/README.md | diverged | both the template and the doc moved — manual merge |
| control/inbox.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| control/status.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| control/claims/README.md | unchanged | template identical across versions |
| scripts/env-setup.sh | unchanged | template identical across versions |

## Carve-out scan

- carve-out scan: .github/workflows/substrate-gate.yml — ran, 0 found

## Capability-ledger seed refresh

- capability-seed: docs/CAPABILITIES.md is consumer-untouched — the whole file (fence included) refreshes via `upgrade --apply-docs`; no fence-only refresh needed.

This upgrade ships the venue-scoped capability ledger (grounded-skills §4.2): entries carry a venue token (owner-live · autonomous-project · routine-fired · subagent · any) and the ledger's kit-owned seed block carries the posture decision rule. If this repo carries a local prose copy of the boot-triad/venue-posture rule (superbot Q-0270), that copy is now superseded by docs/CAPABILITIES.md's posture rule — collapse the local copy into a pointer.

## Applied (--apply-docs)

- applied: CONSTITUTION.md (template@new, hash re-recorded)
- applied: docs/collaboration-model.md (template@new, hash re-recorded)
- applied: docs/question-router.md (template@new, hash re-recorded)
- applied: docs/CAPABILITIES.md (template@new, hash re-recorded)
- applied: docs/SKILLS.md (template@new, hash re-recorded)

## Template deltas for diverged docs

### control/README.md

```diff
--- control/README.md (template@old, current slots)
+++ control/README.md (template@new, current slots)
@@ -148,6 +148,7 @@
 WHAT: <one plain sentence, zero jargon — the thing the owner does>
 WHERE: <exact click path or URL>
 HOW: <paste-ready text/values where applicable, or "click only">
+RISK: <one class per manual step — ✅ safe / read-only · ↩️ reversible (say how to undo) · ⚠️ irreversible / destructive>
 WHY-IT-MATTERS: <one sentence, in product terms>
 UNBLOCKS: <what starts moving the moment it's done>
 VERIFIED-NEEDED: <the attempt you made + the exact error/wall proving only the owner can do
@@ -159,6 +160,69 @@
 never exit-affecting — when a non-`none` ⚑ needs-owner list lacks these fields.
 
 Grammar source of truth: the tokens, field lists, and regexes of this format are kit-owned constants in the kit's `src/engine/grammar.py` (EAP §6.8) — the SAME module the `check` enforcers consume, so writer and enforcer cannot drift; agreement is pinned by the kit's `tests/test_grammar.py`.
+
+## Owner-assist output standard — every owner-facing output, not just asks
+
+The OWNER-ACTION block above covers the *needs-owner ask*; this standard
+covers ALL output routed to the owner — reports, questions, values to paste,
+links. The contract in one line: **the owner never derives anything** — an
+output that requires the owner to parse, derive, or transform anything is a
+drafting defect, not an owner task.
+
+1. **Paste-ready, finished values.** Every value the owner must enter is
+   computed and printed final — `NAME=value`, the full command, the full
+   file body — never a recipe for deriving it. When the owner must paste
+   something, give the exact link to where it goes; a full file goes in ONE
+   copyable fenced block, directly in chat.
+2. **Exact destination, always.** Every action names its exact destination:
+   a deep URL, a console path to the exact field (surface → section →
+   field, e.g. `Railway → project → service → Variables`), or a repo path +
+   line. Never a bare "go to settings" — `check` nags that class (advisory).
+3. **Risk class on every manual step:** ✅ safe / read-only · ↩️ reversible
+   (say how to undo) · ⚠️ irreversible / destructive. One class per step,
+   stated on the step (the `RISK:` line in an OWNER-ACTION block).
+4. **Structured choices, recommendation first.** A decision put to the
+   owner is options A/B(/C) with a **bolded recommendation** and a one-line
+   rationale, answerable with one letter — never an ask that requires the
+   owner to parse, derive, or transform anything.
+5. **Large outputs: digest + rendered link, never a wall of text.** Default
+   delivery is a control-plane rendered link plus a 3-line digest in chat;
+   the fallback — full text in one copyable block directly in chat — applies
+   where the control plane cannot render the repo yet. Link rules: deep-link
+   the exact file, never the repo root; the rendered view for things the
+   owner should *read*, the GitHub blob URL for things the owner should
+   *edit*; post-merge, link `ref=main`; the control-plane render cache is
+   180 s — append `&refresh=1` when the owner must see a just-pushed change.
+
+Worked example — digest + rendered deep link + a six-field ask carrying its
+risk class (every rule above in one output):
+
+```
+📄 Adopter-outcomes report — shipped (PR #247, merged b862e9a)
+
+Digest: before/after adoption is unmeasurable (9/10 adopters born <20h
+before their kit-install PR); false-claim audit near-clean (1 confirmed,
+self-corrected in 6 min); post-adoption time-to-ship baselines recorded.
+
+Full report (rendered, phone-readable):
+https://control-plane-production-abb0.up.railway.app/journal/substrate-kit/file?path=docs/reports/2026-07-11-adopter-outcomes-measurement.md
+
+⚑ OWNER-ACTION — set GITHUB_TOKEN on the control-plane service
+WHAT: paste one variable into Railway so private-repo pages stop degrading.
+WHERE: railway.app → project `websites` → service `control-plane` →
+       Variables → New Variable.
+HOW (paste-ready): name `GITHUB_TOKEN`, value = the fine-grained PAT you
+       created for the fleet's repos (contents: read). One paste, Save.
+RISK: ↩️ reversible — delete the variable to undo.
+WHY-IT-MATTERS: private-repo renders show "not-configured" banners until
+       this is set.
+UNBLOCKS: rendered file links + queue items for private repos.
+VERIFIED-NEEDED: attempted 2026-07-11 — raw fetch of a private path
+       returns 404 without a token (token-on-raw also verified NOT to
+       work, so the API fallback is the only private path).
+```
+
+Grammar source of truth: the risk-class tokens, the structured-choice phrases, and the vague-destination scan of this standard are kit-owned constants in the kit's `src/engine/grammar.py` — the SAME module the `check` enforcers AND the `/intake` skill pins consume, so writer, skill, and enforcer cannot drift; agreement is pinned by the kit's `tests/test_owner_assist.py`.
 
 ## `inbox.md` order format (manager-written, append-only)
 
```

