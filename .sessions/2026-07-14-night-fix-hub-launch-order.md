# 2026-07-14 · night fix — print the hub launch banner before the game session

> **Status:** `in-progress`
>
> 📊 Model: Fable · 2026-07-14T01:54:25Z · night-fix-hub-launch-order

UX bug-fix slice. `games/__main__.py`'s `hub_step` calls `launch(entry)`
(which runs the whole game session synchronously via `_default_launch`)
and only THEN returns `lines=["Launching {id}…"]` (line 146); `main()`
prints `step.lines` after `hub_step` returns — so the launch banner
prints after the game has already ended. Reproduced this session at main
`bdc3445`: `printf 'play mining\nquit\nquit\n' | python3 -m games` shows
mining's full session summary and "Thanks for playing!" BEFORE
"Launching mining…". Grep confirms nothing else renders or pins the
banner text ("Launching" appears only at `games/__main__.py:146`).

Plan: move the banner emission into the launch path — a `launching_line`
string builder plus per-caller announcing wrappers (`main()` prints it,
`run_hub` appends it to the transcript) BEFORE the opener is invoked;
`hub_step` keeps its dispatch contract (`launched` set, never raises,
same clamp of bad input) but no longer returns the banner as a
post-launch line. Update #111's `services/tests/test_games_hub_loop.py`
honestly — the behavior change is the point — pinning the NEW order
end-to-end (banner precedes the opener's own output in `main()`), plus
the transcript banner in `run_hub` and `hub_step`'s bannerless return.
Verify by rerunning the repro. `services/tests` floor bumped and
`docs/balance.md` regenerated in the same push.

Self-release note: this slice's claim file
(`control/claims/night-fix-hub-launch-order.md`) is deleted in this
card's flip commit, per the established precedent.
