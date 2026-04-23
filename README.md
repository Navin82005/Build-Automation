# Build Automation

Interactive CLI pipeline that cleans, builds, zips, uploads to Google Drive,
and emails notifications for Flutter projects — with a timed confirmation prompt
before every step.

---

## Package Layout

```
flutter_build/
├── __init__.py               # package entry, re-exports main()
├── colours.py                # ANSI escape constants + _c() helper
├── config.py                 # ConfigLoader — loads & validates config.json
├── logger.py                 # Logger — structured, coloured CLI output
├── commands.py               # Commands — CLI command definitions
├── prompter.py               # Prompter — timed yes/no prompt with fallback
├── main.py                   # Entry-point — wires layers, runs pipeline
├── pipeline.py               # BuildPipeline — orchestrates the build flow
└── services/
    ├── __init__.py           # re-exports all four services
    ├── command_processor.py  # CommandProcessor — CLI command processor
    ├── drive.py              # DriveService — OAuth2 + resumable upload
    └── email.py              # EmailService — HTML success/failure emails
    ├── runner.py             # CommandRunner — shell commands with live output
    ├── zipper.py             # ZipService — folder → .zip archive
```

---

## Installation

```bash
pip install -e .
```

Or without installing:

```bash
python -m flutter_build.main
```

---

## Configuration — config.json

Place `config.json` in the project root (next to `pyproject.toml`):

```json
{
  "working_path": "/path/to/your/flutter/project",
  "build_command": "flutter build ios --simulator --debug",
  "output_name":   "MyApp",
  "drive_folder_id": "YOUR_GOOGLE_DRIVE_FOLDER_ID",

  "prompt_timeout": 15,

  "step_fallbacks": {
    "clean":        "yes",
    "pub_get":      "yes",
    "pod_install":  "yes",
    "build_runner": "yes",
    "main_build":   "yes"
  },

  "email": {
    "sender":      "ci-bot@example.com",
    "receiver":    "team@example.com",
    "smtp_server": "smtp.gmail.com",
    "smtp_port":   587,
    "password":    "YOUR_APP_PASSWORD"
  }
}
```

| Key | Description |
|---|---|
| `prompt_timeout` | Seconds to wait for user input before applying the fallback |
| `step_fallbacks` | Per-step default answer (`"yes"` or `"no"`) used on timeout |

---

## Google Drive Setup

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Google Drive API**.
3. Create **OAuth 2.0 credentials** (Desktop app) and download `credentials.json`.
4. Place `credentials.json` in the project root.
5. On first run a browser window will open for OAuth consent; `token.json` is
   saved automatically for subsequent runs.

---

## Usage

```bash
# via installed script
flutter-build

# or directly
python -m flutter_build.main
```

The pipeline will prompt before each step:

```
  ?  Run step: flutter clean?
     Enter yes/no — auto-continues in 15s [default: yes]:
```

If no response is given within the timeout, the configured fallback is used.
