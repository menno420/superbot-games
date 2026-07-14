# 2026-07-14 · night build — ci: preflight --flip derives the session card from the branch diff

> **Status:** in-progress
>
> 📊 Model: Fable · 2026-07-14T04:40:39Z · night-flip-card-parity

Build slice from #131's card idea: `--flip`'s step 4 runs bare
`bootstrap.py check --strict`, inheriting strict's newest-by-mtime card
selection (`latest_session_log`) — the wrong card exactly when it matters
(touched bystander card, fresh checkout flattening mtimes). Make `--flip`
derive the card deterministically from the branch's own diff
(`git diff --name-only --diff-filter=A origin/main...HEAD -- .sessions/`)
and pass it via strict's existing `--session-log` flag: one added card →
graded explicitly; multiple added cards → loud error; zero added cards
(control-fast-lane tree) → today's bare behavior behind a clear banner.
Unit tests for all three paths, in-process per the #131 pattern.

## 💡 Session idea

(pending — filled at flip)

## ⟲ Previous-session review

(pending — filled at flip)
