# 2026-07-14 · night test — test: exploration quest catalog — every quest completable within budget

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-14T04:26:20Z · night-quest-completability

Test slice from #129's card idea, verified fresh at branch base `8703481`:
nothing in the tree walked any `games/exploration/quest/catalog.py` quest
to COMPLETED via the real seam — `tests/exploration/` covered the CLI and
help parity, `services/tests/test_exploration_workflow.py` covered op
semantics, but no test proved the CATALOG rows are finishable.

Read-first: quests declare their own bound as objectives' `required`
counts (budget = sum, 2–5 across the five templates); each on-menu
`apply_action` maps 1:1 to an objective event whose catalog predicates
carry no `count_field`, so one ok action advances exactly one step; energy
is `TUNABLES[difficulty]` (60/50/40 bar, cost 1) with NO rest/regen op on
the seam; rewards are `TIER_CAPS[tier]` by construction with capability
tier-III-only.

Shipped **6 tests** (≤10 as specced; internal loops bounded by each
quest's own budget, never unbounded; 0.05s) in
`tests/exploration/test_quest_completability.py`: the sweep (all 5 ids ×
3 tiers, offer → accept → budget-bounded act loop → COMPLETED, failures
collected as named headline rows and asserted empty — a red names every
broken quest×tier instead of deleting it); budget tightness (budget−1
actions leave ACTIVE — pins no hidden multi-counts); banked bundle ==
tier cap component-wise + capability rule + `GLOBAL_MAX` ceiling + ledger
fold + retire + one grant row; energy-starvation sweep (budget×cost ≤
max_energy at every difficulty — no rest op exists, so a miss is
uncompletable, a headline); fixed-seed determinism (identical instance
id, audit stream, bundle across two walks); audit-trail arithmetic
(budget+3 rows per banked quest).

**No headline bug found**: every quest × tier walks to COMPLETED in
exactly its declared budget, every budget fits every difficulty's bar
(worst case 5×1 vs 40), bundles match caps. The value is the tripwire —
any future catalog row that under-budgets, over-counts, or starves reds
with its name in the failure. Floor `tests/exploration` 17 → **23**
(floor==collected); `docs/balance.md` regenerated BEFORE flip; suite
**788 → 794 passed** locally; flip-readiness via this run's own #131
deliverable: `python3 tools/preflight.py --flip` GREEN post-flip. Claim
`control/claims/night-quest-completability.md` self-released here.

## 💡 Session idea

The sweep proves completability from a FULL bar — but the seam has no
rest/regen op (`regen_seconds` ships in `TUNABLES` with zero seam
consumers), so energy is a strictly draining resource across a session,
and `accept` never checks affordability: a player at energy 3 can accept
`cull_the_pack` (budget 5) and hold a quest that is GUARANTEED to stall
too-tired forever — silently, since the too-tired message says "rest and
try again" while no rest exists on the seam. Add **budget-affordability
surfacing**: the seam exposes each template's declared action budget
(`budget(template) = sum(required)`), `offer`/`accept` warn (or
honest-refuse) when `energy < budget × cost`, and a test drives the
drain-to-stall path end-to-end plus pins the session horizon — how many
quests one full bar funds per difficulty — so a tunables change that
strands players mid-quest reds immediately. Dedupe check against all
2026-07-14 cards' 💡 lines: the completability idea (#129) is THIS slice
(full-bar walks); degenerate-bounds, detector-trips, and sim-smoke pin
renderers/predicates, not energy affordability; no card mentions the
regen-less drain, the stall-forever accept, or a session-horizon pin.

## ⟲ Previous-session review

The previous slice is this run's own #131
(`claude/night-preflight-flip-mode`, born-red `2706a47`, implementation
`2d2f2e4`, flip `6db498d`, test-fix `480cf00`, squash-merged to main as
`8703481` — this branch's base — by github-actions[bot] at
2026-07-14T04:23:34Z). Same-session review, so discount, but the honest
headline is a NEGATIVE: **CI was not green on first post-implementation
push.** At flip SHA `6db498d`, tests run `29305687495` FAILED — the
slice's own byte-compat pin asserted a bare `"4/" not in out`, and CI's
toolcache interpreter path (`/Python/3.14.6/x64/`) is echoed verbatim in
the preflight banners, so the substring matched a path, not a step
banner. The fix (`480cf00`) anchored the assertion to `preflight 4/` /
`flip-ready` / `flip-readiness`; runs `29305843287` (tests) and
`29305843292` (substrate-gate) then both success, and born-red
`2706a47`'s gate failure (run `29305440451`) was the designed HOLD. The
lesson generalizes and the fix commits it as a comment: negative
substring assertions over output that echoes ABSOLUTE PATHS are hostage
to the host's path shape — anchor on emitted prefixes. What held up
well under re-use: this slice ran `preflight --flip` as its own
flip-readiness gate (dogfood of #131's deliverable, green), and the
strict step-4 semantics #131 pinned via `--session-log` are exactly what
held this slice's own born-red HOLD red at `4e3ed21`.
