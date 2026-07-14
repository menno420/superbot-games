# 2026-07-14 · night test — pin tools/gen_balance: generation, sections, helpers, stale detection

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-14T02:34:09Z · night-cover-gen-balance

Test slice. Provenance stated honestly: this partially implements the
"gen_balance generator pins" card idea from #120's session card
(`.sessions/2026-07-14-night-truth-stamp-anchor.md`) — not novel scope
invented here. Verified unimplemented at main `51590c6`: no test
imported `gen_balance`; `tools/gen_balance.py` sat at 227 statements /
0% coverage while its `--check` step in `.github/workflows/tests.yml`
gates every merge, so a regression in the generator itself would have
surfaced only as an opaque CI failure with no unit pin naming the seam.

Shipped `tests/tools/test_gen_balance.py` (13 tests, in the
already-registered `tests/tools/` suite — no new suite registration, no
overlapping-suite trap): the exact CI seam (`check()` == 0 against the
committed `docs/balance.md` at HEAD, printing nothing when green);
`render()` deterministic and byte-identical to the committed page; all
17 section/subsection headers present in document order; `_num` pins
(int passthrough, negative, bool-guard `True`, `3.0` → `3`, trailing
zeros stripped, 4-decimal rounding, non-number `str()` passthrough);
`_table` GitHub-markdown shape; `_read_floor` whitespace strip;
`write()`→`check()` roundtrip on a tmp path; stale detection (mutated
in-repo copy → `check()` == 1 with `---`/`+++` unified-diff headers +
the "is stale … regenerate" message, probe file removed in `finally`);
missing-file-is-stale; `main()` dispatch (`--check` → 0, unknown flag →
usage on stderr + exit 2).

**Quirk found and pinned (not fixed — reads-only slice):** `check()`
on a stale path OUTSIDE the repo root raises `ValueError` from the
error message's `path.relative_to(_REPO_ROOT)` instead of returning 1.
Latent in practice (CI only ever passes `DOC_PATH`), but the pin
documents it; the trivial fix (fall back to `str(path)` when
`relative_to` fails) is a follow-up, deliberately out of scope for a
test-only slice.

`tests/tools` floor 8 → **21** (pinned to collected, suite convention);
`docs/balance.md` regenerated BEFORE flip so the floors table carries
the bump (gen-balance gate) and `gen_balance.py --check` is green —
this slice's own new tests exercise exactly that freshness. Full suite
703 → **716 passed** locally on this branch; strict check exit 0. Claim
`control/claims/night-cover-gen-balance.md` self-released in this flip
commit (established precedent).

## 💡 Session idea

`gen_balance.py`'s DND section derives its effect→mints table from a
hand-maintained set inside the generator (`minting = {"escort_step"}`,
line ~384): if a NEW minting effect is ever added to
`games/dnd/core/effects.py`, the balance page would silently label it
"nothing (narrate-only)" while it actually grants — a wrong-but-fresh
page that `--check` can never catch, because the lie is generated. Fix
the class, not the instance: make effects carry their grant as data
(each `Effect` declares its bundle or `None`) and have the generator
read it, plus one cross-check test asserting every effect the resolver
can mint through appears as minting on the page. Dedupe check against
the used-idea list: "gen_balance generator pins" (this slice) pins the
generator's mechanics, not the hand-set's truthfulness; the
display-table completeness registry syncs vocab↔display dicts inside a
game, not generator-embedded knowledge against source modules; no card
idea to date targets generated-page semantic drift.

## ⟲ Previous-session review

The previous slice is #120 (`claude/night-truth-stamp-anchor`, born-red
`0822e6a`, flip `506c7c8`, squash-merged to main as `51590c6`).
Verified against live CI: at flip SHA `506c7c8` all three workflows
completed green (tests run 29301174943's sibling — tests 29301174941,
substrate-gate 29301174943, auto-merge-enabler 29301174980), and the
born-red SHA `0822e6a`'s substrate-gate failure (run 29300883269) was
exactly the designed pre-flip HOLD while tests (29300883270) and the
enabler (29300883282) stayed green. Verified against this branch's base
(includes `51590c6`): `docs/current-state.md:25` carries the
machine-readable `<!-- truth-stamped-at: fdea103… -->` anchor exactly
as claimed, `tools/stamp_scaffold.py` exists with its 8-test
`tests/tools/test_stamp_scaffold.py` (this slice collected them:
8 + 13 = 21), and `tests/EXPECTED_SUITES.txt` registers `tests/tools`.
One honest nit: #120's card describes the anchor as "beside" the prose
stamp, but the anchor SHA (`fdea103`) is the pre-#120 groom HEAD — the
prose stamp and anchor deliberately point at the last-groomed commit,
not #120's own merge, which is correct behavior yet easy to misread as
staleness; the card could have said so explicitly.
