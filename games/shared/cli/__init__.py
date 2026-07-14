"""Shared CLI plumbing for the game front-ends.

:mod:`games.shared.cli.repl` owns the ONE interactive-loop implementation
(prompt render, EOF/^C sign-off, quit detection, exit code) that every game
``main()`` previously hand-rolled, and its scripted twin ``run_scripted``
(the banner → feed → quit/end-of-list → closing transcript mechanics every
``run_commands`` / ``run_hub`` previously hand-rolled). Games remain the
callers: this package never imports a game.
"""

from games.shared.cli.repl import StepLike, repl, run_scripted

__all__ = ["StepLike", "repl", "run_scripted"]
