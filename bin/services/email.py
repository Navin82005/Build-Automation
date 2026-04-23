"""Service layer — HTML email notifications (success & failure)."""

from __future__ import annotations

import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ..logger import Logger


class EmailService:
    """
    Sends production-grade HTML notification emails.

    Two public methods:
      • send_success(zip_name, drive_link, duration)
      • send_failure(error_details)
    """

    def __init__(self, config: dict, logger: Logger) -> None:
        self._cfg     = config["email"]
        self._project = config.get("output_name", "Flutter App")
        self._log     = logger

    # ── public API ────────────────────────────────────────────────────────────

    def send_success(self, zip_name: str, drive_link: str, duration: str) -> None:
        subject = f"✅ Build Succeeded — {self._project}"
        self._send(subject, self._render_success(zip_name, drive_link, duration))

    def send_failure(self, error_details: str) -> None:
        subject = f"❌ Build Failed — {self._project}"
        self._send(subject, self._render_failure(error_details))

    # ── template rendering ────────────────────────────────────────────────────

    @staticmethod
    def _now() -> str:
        return datetime.now().strftime("%d %b %Y, %H:%M:%S")

    def _base_template(
        self, accent: str, badge: str, heading: str, body_html: str
    ) -> str:
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{heading}</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:#0f0f13;font-family:'Segoe UI',Helvetica,Arial,sans-serif;
        color:#c9d1d9;padding:40px 16px}}
  .card{{background:#161b22;border:1px solid #30363d;border-radius:12px;
         max-width:620px;margin:0 auto;overflow:hidden}}
  .header{{background:{accent};padding:28px 32px;display:flex;
            align-items:center;gap:14px}}
  .header .badge{{font-size:32px;line-height:1}}
  .header h1{{font-size:20px;font-weight:700;color:#fff;letter-spacing:.5px}}
  .header p{{font-size:13px;color:rgba(255,255,255,.7);margin-top:4px}}
  .body{{padding:28px 32px}}
  .row{{display:flex;justify-content:space-between;align-items:center;
        padding:10px 0;border-bottom:1px solid #21262d}}
  .row:last-child{{border-bottom:none}}
  .label{{font-size:12px;text-transform:uppercase;letter-spacing:.8px;
           color:#8b949e;font-weight:600}}
  .value{{font-size:13px;color:#e6edf3;text-align:right;word-break:break-all}}
  .btn{{display:inline-block;margin-top:22px;padding:11px 26px;
        background:{accent};color:#fff;font-size:14px;font-weight:600;
        border-radius:8px;text-decoration:none;letter-spacing:.3px}}
  .footer{{padding:18px 32px;border-top:1px solid #21262d;
           font-size:11px;color:#484f58;text-align:center}}
  pre{{background:#0d1117;border:1px solid #30363d;border-radius:8px;
       padding:16px;font-size:12px;overflow-x:auto;white-space:pre-wrap;
       word-break:break-all;color:#f85149;margin-top:18px;line-height:1.6}}
</style>
</head>
<body>
<div class="card">
  <div class="header">
    <span class="badge">{badge}</span>
    <div>
      <h1>{heading}</h1>
      <p>{self._project} &nbsp;·&nbsp; {self._now()}</p>
    </div>
  </div>
  <div class="body">{body_html}</div>
  <div class="footer">
    This message was generated automatically by Flutter Build Automation.<br/>
    Do not reply directly to this email.
  </div>
</div>
</body>
</html>"""

    def _render_success(
        self, zip_name: str, drive_link: str, duration: str
    ) -> str:
        rows = [
            ("Status",   "✔ Succeeded"),
            ("Artifact", zip_name),
            ("Duration", duration),
            ("Uploaded", self._now()),
        ]
        rows_html = "\n".join(
            f'<div class="row">'
            f'<span class="label">{label}</span>'
            f'<span class="value">{value}</span>'
            f'</div>'
            for label, value in rows
        )
        body = f"""
<p style="font-size:14px;color:#8b949e;margin-bottom:18px">
  Your Flutter build completed successfully. The artefact has been uploaded to
  Google Drive and is ready to download or share.
</p>
{rows_html}
<a class="btn" href="{drive_link}" target="_blank">Open in Google Drive →</a>
"""
        return self._base_template(
            accent="#1f6feb", badge="🚀",
            heading="Build Succeeded", body_html=body,
        )

    def _render_failure(self, error_details: str) -> str:
        safe = (
            error_details
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        body = f"""
<p style="font-size:14px;color:#8b949e;margin-bottom:18px">
  The Flutter build pipeline encountered an unhandled exception and was
  terminated. Review the trace below and fix the issue before re-triggering.
</p>
<div class="row">
  <span class="label">Status</span>
  <span class="value" style="color:#f85149">✖ Failed</span>
</div>
<div class="row">
  <span class="label">Time</span>
  <span class="value">{self._now()}</span>
</div>
<pre>{safe}</pre>
"""
        return self._base_template(
            accent="#b91c1c", badge="🔴",
            heading="Build Failed", body_html=body,
        )

    # ── SMTP transport ────────────────────────────────────────────────────────

    def _send(self, subject: str, html: str) -> None:
        self._log.info(f"Sending email → {self._cfg['receiver']}")
        msg                = MIMEMultipart("alternative")
        msg["From"]        = self._cfg["sender"]
        msg["To"]          = self._cfg["receiver"]
        msg["Subject"]     = subject
        msg["X-Mailer"]    = "Flutter-Build-Automation/2.0"
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(self._cfg["smtp_server"], self._cfg["smtp_port"]) as server:
            server.ehlo()
            server.starttls()
            server.login(self._cfg["sender"], self._cfg["password"])
            server.send_message(msg)

        self._log.success("Notification email sent.")
