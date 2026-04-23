"""Entry-point — wires all layers together and runs the pipeline."""

from __future__ import annotations

import sys

from .config   import ConfigLoader
from .logger   import Logger
from .pipeline import BuildPipeline
from .prompter import Prompter
from .services import CommandRunner, DriveService, EmailService, ZipService, CommandProcessor


def main() -> None:
    logger = Logger()
    logger.banner()
    commandProcessor = CommandProcessor(logger)
    
    if (len(sys.argv) > 1):
        isCommand = commandProcessor.process(args=sys.argv[1:])
        if (isCommand):
            return

    # ── Configuration ─────────────────────────────────────────────────────────
    logger.section("Loading Configuration")
    try:
        config = ConfigLoader().load()
    except (FileNotFoundError, ValueError) as exc:
        logger.error(str(exc))
        logger.info("Use flutter-build --set-up to setup config")
        sys.exit(1)
    logger.success(
        f"Project: {config['output_name']}  |  Path: {config['working_path']}"
    )

    # ── Service wiring ────────────────────────────────────────────────────────
    prompter = Prompter(timeout=config.get("prompt_timeout", 15))
    runner   = CommandRunner(logger)
    zipper   = ZipService(logger)
    drive    = DriveService(logger)
    mailer   = EmailService(config, logger)

    pipeline = BuildPipeline(
        config, logger, prompter, runner, zipper, drive, mailer
    )

    # ── Execute ───────────────────────────────────────────────────────────────
    logger.section("Starting Pipeline")
    try:
        pipeline.run()
    except Exception as exc:
        pipeline.handle_error(exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
