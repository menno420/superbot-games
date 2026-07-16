# 2026-07-16 · current-state refresh — docs: re-stamp docs/current-state.md at live HEAD (docs-only)

> **Status:** `in-progress`
>
> 📊 Model: Claude Opus 4.x · high · docs/records

Truth-refresh slice, executed at branch base `197966d` (#150). The living
ledger `docs/current-state.md` was truth-stamped 2026-07-15 at HEAD
`446a84e` (#145) and still claims "PRs through **#145**" and "ZERO open
PRs". Four PRs have merged since that stamp — #146 (`1543c4b`,
merge-automation verification probe), #147 (`8e7acc2`, the prior truth
refresh itself), #148 (`5db902a`, ORDER 010 EAP-extension ack) and #150
(`197966d`, the shared deterministic-RNG seam `games/shared/rng.py`
extracted from mining) — and PR **#149**
(`claude/mirror-reconcile-race-fix`, DRAFT, `do-not-automerge`) is OPEN
awaiting the owner's review+merge. So the ledger's "zero open PRs / through
#145" is stale on both axes.

Scope: re-verify every existing claim in `docs/current-state.md` live at
HEAD and correct what moved — the truth-stamp date/anchor
(2026-07-15/`446a84e` → 2026-07-16/`197966d`), "through #145" → through
#150-with-#149-open, "ZERO open PRs" → the one open PR #149, the suite
count (810 → **821** after #150's `tests/shared/rng/` suite), the ORDER 010
ack ("owed" → LANDED via #148), and the "Recently shipped" list (stops at
#145 → add #146/#147/#148/#150). No code changes; `control/status.md` (the
read-only archive) is deliberately NOT touched — this slice is
`docs/current-state.md` only, plus this card and its claim.

## 💡 Session idea

The two stalest facts this groom fixes are both COUNTS that a machine can
watch: the ledger's "ZERO open PRs" claim (contradicted by live open #149)
and its "through #145" watermark (four merges behind main's #150). The #89
ledger-drift KIT-ASK already proposes comparing the ledger's highest CITED
PR to main's squash subjects (the watermark axis); the missing companion is
an OPEN-PR axis — a check-time advisory (`[ledger-open-pr-drift]`) that
greps the truth-stamp paragraph for an "N open PRs" / "ZERO open PRs"
assertion and compares it against the live `list_pull_requests(state=open)`
count, advisory on mismatch, so a stamp that goes stale the moment a sibling
opens a draft PR surfaces in one finding instead of waiting for a human
groom. Guard-recipe anchor: extend the same stamp-scanning pass the #89
watermark idea targets (`tools/stamp_scaffold.py` reads the
`<!-- truth-stamped-at: -->` anchor already) — one grep of the stamp
paragraph, one API count, one advisory; the open-PR count is the fact this
very session found stale by hand.

## ⟲ Previous-session review

Target: games PR #150 (`claude/shared-rng-seam`, squash `197966d`) — the
newest merged card at this branch's base. Its load-bearing claim
("`games/shared/rng.py` now holds mining's splitmix64 family and both
mining call sites route through it, with mining's produced RNG sequences
byte-identical before/after") is re-checked from this session's own
evidence, not its card's word: `games/shared/rng.py` EXISTS at this HEAD
(`mix64` + `cell_seed`, 2 694 bytes), and its "821 passed" suite claim
REPRODUCES at this HEAD — `python3 -m pytest -q` = 821 passed (see
Close-out), the 810 baseline + its 11 new `tests/shared/rng/` tests. Its
claim-file discipline also verifies: `control/claims/` at this base carries
only the README + the still-un-swept `claude-shared-rng-seam.md` /
`claude-eap-ack.md` / `claude-truth-refresh.md` leftovers (the last two are
stale — their work merged as #147/#148 and PR #149 is already deleting them;
out of THIS slice's scope, flagged not touched). One standing ding carried
forward: #150's own 💡 (a `tests/shared/rng` cross-family pin that every
seam claiming the mining `0x9E3779B97F4A7C15` family routes through
`games.shared.rng.mix64` rather than re-inlining it) is still unbuilt at
this HEAD, so fishing's clean copy can still drift silently.

## ✅ Close-out — Verification

_(filled by the flip-to-complete commit.)_
