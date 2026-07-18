"""Cross-CLI case-normalisation sweep — guards the #158 drift class.

PR #158 fixed a real bug: the standalone mining CLI silently failed on a
CAPITALISED item/branch token (``sell Iron`` falsely read "0 held") because it
never lower-cased the token before the seam's lowercase-keyed lookups. That is a
DRIFT CLASS, not a one-off — any game CLI that forwards a name/id token to a
lowercase-keyed seam without normalising case can regress the same way, and no
single-CLI test would catch it (that is exactly how #158's bug shipped).

This module is the sweep that pins the invariant across every game CLI: for each
CLI, drive its REAL scripted entry point once with a lowercase token and once
with the same token CAPITALISED, and assert the two runs produce an IDENTICAL
committed outcome (same state delta, same audit-row count). Each adapter also
asserts its lowercase baseline actually COMMITTED something, so a CLI that
silently no-ops on BOTH cases cannot pass the sweep vacuously.

Covered (all normalise at the CLI boundary):

* mining      — ``sell <item>``    (``_split_item_qty`` lower-cases; #158)
* fishing     — ``sell <species>`` (``args[0].lower()``)
* exploration — ``offer <id>``     (lower-cased at the boundary in this PR — the
  sweep surfaced that it previously did NOT, the same latent #158 bug)

Gap (tracked as a follow-up, xfailed below):

* dnd — a bounded-menu pick treats a capitalised option id as OFF-MENU and
  clamps to the scene's safe default BY DESIGN ("anything off-menu keeps you
  safe"). Folding case-variant option ids into exact matches is a
  product-semantics decision, not the mechanical ``.lower()`` the other CLIs
  take, so it is deferred rather than forced.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import pytest

from services.audit import InMemorySink

FIXED_NOW = datetime(2026, 7, 13, 12, 0, 0, tzinfo=timezone.utc)


@dataclass(frozen=True)
class Outcome:
    """A committed-effect signature two runs of one CLI can be compared on.

    ``records`` is the number of audit rows the run recorded; ``effect`` is the
    game-specific committed state delta. Two runs match only when BOTH agree.
    """

    records: int
    effect: tuple

    @property
    def committed(self) -> bool:
        """True when the run actually committed a mutation (recorded a row)."""
        return self.records >= 1


# ---------------------------------------------------------------------------
# Per-CLI adapters — each drives the REAL scripted entry point with *token* in
# an item/branch/id position and returns the run's committed-effect signature.
# ---------------------------------------------------------------------------
def _mining_outcome(token: str) -> Outcome:
    from games.mining.cli import new_state, run_commands

    state = new_state(now=FIXED_NOW)
    state.inventory = {"iron": 5}
    sink = InMemorySink()
    result = run_commands([f"sell {token} 2", "quit"], sink=sink, state=state, now=FIXED_NOW)
    return Outcome(
        records=len(sink.records),
        effect=(result.state.coins, result.state.inventory.get("iron")),
    )


def _fishing_outcome(token: str) -> Outcome:
    from games.fishing.cli import new_state, run_commands

    state = new_state()
    state.haul = {"bass": 3}
    sink = InMemorySink()
    result = run_commands([f"sell {token} 2", "quit"], sink=sink, state=state, now=FIXED_NOW)
    return Outcome(
        records=len(sink.records),
        effect=(result.state.coins, result.state.haul.get("bass")),
    )


def _exploration_outcome(token: str) -> Outcome:
    from games.exploration.cli import run_commands

    sink = InMemorySink()
    result = run_commands([f"offer {token}", "accept", "quit"], sink=sink, now=FIXED_NOW)
    quest = result.state.quest
    return Outcome(
        records=len(sink.records),
        effect=(
            quest.template_id if quest is not None else None,
            quest.state.value if quest is not None else None,
        ),
    )


# ---------------------------------------------------------------------------
# The sweep — every covered CLI must resolve a capitalised token identically to
# its lowercase form (the #158 invariant).
# ---------------------------------------------------------------------------
CLI_CASES = [
    pytest.param(_mining_outcome, "iron", "Iron", id="mining-sell"),
    pytest.param(_fishing_outcome, "bass", "Bass", id="fishing-sell"),
    pytest.param(_exploration_outcome, "supply_run", "Supply_Run", id="exploration-offer"),
]


@pytest.mark.parametrize("outcome_fn, lower, upper", CLI_CASES)
def test_cli_normalises_case_at_the_token_boundary(outcome_fn, lower, upper) -> None:
    lo = outcome_fn(lower)
    hi = outcome_fn(upper)
    # Guard against a vacuous pass: the lowercase baseline must really commit —
    # else "both cases silently no-op" would compare equal and hide the very
    # #158 bug the sweep exists to catch.
    assert lo.committed, (
        f"lowercase baseline {lower!r} did not commit a mutation — the sweep "
        f"would be vacuous; the adapter must drive a real committed action"
    )
    assert hi == lo, (
        f"capitalised token {upper!r} diverged from {lower!r}: {hi} != {lo} — "
        f"the CLI is not normalising case at its token boundary (#158 drift)"
    )


# ---------------------------------------------------------------------------
# The dnd gap — pinned, intentional, and self-healing.
#
# dnd's bounded-menu pick clamps a capitalised (off-menu) option id to the
# scene's safe default BY DESIGN, so its outcome legitimately diverges from the
# exact lowercase pick. Whether the DM's seat should case-fold option ids before
# the clamp is a PRODUCT-SEMANTICS call, deferred as a follow-up (see the session
# card / PR body). ``strict=True`` makes a future fix (dnd starts normalising)
# trip XPASS, forcing this xfail to be removed and dnd folded into the sweep.
# ---------------------------------------------------------------------------
def _dnd_outcome(token: str) -> Outcome:
    from games.dnd.cli import run_commands

    sink = InMemorySink()
    result = run_commands([token, "quit"], sink=sink, now=FIXED_NOW)
    return Outcome(
        records=len(sink.records),
        effect=(result.state.scene_id, result.state.global_xp),
    )


@pytest.mark.xfail(
    strict=True,
    reason=(
        "dnd CLI treats a capitalised option id as OFF-MENU and clamps to the "
        "scene's safe default by design (bounded-menu 'anything off-menu keeps "
        "you safe'); making option-id matching case-insensitive is a "
        "product-semantics call, tracked as a follow-up backlog item — see PR body"
    ),
)
def test_dnd_option_id_is_case_insensitive() -> None:
    lo = _dnd_outcome("advance_escort")
    hi = _dnd_outcome("Advance_Escort")
    assert hi == lo
