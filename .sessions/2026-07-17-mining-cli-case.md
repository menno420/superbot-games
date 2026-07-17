# 2026-07-17 · mining-cli-case — fix: standalone mining CLI item/branch tokens are now case-insensitive (bug + regression tests)

> **Status:** in-progress
>
> 📊 Model: Claude Opus 4.x · high · runtime bugfix

⚑ Self-initiated: small game-improvement slice (owner order 2026-07-17 —
improve the game via contained, tested, independently-landable slices).
Executed at branch base `6f95b9a` (#157).

The standalone mining CLI (`games/mining/cli.py`) never lower-cased the item /
branch / structure token a player types, even though the catalog, inventory,
skill-branch and structure-registry keys are ALL lowercase — and even though
the sibling **fishing** CLI already normalises with `args[0].lower()`. So a
perfectly natural capitalised command misfired three different ways, each
verified live before the fix:

- `sell Iron 2` → **"You only have 0× Iron."** even holding 5 iron. The seam's
  price lookup (`market.sell_price`) is case-insensitive, but the held-quantity
  read (`state.inventory.get(name, 0)`) is not — and inventory keys are always
  lowercase — so the sale was falsely blocked.
- `buy Torch` → succeeded but stored the item under a mismatched `"Torch"`
  inventory key (everything else keys lowercase), so the bought item was
  effectively orphaned from every other lookup.
- `skill Mining 2` → **"Mining is not a skill branch."** (`skills.is_branch`
  keys on the lowercase branch vocabulary).

Fix (surgical, one file): normalise the name at the CLI boundary — lower-case
the name portion in `_split_item_qty` (feeds `sell` / `build` / `skill`) and in
`_do_buy` / `_do_repair`. The key spaces are entirely lowercase, so this only
ever normalises case, never meaning; it mirrors the fishing CLI convention. The
audited seam is untouched (it already lower-cased for price/branch lookups), so
no balance, audit-record or economy behaviour changes.

Scope: `games/mining/cli.py` (the fix) + `tests/mining/test_cli.py` (five
regression tests pinning `sell`/`buy`/`skill`/`repair` case-insensitivity, incl.
the default-quantity sell path) + `tests/mining/EXPECTED_MIN_TESTS.txt` floor
188 → 193. No other surface touched.

## 💡 Session idea

The bug was a **cross-CLI convention drift**: fishing normalised item-name case
at its boundary (`args[0].lower()`), mining did not — an inconsistency invisible
to both suites because each CLI is only ever tested against itself, exactly the
class the driver-parity work (#134) closed for the step-closure twins. A cheap
guard: a shared parametric test that walks EVERY game CLI's item/name entry
point with a capitalised-token input and asserts it resolves identically to its
lowercase form (or is rejected identically), so a new game CLI that forgets to
lower-case reds by construction — the same "one registry, per-row red" shape the
display-table (#123) and help-parity (#125) sweeps already use for their
cross-game invariants.

## ⟲ Previous-session review

Target: games PR #157 (`6f95b9a`, "docs: remove human-gated language — correct
current-state.md + append inbox retraction") — the merge at this branch's base.
Its load-bearing claim (it corrected the one contradictory `docs/current-state.md`
passage so the In-flight banner stops calling merges "human-gated" and instead
records the LIVE auto-merge path, `.github/workflows/auto-merge-enabler.yml`
gated on `substrate-gate`) re-checks TRUE from this session's own evidence, not
its word: the In-flight banner at this HEAD reads "Merges, however, are **NOT
human-gated**: the CI auto-merge apparatus is still **live**… lands the squash
the moment the required `substrate-gate` check passes — no owner click", and the
card's *stated* omission also holds — `control/inbox.md` carries no such
`## CORRECTION` append (its write was classifier-blocked and deferred). The
`.github/workflows/auto-merge-enabler.yml` the banner now cites is present on the
live tree. Documentation-accuracy claim verified against the shipped source.
