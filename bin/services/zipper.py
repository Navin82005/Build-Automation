"""Service layer — folder → ZIP archive."""

from __future__ import annotations

import os
import zipfile
from pathlib import Path

from ..logger import Logger


class ZipService:
    """Compresses a folder into a deflate-compressed .zip archive."""

    def __init__(self, logger: Logger) -> None:
        self._log = logger

    def zip_folder(self, folder_path: str, output_path: str) -> str:
        """
        Walk *folder_path* recursively and write every file into *output_path*.

        Returns *output_path* for convenience.
        """
        self._log.info(
            f"Zipping: {Path(folder_path).name}  →  {Path(output_path).name}"
        )

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    arc_name  = os.path.relpath(
                        full_path, os.path.join(folder_path, "..")
                    )
                    zf.write(full_path, arc_name)

        size_mb = os.path.getsize(output_path) / 1_048_576
        self._log.success(f"Archive created ({size_mb:.2f} MB)")
        return output_path
