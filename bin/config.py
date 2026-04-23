"""Config layer — loads and validates config.json."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).parent.parent  # repo root when installed as a package


class ConfigLoader:
    """Loads and validates config.json, raising clear errors on bad input."""

    REQUIRED_KEYS = [
        "working_path",
        "build_command",
        "output_name",
        "drive_folder_id",
        "email",
    ]
    EMAIL_KEYS = ["sender", "receiver", "smtp_server", "smtp_port", "password"]

    def __init__(self, path: Path | None = None) -> None:
        self._path = path or (SCRIPT_DIR / "config.json")

    # ── public ────────────────────────────────────────────────────────────────

    def load(self) -> dict[str, Any]:
        if not self._path.exists():
            raise FileNotFoundError(f"config.json not found at {self._path}")
        with open(self._path) as fh:
            cfg = json.load(fh)
        self._validate(cfg)
        return cfg

    # ── private ───────────────────────────────────────────────────────────────

    def _validate(self, cfg: dict[str, Any]) -> None:
        missing = [k for k in self.REQUIRED_KEYS if k not in cfg]
        if missing:
            raise ValueError(f"config.json missing top-level keys: {missing}")

        email_missing = [k for k in self.EMAIL_KEYS if k not in cfg.get("email", {})]
        if email_missing:
            raise ValueError(f"config.json [email] section missing keys: {email_missing}")
