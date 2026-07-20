# 2026-07-20 · order-012-kit-games-dewall — turn PR #183 substrate-gate + tests green (kit v1.20.1)

> **Status:** `complete`
>
> 📊 Model: Opus 4.8 · medium · mechanical refactor — land kit v1.20.1 gate-green

ORDER 012 (control/inbox.md, 2026-07-20): the substrate-kit v1.20.1 upgrade
PR #183 was red on both its `substrate-gate` and its sibling `tests` check.
Verified against live GitHub at head `c2ce396` — three exit-affecting items,
all resident-owned and pre-existing / upgrade-induced, none introduced by the
distribution PR. Fix per the ORDER recipe (fleet-manager d0e16e2 style): plain
ADDITIVE commits on the foreign PR branch — no force-push, no rebase.

## What happened

- **Root cause of the two red checks, confirmed from the live CI logs (not the
  nudge's summary):** the `tests` job failed on
  `tests/tools/test_preflight.py:331` `assert "designed hold" in proc.stdout`.
  Under v1.20.1 the `--session-log` explicit-card path prints "designed hold"
  only from the born-red HOLD *banner*, and that banner is reached ONLY when
  the repo tree is otherwise clean of blocking findings. On `c2ce396` the two
  false-wall doc lines are still present, so `check --strict` reports THOSE and
  never reaches the banner — hence "designed hold" is absent from CI stdout and
  the assertion fails. The robust replacement is the missing-sections wording
  the `--session-log` path ALWAYS emits for an in-progress card:
  `"a completed Status (badge still says in-progress)"`.
- Confirmed the strict gate STILL HOLDS RED on a synthetic in-progress card
  under v1.20.1 (exit 1) — only the reachable wording changed, not the hold
  behaviour. No regression.
- `tests/tools/test_preflight.py:331`: `"designed hold"` →
  `"a completed Status"` (comment records the v1.20.1 rewording + why the new
  substring is tree-state-independent).
- `docs/current-state.md:102`: reframed the 2026-07-21 read-only date as a
  platform-wide repo freeze (a repo-level event, not an agent-capability
  limit); dated past-tense fact, 2026-07-20.
- `docs/gen2-custom-instructions-exploration.md:73`: reframed the
  tag/release/branch-delete 403 as a dated past-tense observation limited to
  those three ops, noting ordinary push/merge is normal agent work.
- Verify: `python3 -m pytest -q` → 940 passed. `python3 bootstrap.py check
  --strict` → exit 0 (all three exit-affecting findings cleared; only
  allowlist/advisory items remain). Ran the substrate-gate added-card command
  against this card locally: complete + well-formed → passes.

💡 Session idea: the "kit-upgrade test coupling" class (a resident test pinning
a kit's exact stdout prose) silently reds every upgrade PR — worse, the prose
it pins can be tree-state-dependent (the "designed hold" banner only prints on
an otherwise-clean tree), so the assertion breaks for a *second-order* reason.
The kit could expose the HOLD reason as a stable machine-readable token (e.g. a
`HOLD:in-progress` marker line) so adopter tests assert on the token, never on
release-free prose.

⟲ Previous-session review: the prior session's born-red card correctly named
the two false-walls but pinned item 3 to the surface symptom ("v1.20.1 reworded
the HOLD line"); reading the live CI log this session showed the deeper cause
(the banner is unreachable while the false-walls stand), which confirms the new
substring must come from the always-emitted `--session-log` report, not the
banner — the fix is correct and now robust.
