"""CLI command processor."""

from __future__ import annotations

import sys

from ..logger import Logger
from ..commands import Commands


class CommandProcessor:
    def __init__(self, logger: Logger) -> None:
        self.logger = logger

    def process(self, args: list[str]) -> bool:
        """
        Returns True if command handled.
        Returns False if normal pipeline should continue.
        """

        if not args:
            return False

        command = args[0]
        
        if command == Commands.BUILD:
            return False

        if command == Commands.HELP:
            self._help()
            return True

        if command == Commands.VERSION:
            self._version()
            return True

        if command == Commands.SETUP:
            self._setup()
            return True

        self.logger.error(f"Unknown command: {command}")
        self._help()
        sys.exit(1)

    def _help(self) -> None:
        self.logger.menu(
            title="Help",
            usage="flutter-build [command]",
            items=[
                (f"{Commands.SETUP:<15}", "Configure project"),
                (f"{Commands.HELP:<15}", "Show help menu"),
                (f"{Commands.VERSION:<15}", "Show package version"),
            ],
            footer="Use a command to perform a specific action.",
        )

    def _version(self) -> None:
        self.logger.info(
            "Version flutter-build v1.0.0",
            showTime=False
        )

    def _setup(self) -> None:
        self.logger.menu(
            title="Setup",
            items=[
                (f"{'Status':<15}", "Starting configuration wizard..."),
            ],
        )
