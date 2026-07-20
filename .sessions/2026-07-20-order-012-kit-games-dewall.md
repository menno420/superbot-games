# 2026-07-20 · order-012-kit-games-dewall — turn PR #183 substrate-gate + tests green (kit v1.20.1)

> **Status:** `in-progress`
>
> 📊 Model: Opus 4.8 · medium · mechanical refactor — land kit v1.20.1 gate-green

ORDER 012 (control/inbox.md, 2026-07-20): PR #183 (substrate-kit v1.20.1
distribution upgrade) is red on its `substrate-gate` and its sibling `tests`
check. This born-red heartbeat opens the session; the close-out and the three
fixes land in the flip-to-complete commit.

## What is about to happen

Verified against live GitHub at head `c2ce396`: three exit-affecting items, all
resident-owned / upgrade-induced, none introduced by the distribution PR — two
false-wall doc lines (docs/current-state.md:102,
docs/gen2-custom-instructions-exploration.md:73) and one kit-upgrade test
coupling (tests/tools/test_preflight.py:331 pins the old kit's "designed hold"
wording). Fix per the ORDER recipe (fleet-manager d0e16e2 style): plain
ADDITIVE commits on the foreign PR branch — no force-push, no rebase.

💡 Session idea: (recorded at close-out.)

⟲ Previous-session review: (recorded at close-out.)
