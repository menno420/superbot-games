# 2026-07-10 — substrate-gate runs the test suite (gen-2 night prep)

> **Status:** `complete`

- **📊 Model:** claude-fable-5 · high · one-step CI addition (single-push; the gen-1
  grand-review session, owner-directed night prep)

## Scope

The #5 review flagged it and the grand review (superbot
`docs/eap/gen1-grand-review-2026-07-09.md` §8 item 8) queued it: `substrate-gate` ran
ONLY the kit hygiene check — the repo's 73 pure-domain tests (mining 62 + encounters 11 +
exploration) were never exercised in CI. Every gen-1 merge relied on sessions running
pytest locally; tonight's autonomous sessions get the enforcing version instead
("enforce, don't exhort").

## What shipped

One step appended to `.github/workflows/substrate-gate.yml`: `pip install pytest &&
python3 -m pytest tests/ -q`, behind the same control-fast-lane short-circuit (heartbeat
commits stay a ~7-second green). Suite is pure stdlib — no other deps needed; 73 passed
locally at this head in ~2 s.

⚑ Self-initiated (flagged): a workflow-file change — contained, reversible, and the
owner's "prepare the repos for tonight's autonomous work" is its provenance; veto =
revert this one step.

## 💡 Session idea

The kit's `adopt --wire-enforcement` could plant this pytest step by default whenever a
`tests/` dir exists at adoption time — both games lanes independently assumed CI ran
their tests until a reviewer read the workflow.

## ⟲ Previous-session review

The mining wind-down session (#14) parked a complete succession package cleanly, but its
lane lived its whole life with a tests-blind gate and never flagged it — the exploration
lane's D-0009 ("first CI") stopped at the hygiene check. Reading the workflow file you
rely on takes one minute; assuming it runs your tests cost nothing this time only because
the sweep's reviewers ran them out-of-band.
