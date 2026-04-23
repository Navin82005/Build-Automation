"""CLI command definitions."""

from __future__ import annotations


class Commands:
    SETUP = "--set-up"
    HELP = "--help"
    VERSION = "--version"
    BUILD = "build"

    ALL = [
        SETUP,
        HELP,
        VERSION,
        BUILD,
    ]

    @classmethod
    def help_text(cls) -> str:
        return f"""
Usage:
    flutter-build <command>

Commands:
    {cls.SETUP:<15} Configure project
    {cls.HELP:<15} Show help
    {cls.VERSION:<15} Show version
""".strip()