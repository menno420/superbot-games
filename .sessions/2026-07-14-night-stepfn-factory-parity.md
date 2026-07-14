# 2026-07-14 · night build — refactor: one step-closure per game — main() and run_commands share construction

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-14T04:51:53Z · night-stepfn-factory-parity

Build slice from #130's final-verdict follow-up, verified fresh at branch
base `bc85689`: the loops are unified (`repl`/`run_scripted`) but each
game still wrote its per-step BOOKKEEPING CLOSURE twice — `main()` and
`run_commands` each defined a near-identical `step_fn`, and the hub pair
duplicated the announcing-launch wrapper. Read-first: all five entrypoint
pairs read end-to-end before touching any; the only twin asymmetries were
clock source (interactive stamps per-line wall clock, scripted a fixed
`now`) and counters the interactive summaries never read (fishing
`ok_casts`, exploration `quests_completed`, hub `launched`).

Shipped ONE `make_step_fn` per pair, used by BOTH drivers:
`games/{mining,fishing,dnd,exploration}/cli.py` gain
`make_step_fn(state, sink, *, now=None[, rng=None])` →
`(step_fn, StepTally)` (`now=None` keeps the interactive per-line wall
clock; fixed `now` keeps scripted determinism); the hub gains
`make_step_fn(entries, *, launch, announce=None)` (buffered banner for
the transcript vs `announce=print` before the synchronous sub-session —
the #117 ordering preserved). No pair was left unshared — none required
a behavior change.

**Byte-identity** (#125/#127/#130 pattern): 10 fixed-seed/now transcripts
— `run_commands` ×4, `run_hub`, and all five interactive `main()`s under
frozen module clock + seeded rng + replayed input (hub main including a
REAL mining sub-session launch) — each captured TWICE to prove
determinism before trusting it; all 10 SHA-256s identical before
(`bc85689`) and after (`640c7d0`); table on PR #134.

**12 driver-parity tests** in
`services/tests/test_stepfn_driver_parity.py` (floor 204 → **216**,
floor==collected): per game, the same command list through a piped
`main()` and through `run_commands` pins the actual relation —
main-stdout == greeting line(s) + the scripted transcript, byte for
byte; adoption spies prove BOTH drivers construct via the factory with
the right clock/announce mode; the hub factory's two announce modes
pinned directly. `docs/balance.md` regenerated BEFORE flip; suite
**798 → 810 passed** locally; preflight green. Honesty note: the capture
harness lives in the session scratchpad (the same non-durability this
run's #131 review dinged #130 for) — but unlike #130, the parity tests
here DO re-derive the transcript relation in-repo on every run, so the
evidence class is no longer scratchpad-only. Claim
`control/claims/night-stepfn-factory-parity.md` self-released here.

## 💡 Session idea

Freezing the interactive clock for the parity tests required swapping the
cli MODULE's `datetime` attribute (a `FrozenDatetime` subclass injected
via monkeypatch) — the third test module to hand-roll that dance, and a
fragile one: it works only because each cli module happens to call
`datetime.now(timezone.utc)` through its own module global. Make the
clock a SEAM instead: `make_step_fn(..., clock=None)` where `clock` is a
zero-arg callable defaulting to `lambda: datetime.now(timezone.utc)` and
the fixed-`now` path becomes `clock=lambda: now` — wall-clock consumption
collapses to one auditable parameter, tests inject a fake clock the
supported way (no module-attribute surgery), and a grep-pin test can
assert no game cli calls `datetime.now` outside the factory default.
Dedupe check against all 2026-07-14 cards' 💡 lines: this run's slice-1
idea is the `--cards-from-diff` bootstrap lane (CI/local card-loop
parity); the REPL/scripted/step-factory seam ideas (#111/#127/#130 cards)
unified LOOPS and CLOSURES, never the clock; golden-corpus, grammar-lint,
registry, ratchet, telemetry, stamp, and quest ideas are elsewhere. No
card touches clock injection.

## ⟲ Previous-session review

Previous slice is this run's own #133 (`claude/night-flip-card-parity`,
born-red `e18df8b`, implementation `4188585`, flip `d8a2d6d`,
squash-merged `bc85689` — this branch's base). Same-session review,
discount accordingly; external evidence: at the flip SHA, tests run
`29306892092`, substrate-gate run `29306892105`, and enabler run
`29306892095` all success; the born-red (`29306589827`) and mid-slice
(`29306777698`) substrate-gate failures were the designed HOLD while
tests stayed green (`29306589824`, `29306777714`) — CI green on every
push, first try. Strong points held up in use: this very slice ran
`preflight --flip` and it derived THIS branch's card via `--session-log`
(the banner names it), exactly the parity #133 promised. Two honest
dings: (1) #133's derivation re-implements the substrate gate's shell
grammar in Python — two derivations of the same card set that can drift
(its own 💡 concedes this and proposes the single-source fix; until then
the parity is by convention, not construction). (2) coverage asymmetry:
the ADDED-card lane is derived, but a branch that only MODIFIES cards
still falls to the zero-added mtime fallback locally while CI runs the
locked-door gate per modified card — the banner is honest about the
fallback, but "flip-ready" on such a branch still grades a
possibly-wrong card.
