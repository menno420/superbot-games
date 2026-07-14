# 2026-07-14 · night build — refactor: shared REPL seam — one loop implementation for all five CLIs

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-14T03:23:37Z · night-shared-repl-seam

Build slice from `.sessions/2026-07-14-night-coverage-games-hub.md`'s card
idea, verified unimplemented at branch base `9f48f7c` (no `games/shared/cli/`
existed). Five interactive `main()` loops — `games/{mining,fishing,dnd,
exploration}/cli.py` + `games/__main__.py` — each hand-rolled the same
banner / `input(PROMPT)` / EOF-^C-newline / quit / step-print / summary /
`return 0` mechanics. All five were read FIRST; the only real differences
were per-game bookkeeping (cast/action/choice counters, dnd's
`scenes_visited` + `story_over`) and the hub's pre-launch banner — all of
which stay with the game, closed over inside its `step_fn`.

Shipped `games/shared/cli/repl.py`: `repl(step_fn, *, prompt, source=None,
sink=None, banner_lines=(), closing_lines=None)` owning the loop once,
adopted by ALL FIVE mains (none had to be left behind). Defaults resolve
LAZILY to the live `input`/`print` — a def-time `source=input` default would
have silently broken the established monkeypatch-`builtins.input` test
choreography (pinned by a dedicated test). Byte-identity discipline (#125's
proven pattern): 15 scripted-stdin transcripts — help/action/unknown/quit +
EOF-close + ^C-close variants per entrypoint, frozen `datetime.now`, seeded
rng (fishing/mining cores are `(state.seed, spot)`-derived anyway) —
SHA-256-identical before/after; run-to-run determinism verified first; full
table in PR #127's body. 11 tests in `services/tests/test_shared_repl_seam.py`
(same suite as the hub-loop tests): quit/EOF/^C close paths, banner-before-
first-read, line ordering, closing-lines-see-final-state, live-builtins
default, empty session, plus fishing/exploration `main()` adoption drives.
Coverage: `games/shared/cli/repl.py` 100%; fishing cli 93% → **99%** and
exploration cli 90% → **96%** with both `main()` bodies fully covered (the
residual misses are pre-existing non-main branches: fishing 263/379,
exploration 107/178/221/260-261/322). Suite **749 → 760 passed**;
`services/tests` floor 182 → **193** (floor==collected); `docs/balance.md`
regenerated BEFORE flip, `--check` green. Claim
`control/claims/night-shared-repl-seam.md` self-released in this flip commit.

## 💡 Session idea

Unifying the interactive loop exposed its scripted TWIN still duplicated
five times: `run_commands` (×4) and `run_hub` each hand-roll the same
feed-loop — iterate commands, `step()`, break on quit, `lines.extend`,
per-game counters, append summary, build a SessionResult. Extract the
scripted-session seam next: one generic
`run_script(step_fn, commands, *, opening_lines, closing_lines)` in
`games/shared/cli/` returning `(lines, steps)` that the five drivers wrap
for their own SessionResult bookkeeping — so the scripted and interactive
paths dispatch through the SAME `step_fn` shape and the feed mechanics are
written once. Dedupe check against the used-idea list: the REPL-seam idea
(this card's spec) covered the *interactive* `input()` loop only — its own
text called out the interactive/scripted split and left the scripted half
alone; the transcript-golden-corpus idea commits transcripts, it doesn't
unify drivers; verb-table/help-parity unified command *surfaces*, not the
feed loop. No card idea to date touches the scripted-driver duplication.

## ⟲ Previous-session review

The previous slice is #126 (`claude/night-dnd-scene-reachability`,
born-red `b94f562`, squash-merged to main as `9f48f7c` — this branch's
base). Its numbers re-verified against this session's own runs rather than
trusting the card: the suite at `9f48f7c` collects **749 passed** (my
pre-slice baseline run), matching its "744 → 749"; `tests/dnd` floor reads
**68** and `tests/dnd/test_scene_reachability.py` collects 5 tests,
matching its "63 → 68, 5 tests, ≤8 as specced"; `control/claims/` held
only README.md at session start, so its claim self-release held. Its
data-model citations check out where load-bearing: `START_SCENE =
"waystation_road"` sits at `services/dnd_workflow.py:80` exactly as cited,
and the "no headline bug" claim is consistent with the sweep passing green
in my baseline. Its card idea's module citation also verifies:
`games/dnd/core/effects.py` exists at HEAD, so the effects-liveness sweep
it proposes has a real target.
