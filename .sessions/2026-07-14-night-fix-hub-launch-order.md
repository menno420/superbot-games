# 2026-07-14 · night fix — print the hub launch banner before the game session

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-14T01:58:14Z · night-fix-hub-launch-order

UX bug-fix slice. `games/__main__.py`'s `hub_step` called `launch(entry)`
(which runs the whole game session synchronously via `_default_launch`)
and only THEN returned `lines=["Launching {id}…"]` (line 146 pre-fix);
`main()` prints `step.lines` after `hub_step` returns — so the banner
printed after the game had already ended. Reproduced this session at
main `bdc3445`: `printf 'play mining\nquit\nquit\n' | python3 -m games`
showed mining's session summary and "Thanks for playing!" BEFORE
"Launching mining…". Grep confirmed nothing else rendered or pinned the
banner ("Launching" appeared only at the one render site).

Shipped: the banner emission moved into the launch path — a
`launching_line(game_id)` string builder (single source, exported) plus
per-caller announcing wrappers that emit it BEFORE invoking the opener
(`main()` prints it; `run_hub` appends it to the transcript, so scripted
sessions still show the line). `hub_step` keeps its dispatch contract —
resolves the token, calls the injected `launch`, sets `launched`, never
raises on bad input, the injectable-launch audit seam untouched — but no
longer returns the banner as a post-launch line. #111's
`services/tests/test_games_hub_loop.py` updated honestly (the behavior
change is the point): four new pins — the END-TO-END order in `main()`
(banner index < the opener's own stdout index), the transcript banner on
both `run_hub` launch paths (fallback opener and injected fake), and
`hub_step`'s bannerless return. Verified by rerunning the repro: the
transcript now reads `games> Launching mining…` THEN mining's banner and
session. `services/tests` floor 178 → 182; `docs/balance.md`
regenerated (gen-balance gate). Full suite 671 → **675 passed** locally
on this branch; `gen_balance.py --check` green. Claim
`control/claims/night-fix-hub-launch-order.md` self-released in this
flip commit (established precedent).

## 💡 Session idea

This bug lived in the GAP between two green suites: hub tests asserted
the banner string existed and the game tests asserted the session ran,
but nothing observed their relative ORDER on the real stdout stream.
Adopt a **scripted-transcript golden corpus**: commit a tiny set of
canonical end-to-end stdin scripts (one per game + one hub script, e.g.
`printf 'play mining\nquit\nquit\n' | python3 -m games`) with their full
expected transcripts as golden files, replayed by one meta-test with the
world seed pinned — any future ordering/interleaving regression (banner
after session, prompt after output, summary before the last action)
diffs loudly as a transcript change, not silently between suites.
Dedupe check against the used-idea list: the shared REPL seam is about
driving REPLs uniformly, the sim-harness smoke registry about harness
liveness, the display-table completeness registry about table coverage,
and slice 2's composed-narration grammar lint about single-line grammar;
none pins the ordered, interleaved stdout of a whole scripted session.
No card idea to date does.

## ⟲ Previous-session review

The previous slices are this run's own #115 and #116, reviewed against
their branches and live CI: #115
(`claude/night-fix-dnd-resolver-unhashable`, born-red `134fe1d`, fix
`e29ebb6`, flip `9011634`) is fully verified — at the flip SHA all three
workflows completed green (tests run 29299418922, substrate-gate run
29299418928, auto-merge-enabler run 29299418946), and the born-red SHA's
substrate-gate failure (run 29299262324) was exactly the designed
pre-flip HOLD its card convention predicts. #116
(`claude/night-fix-fishing-dock-grammar`, born-red `917dde1`, fix
`972bc74`, flip `090ceef`) verifies locally — repro fixed ("🪝 At the
Old Dock"), suite 674 on its branch, strict exit 0 post-flip — but its
CI had produced no listed workflow runs at this session's first poll
(minutes after push), so its conclusions are recorded in the session
report rather than re-asserted here. One honest note repeated from
#116's card: each flip's green is claimed from the local suite + strict
run at flip time; CI conclusions land in the report.
