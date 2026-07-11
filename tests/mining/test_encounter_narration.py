"""Behaviour-preservation guard for the Q-0267 narration-data extraction.

The encounter resolver's player-visible strings (and the "creature" noun) moved
out of the ``_resolve_*`` branches into a module-level ``_NARRATION`` data table
(theme-audit leak #1, roadmap R1). This suite proves that move was a **pure
relocation**:

1. **Golden characterization** — a fixture captured from the *pre-change* resolver
   pins the FULL :class:`EncounterOutcome` (kind, resolution, rewards, damage,
   energy_cost, **and** narration) byte-identical across a fixed sweep. Post-change
   the sweep must reproduce it exactly → outcomes AND copy unchanged.
2. **Narration flows through data** — swapping a ``_NARRATION`` row changes only the
   narration string; every outcome field stays identical.
3. **No inline player-strings** — the ``_resolve_*`` source carries no player-facing
   string literal; all copy comes from the table.

See ``docs/audit/theme-slot-readiness-2026-07-11.md`` §6–§7 (the integrity floor
and verification recipes) for the discipline this encodes.
"""

from __future__ import annotations

import inspect
import json
import os
import random

from games.mining.core import encounters, equipment, grid

from tests.mining import _encounter_golden as golden

_FIXTURE = os.path.join(os.path.dirname(__file__), "_encounter_golden.json")


# ---------------------------------------------------------------------------
# 1. Golden characterization — the whole outcome is byte-identical vs pre-change.
# ---------------------------------------------------------------------------
def test_encounter_outcomes_match_golden() -> None:
    """The full sweep (outcome fields + narration) reproduces the captured fixture.

    The fixture was serialised from the resolver *before* the narration-data
    extraction, so an exact match proves the move changed nothing observable:
    same kind/resolution/rewards/damage/energy_cost AND byte-identical copy.
    """
    with open(_FIXTURE, encoding="utf-8") as fh:
        expected = json.load(fh)
    # Round-trip the live records through JSON so tuples/lists compare structurally.
    got = json.loads(json.dumps(golden.sweep_records(), ensure_ascii=False))
    assert len(got) == len(expected)
    for exp, act in zip(expected, got):
        assert act == exp, f"outcome drift at {exp[0]}: {act[1]} != {exp[1]}"


def test_golden_fixture_covers_every_branch() -> None:
    """The fixture actually exercises all seven narration slots (guard vs a lean sweep)."""
    with open(_FIXTURE, encoding="utf-8") as fh:
        rows = [rec[1] for rec in json.load(fh)]
    narrations = {r[5] for r in rows}
    for template in encounters._NARRATION.values():
        # Every table template's fixed prefix must appear in some captured string.
        stem = template.split("{")[0]
        assert any(n.startswith(stem) for n in narrations), template


# ---------------------------------------------------------------------------
# 2. Narration flows through the data table (swap a row → only copy changes).
# ---------------------------------------------------------------------------
def test_narration_comes_from_the_data_table() -> None:
    """Swapping a ``_NARRATION`` row re-skins the copy while every outcome field
    (kind, resolution, rewards, damage, energy_cost) stays byte-identical — the
    proof that the table is the *only* narration source, mechanics-neutral."""
    treasure = grid.Cell(0, 0, 5, grid.CellFeature.TREASURE, "gold", 2.0)
    lucky = equipment.EffectiveStats(luck=3, loot_bonus=2)
    before = encounters.resolve(3, treasure, lucky)
    assert before.kind is encounters.EncounterKind.LOOT_CACHE  # branch actually hit

    original = encounters._NARRATION[encounters._Narration.LOOT_CACHE]
    try:
        encounters._NARRATION[encounters._Narration.LOOT_CACHE] = "REEF STASH: {amount}x {item}"
        after = encounters.resolve(3, treasure, lucky)
    finally:
        encounters._NARRATION[encounters._Narration.LOOT_CACHE] = original

    # Only the narration changed; every deterministic outcome field is identical.
    assert after.narration == f"REEF STASH: {before.rewards[0].amount}x {before.rewards[0].item}"
    assert after.narration != before.narration
    assert (after.kind, after.resolution, after.rewards, after.damage_taken, after.energy_cost) == (
        before.kind,
        before.resolution,
        before.rewards,
        before.damage_taken,
        before.energy_cost,
    )


def test_creature_noun_lives_in_data() -> None:
    """The enemy noun is a swappable data row, not baked into the resolver: re-skin
    it and every hazard-with-a-monster narration follows, outcome untouched."""
    cell = grid.Cell(0, 0, 8, grid.CellFeature.NORMAL, "iron", 1.0)
    # Find a fixed rng stream that yields a monster-bearing hazard string.
    seed = next(
        s
        for s in range(200)
        if "{creature}" in _slot_template(encounters.resolve(1, cell, rng=random.Random(s)))
    )
    before = encounters.resolve(1, cell, rng=random.Random(seed))
    original = encounters._CREATURE_NOUN
    try:
        encounters._CREATURE_NOUN = "abomination"
        after = encounters.resolve(1, cell, rng=random.Random(seed))
    finally:
        encounters._CREATURE_NOUN = original
    assert "creature" in before.narration and "abomination" in after.narration
    assert (after.kind, after.resolution, after.damage_taken, after.energy_cost) == (
        before.kind,
        before.resolution,
        before.damage_taken,
        before.energy_cost,
    )


def _slot_template(out: encounters.EncounterOutcome) -> str:
    """Reverse-map an outcome's narration to its table template (test helper)."""
    for slot, tmpl in encounters._NARRATION.items():
        stem = tmpl.split("{")[0]
        if out.narration.startswith(stem) and stem:
            return tmpl
    return ""


# ---------------------------------------------------------------------------
# 3. No inline player-strings survive in the resolver branches.
# ---------------------------------------------------------------------------
def test_resolvers_contain_no_inline_player_strings() -> None:
    """Each ``_resolve_*`` body emits copy only via ``_narrate`` — no string literal
    with a space (the shape of player prose) remains inline. Guards against a new
    branch shipping an inline string without a table row (audit §7 recipe #1)."""
    import ast

    src = inspect.getsource(encounters)
    tree = ast.parse(src)
    offenders: list[str] = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.FunctionDef) and node.name.startswith("_resolve_")):
            continue
        docstring = ast.get_docstring(node, clean=False)  # excluded — not player copy
        for sub in ast.walk(node):
            if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                if sub.value == docstring:
                    continue
                # A player string is prose: contains a space. Neutral tokens/ids don't.
                if " " in sub.value:
                    offenders.append(f"{node.name}: {sub.value!r}")
    assert not offenders, offenders


def test_every_emittable_narration_has_a_table_row() -> None:
    """The resolver can only emit strings assembled from ``_NARRATION`` — the set of
    slots equals the set the branches use (no orphan copy, no missing row)."""
    # _NONE_OUTCOME plus the four _resolve_* fns cover exactly the seven slots.
    assert set(encounters._NARRATION) == set(encounters._Narration)
    assert len(encounters._NARRATION) == 7
    # Baseline narration is table-sourced.
    assert encounters._NONE_OUTCOME.narration == encounters._NARRATION[encounters._Narration.NONE]
