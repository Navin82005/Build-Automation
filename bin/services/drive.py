"""Service layer — Google Drive authentication and file upload."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..logger import Logger

# ── optional deps guard ───────────────────────────────────────────────────────
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False

SCOPES     = ["https://www.googleapis.com/auth/drive.file"]
SCRIPT_DIR = Path(__file__).parent.parent.parent   # repo root


class DriveService:
    """
    Handles OAuth2 token management and resumable file upload to Google Drive.

    Raises ``RuntimeError`` on construction if the google-api libraries are not
    installed so the error surfaces early rather than at upload time.
    """

    def __init__(self, logger: Logger) -> None:
        self._log = logger
        if not _AVAILABLE:
            raise RuntimeError(
                "Google Drive libraries are not installed.\n"
                "Run: pip install google-auth google-auth-oauthlib "
                "google-auth-httplib2 google-api-python-client"
            )

    # ── public ────────────────────────────────────────────────────────────────

    def upload(self, file_path: str, folder_id: str) -> str:
        """Upload *file_path* into *folder_id* and return its webViewLink."""
        self._log.info("Uploading to Google Drive…")
        service  = self._get_service()
        metadata = {"name": Path(file_path).name, "parents": [folder_id]}
        media    = MediaFileUpload(file_path, resumable=True)
        result   = (
            service.files()
            .create(body=metadata, media_body=media, fields="id, webViewLink")
            .execute()
        )
        link: str = result["webViewLink"]
        self._log.success(f"Upload complete → {link}")
        return link

    # ── private ───────────────────────────────────────────────────────────────

    def _get_service(self) -> Any:
        token_path = SCRIPT_DIR / "token.json"
        creds_path = SCRIPT_DIR / "credentials.json"
        creds      = None

        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                self._log.info("Refreshing Drive OAuth token…")
                creds.refresh(Request())
            else:
                if not creds_path.exists():
                    raise FileNotFoundError(
                        f"credentials.json not found at {creds_path}.\n"
                        "Download it from the Google Cloud Console and place it "
                        "in the project root."
                    )
                flow  = InstalledAppFlow.from_client_secrets_file(
                    str(creds_path), SCOPES
                )
                creds = flow.run_local_server(port=0)

            token_path.write_text(creds.to_json())

        return build("drive", "v3", credentials=creds)
