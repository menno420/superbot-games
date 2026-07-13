"""``python3 -m games.dnd`` — launch the standalone D&D REPL.

Thin entry point: the whole loop lives in :mod:`games.dnd.cli` (importable and
testable via ``run_commands``); this module only wires it to the process so the
game is playable with one command.
"""

from __future__ import annotations

import sys

from games.dnd.cli import main

if __name__ == "__main__":
    sys.exit(main())
