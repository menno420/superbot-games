"""Message-XP -> DM menu-width leverage.

Message-XP is DM *leverage*: it only widens how MANY story-action options the AI
DM may surface (AG-09 Story Actions = 2-4 whitelisted buttons) — never the reward
amounts, never the outcomes. The width is code-computed, monotonic, and hard-capped
here; the model never decides it (Q-0040 bounded authority).
"""

from __future__ import annotations

BASE_MENU_WIDTH = 2  # AG-09: minimum whitelisted story-action buttons
MAX_MENU_WIDTH = 4  # AG-09: hard cap on whitelisted story-action buttons
XP_PER_EXTRA_OPTION = 500  # message-XP needed to unlock each option beyond BASE


def menu_width(message_xp: int) -> int:
    """Return the number of story-action options the DM may surface.

    Deterministic and monotonic non-decreasing in ``message_xp``: floored at
    ``BASE_MENU_WIDTH``, one extra option per ``XP_PER_EXTRA_OPTION`` earned, hard
    capped at ``MAX_MENU_WIDTH``. Negative/zero XP yields the base width.
    """
    xp = max(0, message_xp)
    extra = xp // XP_PER_EXTRA_OPTION
    width = BASE_MENU_WIDTH + extra
    if width < BASE_MENU_WIDTH:
        return BASE_MENU_WIDTH
    if width > MAX_MENU_WIDTH:
        return MAX_MENU_WIDTH
    return width
