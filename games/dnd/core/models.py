"""The bounded-menu dataclasses (design §4.1) — the schema the DM law binds.

A :class:`Scene` presents a hard-capped list of :class:`MenuOption`. Each option
carries a stable ``id`` (mechanics key on THIS), a ``text_key`` (a neutral id into
the theme catalog — NOT copy, Q-0267), and an ``effect_id`` (an id into
:data:`games.dnd.core.effects.EFFECTS`, a PRE-DEFINED pre-priced transition). No
option field can hold an amount, a reward, or free text — the only number-bearing
thing is an id into a code-owned registry.

:class:`DMChoice` is the ENTIRE payload the AI DM may return: one ``option_id`` plus
optional DISPLAY-ONLY ``flavor``. The resolver validates and clamps it (design §4.4).
"""

from __future__ import annotations

from dataclasses import dataclass

from .effects import EFFECTS

MAX_MENU_SIZE = 4  # hard cap on options in ANY scene (matches leverage.MAX_MENU_WIDTH)
FLAVOR_CAP = 240  # DM flavour text is length-capped and DISPLAY-ONLY (never parsed)


@dataclass(frozen=True)
class MenuOption:
    """One pre-approved button. Mechanics key on ``id``; copy lives in the catalog."""

    id: str  # stable option id, e.g. "advance_escort" — the mechanics key
    text_key: str  # neutral id into data/scenes.py copy — NOT the copy itself (Q-0267)
    effect_id: str  # id into effects.EFFECTS — a PRE-DEFINED, PRE-PRICED transition


@dataclass(frozen=True)
class Scene:
    """A hard-capped menu of options with a designated safe no-op default (§4.1)."""

    scene_id: str
    context_key: str  # neutral id -> scene prose in the theme catalog (Q-0267)
    options: tuple[MenuOption, ...]  # 1..MAX_MENU_SIZE, hard-capped below
    default_option_id: str  # the safe no-op clamp target (§4.4) — always ON the menu

    def __post_init__(self) -> None:
        # Hard cap: the menu can never exceed MAX_MENU_SIZE options.
        assert 1 <= len(self.options) <= MAX_MENU_SIZE, (
            f"scene {self.scene_id!r}: menu size {len(self.options)} out of "
            f"1..{MAX_MENU_SIZE}"
        )
        ids = [o.id for o in self.options]
        # Option ids must be unique so the mechanics key is unambiguous.
        assert len(set(ids)) == len(ids), f"scene {self.scene_id!r}: duplicate option ids"
        # The clamp target is always a real option on the menu (design §4.1/§4.4).
        assert self.default_option_id in set(ids), (
            f"scene {self.scene_id!r}: default_option_id {self.default_option_id!r} "
            f"is not on the menu"
        )
        # Every option references a PRE-DEFINED effect — no undefined outcomes ship.
        for opt in self.options:
            assert opt.effect_id in EFFECTS, (
                f"scene {self.scene_id!r}: option {opt.id!r} references unknown "
                f"effect_id {opt.effect_id!r}"
            )

    def option(self, option_id: str) -> MenuOption:
        """Return the option with ``option_id`` or raise ``KeyError``."""
        for opt in self.options:
            if opt.id == option_id:
                return opt
        raise KeyError(f"scene {self.scene_id!r}: no option {option_id!r}")


@dataclass(frozen=True)
class DMChoice:
    """The AI DM's ENTIRE return payload: one option id + optional display flavour.

    That is the model's whole authority (design §4.3). ``flavor`` is DISPLAY-ONLY —
    the resolver length-caps it and NEVER parses it for mechanics (§4.4).
    """

    option_id: str
    flavor: str = ""


__all__ = ["MAX_MENU_SIZE", "FLAVOR_CAP", "MenuOption", "Scene", "DMChoice"]
