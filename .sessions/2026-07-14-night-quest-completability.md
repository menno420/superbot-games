# 2026-07-14 · night test — test: exploration quest catalog — every quest completable within budget

> **Status:** in-progress
>
> 📊 Model: Fable · 2026-07-14T04:26:20Z · night-quest-completability

Test slice from #129's card idea: every quest in
`games/exploration/quest/catalog.py` × offered RewardTier is walked to
COMPLETED via the real seam (`services/exploration_workflow`) within the
quest's own declared budget (sum of its objectives' `required` counts),
fixed world seed, iterations bounded by the budget — never unbounded. An
uncompletable quest×tier is a HEADLINE (pinned + reported, not deleted).
≤10 collected tests, runtime well under 5s.

## 💡 Session idea

(pending — filled at flip)

## ⟲ Previous-session review

(pending — filled at flip)
