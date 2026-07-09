# 2026-07-09 · exploration wind-down — gen-1 → gen-2 succession package

> **Status:** `in-progress`

- **📊 Model:** claude-fable-5 · standard · wind-down/succession (worker session, exploration lane)

## Scope (declared up front — born-red)

Owner's WIND-DOWN order for the exploration lane (gen-1 → gen-2 fleet transition;
blueprint §4 natural-boundary migration). Seven deliverables, one branch
(`claude/exploration-wind-down-2026-07-09`), READY PR, merge on green:

1. Finish/park — open-PR disposition + the lane's roadmap/queue state committed.
2. Extensive dated project review → `docs/retro/project-review-wind-down-2026-07-09-exploration.md`.
3. Succession doc (first-10-minutes read order, walking skeleton, known walls with
   exact error text) → `docs/succession-exploration.md`.
4. Gen-2 Custom Instructions rewrite proposal → `docs/gen2-custom-instructions-exploration.md`.
5. Tested defensive environment setup script → `environment/setup-exploration.sh` (+ env var names).
6. Gen-2 blueprint feedback → `docs/gen2-feedback-exploration.md`.
7. Ready marker — `control/status-exploration.md` flipped to wind-down-complete as the
   deliberate LAST commit (with this card's flip).

Pre-work already landed this session: ORDER 005 PING-ACK (PR #12, merged `27d0673` —
dispatch 17:54:33Z → discovery 19:54:00Z → ack-on-main ≈ 19:57Z). Exploration-lane files
only; mining's draft PRs #5/#11 are out of lane and untouched.
