# 2026-07-11 · Auto-generated economy balance page + CI freshness guard

> **Status:** `✅ complete`
>
> 📊 Model: Opus 4.8 · 2026-07-11T18:07:38Z · auto-generated balance page

## Goal

Ship `tools/gen_balance.py` — a deterministic, reads-only generator that regenerates
`docs/balance.md` from the shipped catalogs / sim tunables / caps / suite floors so the
owner can eyeball the whole world-games economy on one page — plus a `--check` mode wired
into CI (the same way `tests/check_suite_floors.py` runs) that fails the build if the
committed page drifts from source. No resolver / balance constant may change; the
generator only READS and formats. Branch off `main`, read only on-main sources (the
cross-domain `economy_sim.py` from a sibling in-flight PR is NOT on main — folding its
derived per-hour numbers in is a follow-up once it lands).

## What shipped

- **`tools/gen_balance.py`** — deterministic generator (stdlib + `games.*` imports only,
  side-effect-free on import; all writes behind functions / the `__main__` guard). Puts the
  repo root on `sys.path` so it runs from anywhere. `render()` builds the page from READ
  constants; `write()` writes `docs/balance.md`; `check()` regenerates in memory, prints a
  unified diff, and exits 1 if stale (0 if fresh). Determinism: every dict sorted before
  emit, floats formatted through `_num` (`.4f`, trailing zeros stripped), fixed section
  order, no timestamps / randomness.
- **`docs/balance.md`** — the generated page (badge `> **Status:** `reference``), byte-
  identical to `render()`. Sections: global reward ceiling (`GLOBAL_MAX`), action-rate
  ceilings (mining energy bar + survival `TUNABLES` digs/hr + fishing casts/hr), mining
  (`ORE_WEIGHTS`, roll/tool constants, encounter tunables, per-unit ore coin values,
  storage caps + vault coin-sink costs), fishing (catch resolver constants, species
  weights/ranks, spot bite biases), DND (escort_step tier-I 5/25/10 + which effects mint
  nothing, `MAX_MENU_SIZE`), exploration quests (`TIER_CAPS` I/II/III + leverage menu-width
  constants), test-suite floors table, and a host-gating / economy-sim-follow-up footer.
  Each section notes its source `module.py`.
- **`docs/design/shared-index.md`** — appended a `../balance.md` reference link so the
  docs-gate reachability BFS reaches the new page (matched the index's existing bullet
  style; sibling PRs append here too).
- **`.github/workflows/tests.yml`** — new step **"Balance page freshness"** immediately
  after the test-suite step (same `control_only` guard), running
  `python3 tools/gen_balance.py --check`. No other step touched.
- **Verification:** `--check` exits 0 (fresh); negative proof (append a space → exit 1 +
  diff → regenerate → exit 0); `check_suite_floors.py` passes; full suite green; and
  `bootstrap.py check --strict` EXIT 0 (page badged + reachable). No resolver / balance
  constant changed (generator reads only); `.substrate/guard-fires.jsonl` not committed.

## 💡 Session idea

`gen_balance.py` is a "documentation ratchet": a generator + `--check` CI gate that keeps a
human-readable page provably in sync with code constants. The same pattern would fit any
other scattered-constant surface (e.g. the equipment stat tables, or a future cross-domain
emission budget) — one generator per surface, one freshness step, and the page can never
silently rot. When the economy sim lands on main, its derived per-hour emission numbers
fold into this exact generator rather than a hand-maintained table.

## ⟲ Previous-session review

The inventory-resource-contract session (2026-07-11) mapped the SIX divergent reward/item
shapes across the world games with file:line citations — that map is exactly the source
list this generator reads (mining `rewards`/`encounters`/`items`/`capacity`, fishing
`catch`/`species`/`spots`, quest `catalog`/`leverage`, DND `effects`/`scenes`/`models`).
It confirmed the numbers are scattered but stable and sim-pinned, which is what makes a
deterministic single-page projection safe. This page is the read-only companion to that
plan: the contract proposes unifying the shapes; this page just surfaces today's numbers
so drift is visible while that migration proceeds.

## Guard recipe

- **Regenerate:** `python3 tools/gen_balance.py` (writes `docs/balance.md`).
- **Freshness check (CI):** `python3 tools/gen_balance.py --check` — exit 0 fresh, exit 1 +
  unified diff if the committed page drifted from source. Wired into
  `.github/workflows/tests.yml` right after `python3 tests/check_suite_floors.py`.
- **Negative proof:** append a space to `docs/balance.md` → `--check` exits 1 with a diff;
  `python3 tools/gen_balance.py` restores it → `--check` exits 0.
- **Docs gate:** `python3 bootstrap.py check --strict` must stay EXIT 0 (page needs its
  `reference` Status badge and a reachable link from `docs/design/shared-index.md`).
