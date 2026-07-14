# 2026-07-14 · night build — refactor: single-source CLI verb tables + shared help-parity test

> **Status:** in-progress
>
> 📊 Model: Fable · 2026-07-14T03:05:42Z · night-verb-table-help-parity

Build slice implementing the verb-table single-source idea from
`.sessions/2026-07-14-night-coverage-mining-cli.md` (verified
unimplemented): each game CLI hand-syncs its verb enumerations
(`_ACTION_VERBS` frozenset, dispatch if-ladder, `help_lines()` text).
Plan: derive `_ACTION_VERBS` from one module-level dispatch mapping per
CLI where the structure allows it, keep behavior byte-identical
(scripted transcripts captured before, asserted after), and add
help-parity tests pinning that each CLI's help names exactly its verb
surface.
