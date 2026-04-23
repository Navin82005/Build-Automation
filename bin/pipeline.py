"""Pipeline layer — orchestrates the full Flutter build flow."""

from __future__ import annotations

import os
import traceback
from datetime import datetime
from pathlib import Path

from .colours import BOLD, _c
from .logger import Logger
from .prompter import Prompter
from .services import CommandRunner, DriveService, EmailService, ZipService


class BuildPipeline:
    """
    Owns the end-to-end build sequence:

      1. Prompt → flutter clean
      2. Prompt → flutter pub get
      3. Prompt → pod install  (only when ios/ folder is present)
      4. Prompt → build_runner
      5. Prompt → main build command
      6. Zip the .app output
      7. Upload to Google Drive
      8. Email a success notification
    """

    def __init__(
        self,
        config: dict,
        logger: Logger,
        prompter: Prompter,
        runner: CommandRunner,
        zipper: ZipService,
        drive: DriveService,
        mailer: EmailService,
    ) -> None:
        self._cfg      = config
        self._log      = logger
        self._prompter = prompter
        self._runner   = runner
        self._zipper   = zipper
        self._drive    = drive
        self._mailer   = mailer

    # ── public ────────────────────────────────────────────────────────────────

    def run(self) -> None:
        project_path = self._cfg["working_path"]
        os.chdir(project_path)
        start_time = datetime.now()

        steps = self._build_steps(project_path)
        total = len(steps)

        for idx, (label, cmd, key) in enumerate(steps, start=1):
            self._log.step(idx, total, label)
            self._run_step(label, cmd, key, cwd=project_path)

        # ── Package ──────────────────────────────────────────────────────────
        self._log.section("Packaging Artefact")
        app_path  = self._locate_build_output()
        zip_name  = f"{self._cfg['output_name']}.zip"
        zip_path  = os.path.join(os.path.dirname(app_path), zip_name)
        final_zip = self._zipper.zip_folder(app_path, zip_path)

        # ── Upload ───────────────────────────────────────────────────────────
        self._log.section("Uploading to Google Drive")
        link = self._drive.upload(final_zip, self._cfg["drive_folder_id"])

        # ── Summary ──────────────────────────────────────────────────────────
        elapsed = str(datetime.now() - start_time).split(".")[0]
        self._log.result_box({
            "Artefact":       zip_name,
            "Drive Link":     link,
            "Total Duration": elapsed,
        })

        # ── Notify ───────────────────────────────────────────────────────────
        self._log.section("Sending Notification")
        self._mailer.send_success(zip_name, link, elapsed)
        self._log.success("All done! 🎉")

    def handle_error(self, exc: BaseException) -> None:
        """Log the exception and dispatch a failure email."""
        details = traceback.format_exc()
        self._log.error(str(exc))
        self._log.section("Sending Failure Notification")
        self._mailer.send_failure(details)

    # ── private ───────────────────────────────────────────────────────────────

    def _build_steps(self, project_path: str) -> list[tuple[str, str, str]]:
        """Return the ordered list of (label, command, fallback_key) tuples."""
        steps: list[tuple[str, str, str]] = [
            ("flutter clean",           "flutter clean",            "clean"),
            ("flutter pub get",         "flutter pub get",          "pub_get"),
            (
                "flutter pub run build_runner",
                "flutter pub run build_runner build --delete-conflicting-outputs",
                "build_runner",
            ),
            (
                self._cfg["build_command"],
                self._cfg["build_command"],
                "main_build",
            ),
        ]
        if os.path.exists(os.path.join(project_path, "ios")):
            steps.insert(2, (
                "pod install",
                "cd ios && pod install && cd ..",
                "pod_install",
            ))
        return steps

    def _confirm_step(self, label: str, fallback_key: str) -> bool:
        """Ask the user whether to run *label*, honouring the JSON fallback."""
        fallbacks: dict = self._cfg.get("step_fallbacks", {})
        fallback = fallbacks.get(fallback_key, "yes").lower()
        answer   = self._prompter.ask(f"Run step: {_c(BOLD, label)}?", fallback)
        if answer in ("yes", "y", ""):
            return True
        self._log.warning(f"Skipped: {label}")
        return False

    def _run_step(
        self, label: str, command: str, fallback_key: str, cwd: str | None = None
    ) -> None:
        if self._confirm_step(label, fallback_key):
            rc = self._runner.run(command, cwd=cwd)
            if rc != 0:
                self._log.warning(f"'{command}' exited with code {rc} (continuing)")

    def _locate_build_output(self) -> str:
        ios_path = (
            Path(self._cfg["working_path"]) / "build" / "ios" / "iphonesimulator"
        )
        apps = list(ios_path.glob("*.app"))
        if not apps:
            raise FileNotFoundError(f"No .app bundle found in {ios_path}")
        return str(apps[0])
