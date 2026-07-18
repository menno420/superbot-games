# 2026-07-18 · quest-hashable — restore the hashable-frozen invariant on quest Objective/QuestTemplate

> **Status:** `in-progress`
>
> 📊 Model: Claude Opus 4.x · high · runtime bugfix

⚑ Self-initiated bug-hunt find, reached via the save/load angle: the quest
models promise their frozen dataclasses "stay hashable and frozen" — and cite
THAT as the reason `Objective.params` is a tuple of `(key, value)` pairs rather
than a dict — but `games/exploration/quest/catalog.py` stores DICT values inside
those pairs (`params=(("match", {"item": "supply_crate"}),)`). A dict is
unhashable, so `hash(objective)` / `hash(template)` raise
`TypeError: unhashable type: 'dict'`, silently breaking the class's own
documented invariant. Anything that leans on hashability — a `set`/`dict` key,
a memoized lookup, a save/load round-trip that de-dupes by hash — would trip on
it. Executed at branch base `8bd5da4` (#165, main HEAD).

**The fix (correctness only, no behavior change for readers).** Nested mapping
values in `params` are now normalized at construction into `_FrozenMap` — a
small hashable, order-preserving wrapper (a frozen dataclass over a tuple of
`(key, value)` pairs, recursively frozen) — via `Objective.__post_init__`
(`object.__setattr__`, since the dataclass is frozen). `params_dict()`
reconstructs the plain `dict` on read, so every consumer
(`predicates.event_type_match`, `services/exploration_workflow._event_for`,
`test_balance_sim._satisfying_events`) still sees the identical `dict` content.
The catalog is left untouched — authors keep writing plain dicts, and they are
frozen transparently. Verified byte-identical: `params_dict()` output diffed
equal against `origin/main` for every objective of every catalog template.

## 💡 Session idea

⚑ Self-initiated. A docstring that states an invariant AND names it as the
reason for a specific design choice ("params is a tuple of pairs SO it stays
hashable") is a testable claim, not just a comment — and the most durable
bug-hunt move is to take that claim literally and try to break it. Here the
stated rationale was already contradicted by the sibling catalog module the
same session would read, so a single `hash(template)` over the real catalog
surfaced the latent break. The broader idea: pin self-documented invariants
with a test that exercises the invariant against the REAL data the codebase
ships (the catalog), not a hand-built fixture — a fixture that happens to use
hashable values would have hidden this forever.

## ⟲ Previous-session review

Target: games PR #165 (`8bd5da4`, "docs: correct stale human-gated merge claim
in NEXT-TASKS") — this branch's base and main's current HEAD (`git fetch origin
main && git reset --hard origin/main` → `8bd5da4`, confirmed; `git log
--oneline` lists #163–#165 as the three most recent squashes). It is a docs-only
truth-correction, so its load-bearing claim is a documentation fact rather than
a code path; no runtime seam to re-verify. Green baseline re-run this session
before any edit: `python3 -m pytest -q` = `849 passed, 1 xfailed`, matching the
ledger. The suite this session touches (`games/exploration/tests`) sat at floor
`61`; this session lifts it to `63` for the two added regression tests.

## ✅ Landed
