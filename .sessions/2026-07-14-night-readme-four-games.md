# 2026-07-14 · night docs — README: all four games playable, current commands and hub transcript

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-14T02:10:40Z · night-readme-four-games

Docs slice. README.md's "## Playing the games" section (lines 29–59) was
stale on four counts, verified against real headless runs at main
`d47e28b`: (1) it opened "Two of the world games are playable right now"
while the hub lists FOUR (mining #70, fishing #71, dnd #75, exploration
#77, over the hub #72); (2) it omitted the `python3 -m games.dnd` and
`python3 -m games.exploration` standalones entirely; (3) fishing's
command list predated the `sell <species> [qty]` command (#83/#87); (4)
the seam closer named only `services/mining_workflow.py` /
`services/fishing_workflow.py`, though `services/dnd_workflow.py` and
`services/exploration_workflow.py` exist and are what the two missing
standalones drive. The embedded hub transcript was also pre-#117.

Shipped: the section re-captured from real scripted runs at HEAD — the
same discipline `.sessions/2026-07-13-document-playable-games.md` set.
The hub transcript is the verbatim NEW post-#117 output of
`printf 'list\nhelp\nquit\n' | python3 -m games` (all four games
listed); each standalone's command list is transcribed from its own
`help` output (`printf 'help\nquit\n' | python3 -m games.<id>`),
including mining's argument forms, fishing's `sell <species> [qty]`,
dnd's bounded-menu verbs (`<number>`/`<option name>`, `look`, `status`)
and exploration's quest verbs (`quests`, `offer <id> [tier]`, `accept`,
`act <action>`, `status`). The closer now names all four rung-2 workflow
seams. Edits scoped to the one stale section; existing voice/format
kept; no economy number invented. Docs-only — suite stays **684
passed** locally on this branch; strict check exit 0. Claim
`control/claims/night-readme-four-games.md` self-released in this flip
commit (established precedent).

## 💡 Session idea

The README rotted silently because nothing ties it to the runtime
registry it describes. Adopt a **registry-to-README parity check**: a
tiny test that imports `services/world_registry.py` (via the hub's
composition root), collects every registered game id, and asserts each
id appears in README.md's "Playing the games" section together with its
`python3 -m games.<id>` invocation — so the FIFTH game cannot ship
playable-but-undocumented the way dnd and exploration did. Dedupe check
against the used-idea list: this is not the display-table completeness
registry (in-game render tables), not the sim-harness smoke registry
(harness liveness), not registry-derived CI pytest paths (CI wiring),
not the verb-table single source (code-side verb tables), and not the
scripted-transcript golden corpus (stdout ordering) — it is a
docs-freshness gate keyed off the world registry. No card idea to date
pins README prose to the registry.

## ⟲ Previous-session review

The previous slice is #117 (`claude/night-fix-hub-launch-order`,
born-red `4df88b2`, squash-merged to main as `d47e28b`) — the hub
launch-banner order fix. Verified this session at main `d47e28b`: the
repro its card recorded (`printf 'play mining\nquit\nquit\n' | python3
-m games`) now prints `games> Launching mining…` BEFORE mining's banner
and session — exactly the order its four new pins in
`services/tests/test_games_hub_loop.py` promise — and the full suite
passes 684 at that SHA locally. Its card's honest note (CI conclusions
recorded in the session report, green claimed from local suite + strict
at flip time) is consistent with what landed: the squash merge is on
main, so the enabler only landed it after its checks completed. One
knock-on it correctly predicted: the banner-order change altered the hub
transcript, which is precisely why this README slice had to re-capture
the transcript at HEAD rather than copy the 2026-07-13 capture.
