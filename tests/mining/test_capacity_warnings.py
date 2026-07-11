"""Byte-identical guard for the Q-0267 capacity-warning data extraction (mining R2).

``capacity.pack_warning`` / ``vault_warning`` used to weld their emoji + copy into
inline f-strings; the strings now live in a module-level ``_CAP_WARNING`` table
(mirroring ``grid._STRIKE_NOTE`` and the merged ``encounters._NARRATION``). This
suite pins the *exact* rendered strings so the relocation is provably a pure move:

1. **Snapshot** — the two warnings render byte-identical to their pre-extraction
   literals across fixed :class:`~games.mining.core.capacity.CapStatus` inputs
   (captured green against the unmodified code to lock the baseline).
2. **Threshold logic untouched** — under-cap → ``None`` (no warning), unchanged.
3. **Copy flows through the data table** — swapping a ``_CAP_WARNING`` row changes
   only the string; the numbers still come from the ``CapStatus``.
"""

from __future__ import annotations

from games.mining.core import capacity

# Byte-identical snapshots of the pre-extraction f-strings, captured against the
# unmodified resolver. Any drift here means the refactor changed player output.
_PACK_FULL = (
    "⚠️ Your pack is full (**40/40** item types) — "
    "stash spare loot at the 🏦 Vault to keep mining tidy."
)
_VAULT_OVER = (
    "⚠️ Your vault is over capacity (**31/30** item "
    "types) — `!vaultupgrade` adds more room."
)


def test_pack_warning_byte_identical() -> None:
    """A full pack renders the exact pre-extraction nudge (emoji + counts + copy)."""
    status = capacity.CapStatus(used=40, cap=40)
    assert status.at_cap is True
    assert capacity.pack_warning(status) == _PACK_FULL


def test_vault_warning_byte_identical() -> None:
    """An over-capacity vault renders the exact pre-extraction nudge."""
    status = capacity.CapStatus(used=31, cap=30)
    assert status.over_cap is True
    assert capacity.vault_warning(status) == _VAULT_OVER


def test_warnings_stay_none_below_threshold() -> None:
    """The gentle-nudge thresholds are untouched: under cap → no warning."""
    # pack warns only *at* cap; vault warns only *over* cap.
    assert capacity.pack_warning(capacity.CapStatus(used=39, cap=40)) is None
    assert capacity.vault_warning(capacity.CapStatus(used=30, cap=30)) is None


def test_warning_copy_lives_in_the_data_table() -> None:
    """Swapping a ``_CAP_WARNING`` row re-skins the copy while the counts still
    come from the ``CapStatus`` — the table is the only string source."""
    status = capacity.CapStatus(used=40, cap=40)
    original = capacity._CAP_WARNING["pack"]
    try:
        capacity._CAP_WARNING["pack"] = "PACK FULL: {used}/{cap}"
        assert capacity.pack_warning(status) == "PACK FULL: 40/40"
    finally:
        capacity._CAP_WARNING["pack"] = original
    # restored → byte-identical again.
    assert capacity.pack_warning(status) == _PACK_FULL
