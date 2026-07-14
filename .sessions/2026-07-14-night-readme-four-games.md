# 2026-07-14 · night docs — README: all four games playable, current commands and hub transcript

> **Status:** `in-progress`
>
> 📊 Model: Fable · 2026-07-14T02:08:57Z · night-readme-four-games

Docs slice. README.md's "## Playing the games" section (lines 29–59) is
stale on four counts, verified against real headless runs at main
`d47e28b`: (1) it opens "Two of the world games are playable right now"
while the hub lists FOUR (mining #70, fishing #71, dnd #75, exploration
#77, over the hub #72); (2) it omits the `python3 -m games.dnd` and
`python3 -m games.exploration` standalones entirely; (3) fishing's
command list predates the `sell <species> [qty]` command (#83/#87); (4)
the seam closer names only `services/mining_workflow.py` /
`services/fishing_workflow.py`, though `services/dnd_workflow.py` and
`services/exploration_workflow.py` exist and are what the two missing
standalones drive. The embedded hub transcript is also pre-#117 (two
games listed) and #117 just changed the launch-banner order.

Plan: re-capture the section from real scripted runs at HEAD — the same
discipline `.sessions/2026-07-13-document-playable-games.md` set —
`printf 'list\nhelp\nquit\n' | python3 -m games` for the hub transcript
(NEW post-#117 output), and each standalone's `help`/`quit` for verbatim
command lists. Keep edits scoped to the stale section, match the
existing voice/format, invent no economy number. Docs-only: no code, no
balance number, no test-floor change.

Self-release note: this slice's claim file
(`control/claims/night-readme-four-games.md`) is deleted in this card's
flip commit, per the established precedent.
