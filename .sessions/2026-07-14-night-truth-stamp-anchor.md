# 2026-07-14 · night docs — machine-readable truth-stamp anchor + stamp scaffold tool + groom

> **Status:** `in-progress`
>
> 📊 Model: Fable · 2026-07-14T02:20:53Z · night-truth-stamp-anchor

Docs slice, three parts, from #90's card idea and
`.sessions/2026-07-14-night-truth-stamp-night-wave.md`'s card idea —
both verified unimplemented at main `fdea103` this session (no
`truth-stamped-at` marker anywhere under docs/ or tools/, no
`tools/stamp_scaffold.py`, nothing referencing one):

(a) a machine-readable `<!-- truth-stamped-at: <sha> -->` HTML comment
beside `docs/current-state.md`'s prose stamp ("(Truth-stamped … at HEAD
…)"), so tooling can read the last-groomed SHA without parsing prose;

(b) new `tools/stamp_scaffold.py`: reads that anchor, runs
`git log <anchor>..HEAD --first-parent`, and emits the
`- **#N** (YYYY-MM-DD, \`sha\`) — subject` bullet skeletons the
"Recently shipped" groom hand-transcribes today (squash-merge subjects
carry the PR#) — an authoring aid, deliberately NOT a CI gate, so
SHA/date typos become structurally impossible while prose stays
hand-written; plus a small unit test;

(c) the owed groom in the same PR: record the merged wave since the
last stamp (#108 onward, each PR verified against the local
`origin/main` git log before writing), refresh the suite count and
coverage figures, and move the anchor to the groomed HEAD.

Self-release note: this slice's claim file
(`control/claims/night-truth-stamp-anchor.md`) is deleted in this
card's flip commit, per the established precedent.
