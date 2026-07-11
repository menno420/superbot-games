# substrate-kit upgrade report — v1.11.0 → v1.12.0

> Generated 2026-07-11 by `bootstrap.py upgrade`. Rollback: `python3 bootstrap.py upgrade --rollback`.

**Docs:** consumer-edited: 6 · diverged: 1 · template-improved: 1 · unchanged: 13

| planted doc | class | note |
|---|---|---|
| CONSTITUTION.md | template-improved | consumer-untouched + template improved — safe to apply with `upgrade --apply-docs` |
| docs/decisions.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| docs/architecture.md | unchanged | template identical across versions |
| docs/ownership.md | unchanged | template identical across versions |
| docs/runtime_contracts.md | unchanged | template identical across versions |
| docs/repo-navigation-map.md | unchanged | template identical across versions |
| docs/helper-policy.md | unchanged | template identical across versions |
| docs/collaboration-model.md | unchanged | template identical across versions |
| docs/ai-project-workflow.md | unchanged | template identical across versions |
| docs/owner-profile.md | unchanged | template identical across versions |
| docs/AGENT_ORIENTATION.md | diverged | both the template and the doc moved — manual merge |
| docs/current-state.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| docs/question-router.md | unchanged | template identical across versions |
| docs/CAPABILITIES.md | unchanged | template identical across versions |
| docs/ideas/README.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| .session-journal.md | unchanged | template identical across versions |
| control/README.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| control/inbox.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| control/status.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| control/claims/README.md | unchanged | template identical across versions |
| scripts/env-setup.sh | unchanged | template identical across versions |

## Carve-out scan

- carve-out scan: .github/workflows/substrate-gate.yml — ran, 0 found

## Applied (--apply-docs)

- applied: CONSTITUTION.md (template@new, hash re-recorded)

## Template deltas for diverged docs

### docs/AGENT_ORIENTATION.md

```diff
--- docs/AGENT_ORIENTATION.md (template@old, current slots)
+++ docs/AGENT_ORIENTATION.md (template@new, current slots)
@@ -7,11 +7,9 @@
 
 ## Start every session
 
-1. `.claude/CLAUDE.md` — the working agreement.
-2. `docs/current-state.md` — the living status ledger.
-3. `docs/CAPABILITIES.md` — verified session capabilities & walls (the
-   discovery rule lives there; append what you learn).
-4. This file — task-specific reading routes.
+The boot set lives in `.claude/CLAUDE.md` § "Orientation — read first" (one
+list, one home). This file is not boot reading — open it when a task needs
+a route into the deeper docs.
 
 ## Binding contracts
 
@@ -33,6 +31,4 @@
 
 ## Verifying any change
 
-```
-python3.10 -m pytest (deterministic game-core sims must pass, seed-reproducible) and python3 bootstrap.py check --strict (docs + session-log hygiene). No live CI workflow yet — verification runs locally per lane.
-```
+See `.claude/CLAUDE.md` § "Verifying a change" (one home, never two copies).
```

