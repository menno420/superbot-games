"""Byte-identical guard for the Q-0267 world position/descent copy extraction (R2).

``world.describe_position`` and ``world.descend_hint`` used to weld their player
copy into inline f-strings; the templates now live in module-level tables
(``_POSITION_TEMPLATE`` / ``_DESCEND_HINT``), mirroring ``grid._STRIKE_NOTE`` and
the merged ``encounters._NARRATION``. This suite pins the *exact* rendered strings
so the relocation is provably pure:

1. **Snapshot** — every depth band's position line and every descend hint render
   byte-identical to their pre-extraction literals (captured green against the
   unmodified code to lock the baseline). ``BIOME_LABELS`` / ``BIOME_EMOJI`` were
   already clean data and are unchanged.
2. **Depth-gating logic untouched** — the "deepest bands" branch vs the
   next-band hint still key on ``max_accessible_depth`` and the numbers are intact.
"""

from __future__ import annotations

from games.mining.core import world
from games.mining.core.equipment import EffectiveStats

# Byte-identical snapshots of the pre-extraction f-strings (MAX_DEPTH == 3).
_POSITION = {
    0: "🌳 Surface (depth 0/3)",
    1: "🪨 Cavern (depth 1/3)",
    2: "💎 the Deep (depth 2/3)",
    3: "🌋 the Magma core (depth 3/3)",
}
_HINT_NEXT = {
    0: "Equip a brighter light to descend to Cavern (needs depth access 1).",
    1: "Equip a brighter light to descend to the Deep (needs depth access 2).",
    2: "Equip a brighter light to descend to the Magma core (needs depth access 3).",
}
_HINT_MAX = "You have the gear to reach the deepest bands."


def test_describe_position_byte_identical() -> None:
    """Each band's ``<emoji> <Label> (depth N/MAX)`` line is byte-identical."""
    assert world.MAX_DEPTH == 3
    for depth, expected in _POSITION.items():
        assert world.describe_position(depth) == expected
    # depth clamps to the band range, copy unchanged.
    assert world.describe_position(99) == _POSITION[3]


def test_descend_hint_next_band_byte_identical() -> None:
    """The next-band unlock hint is byte-identical at every reachable depth."""
    for access, expected in _HINT_NEXT.items():
        assert world.descend_hint(EffectiveStats(depth_access=access)) == expected


def test_descend_hint_at_max_depth_byte_identical() -> None:
    """Full-reach gear renders the exact 'deepest bands' line (no next-band hint)."""
    assert world.descend_hint(EffectiveStats(depth_access=world.MAX_DEPTH)) == _HINT_MAX
    assert world.descend_hint(EffectiveStats(depth_access=99)) == _HINT_MAX


def test_position_copy_lives_in_the_data_table() -> None:
    """Swapping ``_POSITION_TEMPLATE`` re-skins the line while numbers/labels still
    come from the biome data — the template is the only string source."""
    original = world._POSITION_TEMPLATE
    try:
        world._POSITION_TEMPLATE = "{label} @ {depth} of {max_depth}"
        assert world.describe_position(1) == "🪨 Cavern @ 1 of 3"
    finally:
        world._POSITION_TEMPLATE = original
    assert world.describe_position(1) == _POSITION[1]
