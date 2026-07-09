# 2026-07-09 · Port the pure mining domain (games/mining/core)

> **Status:** `complete`
>
> 📊 Model: automation-agent · high · port · lane: game-mining · branch: mining/port-pure-domain

## Goal

Execute mining **ORDER 001 step 4 / ORDER 002**: begin the P0→P1 port. Stacked on the
kit-adoption work (draft PR #4, `mining/adopt-substrate-kit`), land the **pure mining
domain** as `games/mining/core/` — all 18 pure oracle modules (`disbot/utils/mining/*` +
`disbot/utils/equipment.py`) ported VERBATIM, Discord/DB/IO-free, with unit tests, plus
the plugin-layout design doc. This PR ships the pure-core slice only; workflow +
host-adapter layers are named-next.

## What shipped

- **`games/mining/core/`** — 18 pure modules ported verbatim (every formula + balance
  constant unchanged; sim-pinned upstream, pinned here as *preserved-from-oracle,
  unchanged*). stdlib only; a purity guard test asserts zero discord/DB/IO/services/cogs/
  views imports.
- **Two fishing couplings + one IO coupling severed** (design doc §5): `items.py`'s
  `utils.fishing.fish.SPECIES` import → `register_fish_species` injection point;
  `structures.py`'s 4 fishing structures dropped (forge/home/campfire remain, generic
  registry shape intact); `recipes.py`'s filesystem loader → in-code `DEFAULT_RECIPES` +
  `overrides` injection.
- **62 unit tests** (`tests/mining/`), all green — ore-weight/depth reweighting, mine-roll
  math, energy/capacity/vault formulas, skill caps + forced specialization, forge tier
  gating, additive-safety invariant, grid `cell_at` seed-determinism (incl. a subprocess
  process-independence check + negative coords), fish severance + injection, recipes purity.
- **Design doc** `docs/design/mining-plugin-layout.md` — three-layer split, the superbot-next
  `SubsystemManifest` host-contract mapping (resolves the open plugin-contract question),
  the port-order DAG, the severances, the sim-pinned-balance statement, and the
  grid-encounters extension seam (DESIGNED, not implemented). Linked from AGENT_ORIENTATION.
- **`control/status-mining.md`** rewritten to reality.

## ⚑ Self-initiated (reversible; flagged for review)

- `equipment.py` placed under `games/mining/core/` (not `games/shared/`) to stay in-lane and
  unblocked — flagged as a `games/shared/` promotion candidate for when a 2nd game ports
  (the claim-first moment). No second game has ported yet.
- Optional injectable `rng` threaded through the reward rolls — `rng=None` is byte-identical
  to the oracle (matches the oracle's own `exploration.resolve` and superbot-next's mining
  port); it only enables deterministic tests.
- Tests placed at `tests/mining/` (no pre-existing test dir; standard pytest discovery).

## Open question resolved

**superbot-next host contract** — NOT in flight/absent. It exists concretely
(`sb/spec/manifest.SubsystemManifest` + `sb/manifest/mining.py` + `sb/domain/mining/*`);
mining core-loop is live in next, deep systems pending on D-0043. The pure core docks via
the Layer-3 adapter (design doc §3); it is contract-independent, so it was safe to ship
ahead of any contract churn.

## 💡 Session idea

**A `games/*/core/` purity CI check for the kit's game lanes.** This session hand-rolled a
`test_purity.py` that asserts the pure core imports zero discord/DB/host-layer deps — the
single load-bearing invariant of the whole plugin model. Worth promoting to a reusable
substrate check (`check_pure_core`) that any game lane opts into by declaring its pure-core
path, so the "pure domain stays pure" guarantee is enforced by the gate, not by each
porter remembering to write the test. It generalises directly to the exploration lane and
every future game.

## ⟲ Previous-session review

The previous session (#4, kit adoption) did the first-adopter work well: it not only adopted
the kit but *fixed* the rough edges it hit (the `check_status_current` hardcoded-path clash,
the vestigial generic inbox) and left a precise guard recipe + needs-owner flags, so this
port session inherited a clean, green baseline and a documented contract-question to resolve
— exactly what let it go straight to porting. What it could have done marginally better:
it left the aggregate `control/status.md` two-writer risk as a live workaround rather than a
tracked follow-up with an owner-decision path, so the risk is easy to forget. **System
improvement:** the kit's session-card requires Session idea / Previous-session review /
Model markers but does **not** require a `⚑ Self-initiated` line — yet self-initiated,
reversible decisions (like this session's equipment-placement + rng choices) are exactly
what the owner needs to see and veto. Promoting a `⚑ Self-initiated` marker into the kit's
session-card contract (mirroring superbot's own convention) would make unprompted decisions
uniformly reviewable across every lane, not left to each porter's discretion.

## Verification

`python3 bootstrap.py check --strict` → green (flipped from born-red as the deliberate final
step). `python3 -m pytest tests/mining/` → 62 passed. Pure-core smoke import: all 18 modules
import with zero impure deps.
