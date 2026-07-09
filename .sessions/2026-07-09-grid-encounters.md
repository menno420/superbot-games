# 2026-07-09 · Grid-encounters first slice (games/mining/core/encounters.py)

> **Status:** `complete`
>
> 📊 Model: automation-agent · high · build · lane: game-mining · branch: mining/grid-encounters

## Goal

Build the **grid-encounters** extension's first slice as PURE DOMAIN, stacked on #5's
`mining/port-pure-domain` (PR #11, draft, base `mining/port-pure-domain` → retarget to
`main` after #5 merges). Layer a live-rollable encounter resolver on the seed-deterministic
grid, sim-pin every new balance number, test it, and mark the seam IMPLEMENTED.

## What shipped

- **`games/mining/core/encounters.py`** — a pure encounter resolver. `resolve(seed, cell,
  stats, energy, rng)` → frozen `EncounterOutcome` (kind · resolution · narration · rewards ·
  damage_taken · energy_cost). Two-stage: a `CellFeature`-keyed **trigger** (NORMAL→hazard,
  RICH→rich vein, TREASURE→loot cache, BARREN→none; sparse, hazard chance depth-scaled), then
  a **resolution** — loot/rich reward from the existing ore/depth tables, or single-exchange
  hazard combat via `EffectiveStats` `damage`/`defense`/`max_health`. Deterministic by default
  (grid splitmix64 `(seed,x,y,z)` convention), live-roll by injected `rng`. stdlib only.
- **`games/mining/sim/encounters_sim.py`** — a pure, seeded sim harness (276k-action sweep ×
  fresh/geared/veteran tiers) aggregating kind frequency, hazard win/flee/lose rates, reward
  yields, damage, energy economy. Every new number is sim-pinned from its output.
- **`tests/mining/test_encounters.py`** — 11 tests: determinism (incl. subprocess
  process-independence), injected-rng override, additive-safety (BARREN = stat-independent
  baseline; stats are monotone hazard improvements), no-pay-to-win (no spend lever; rewards use
  only the existing ore vocabulary), sim-pinned distributions within bounds, sim determinism.
  Updated `test_purity.py` module count 18→19. **73 tests pass** (62 existing + 11).
- **`docs/design/mining-grid-encounters.md`** — the encounter model, CellFeature mapping,
  determinism scheme, the **sim-pin table** (actual numbers + bounds + pasted full sim output),
  the no-pay-to-win statement, and deferred slices. `mining-plugin-layout.md` §7 flipped to
  IMPLEMENTED and points to it.
- **`control/status-mining.md`** — grid-encounters PR #11 added in-flight with the sim-pin note.

## Sim-pin headline (evidence in the design doc §5)

11.6% encounter rate (sparse), 88.4% NONE. Depth×gear danger gradient: a bare miner clears
the surface (z0 100% win) but is overwhelmed in the deep (z15 91% lost); earned gear turns
that around (win fresh 16.6% → veteran 64.8%, mean dmg 11.7 → 0.5, geared/veteran never lose).
That gradient IS the no-pay-to-win incentive — advantage is earned in-domain, never bought.

## ⚑ Self-initiated (reversible; flagged for review)

- **Deterministic-by-default rng, live-roll by injection** — reconciles the task's determinism
  requirement with §7's "live-roll" intent (one pure resolver; the host chooses the rng seed).
- **Feature-keyed archetypes, one kind per `CellFeature`** — simplest mapping to a real
  capability; hazards on the common NORMAL cells, RICH/TREASURE pay out, BARREN dead.
- **Single-exchange combat now** (WON/FLED/LOST from one damage-vs-toughness comparison);
  multi-turn HP attrition deferred as a fast-follow reusing the same stat inputs.
- **Hard depth-gate + per-action cooldown deferred to the workflow layer** — they are stateful
  across actions, not pure-domain; the resolver stays per-action and carries depth-danger via
  `HAZARD_DEPTH_SCALE`.
- **All encounter balance numbers are NEW design, sim-pinned in-repo** (not preserved-from-
  oracle) — the first `games/mining/core` module whose constants originate locally; noted in the
  core `__init__` docstring.
- **`games/mining/sim/` created** (no prior sim convention in-repo) as the pure sim-harness home.

## 💡 Session idea

**A reusable substrate `sim-pin` seam.** This session hand-rolled the sim→pin→bounded-test loop
(`sim/encounters_sim.py` produces distributions; a test re-asserts bounds; the doc pastes the
evidence). The kit could formalise it: a `bootstrap.py economy`-adjacent convention where a lane
declares `sim: <module>` + `bounds:` and the gate runs the sim and checks the pinned bounds are
still met — turning "sim-pinned before shipping" from a discipline each porter remembers into an
enforced check. It generalises to every balance number in every game lane (exploration included).

## ⟲ Previous-session review

The pure-port session (#5) did the seam-setup well: it ported `grid.py` with a clean
`CellFeature`/`cell_at`/splitmix64 substrate and *documented the grid-encounters seam in advance*
(§7), which is exactly what let this slice drop in without re-litigating the design — the value of
"leave the next session better-equipped" made concrete. What it could have sharpened: §7 asserted
"**live-roll** not per-cell deterministic" as if the two were mutually exclusive, which briefly
read as a contradiction with this task's determinism requirement; the reconciliation (deterministic
default + injectable rng) was a one-line insight the seam doc could have pre-empted. **System
improvement:** the born-red→green session-card gate works, but nothing checks that a doc marked
`plan`/DESIGNED actually flips to a shipped status when its code lands — a `plan` doc whose feature
shipped is silent drift. A lightweight kit check ("a design doc referenced by a merged code PR
should not still say `plan`") would catch design/impl drift the way the ledger check catches merge
drift. (Same family as this session's 💡 sim-pin seam: enforce the discipline, don't exhort it.)
