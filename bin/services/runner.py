"""Service layer — shell command runner with live stdout streaming."""

from __future__ import annotations

import subprocess

from ..colours import DIM, _c
from ..logger import Logger


class CommandRunner:
    """Runs a shell command, streaming every output line to the terminal."""

    def __init__(self, logger: Logger) -> None:
        self._log = logger

    def run(self, command: str, cwd: str | None = None) -> int:
        """
        Execute *command* (via the shell) in optional *cwd*.

        Returns the process exit code; never raises on non-zero exit so that
        the pipeline layer can decide whether to abort or continue.
        """
        self._log.command(command)

        process = subprocess.Popen(
            command,
            cwd=cwd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        for line in process.stdout:  # type: ignore[union-attr]
            print(f"      {_c(DIM, line.rstrip())}")

        process.wait()
        return process.returncode
