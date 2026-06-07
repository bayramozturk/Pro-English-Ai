import shutil
import tempfile
import time
import urllib.request
import zipfile
from pathlib import Path


VERSION = "6.5"
URL = f"https://languagetool.org/download/LanguageTool-{VERSION}.zip"
TARGET_ROOT = Path("/app/.runtime")
EXPECTED_DIR = TARGET_ROOT / f"LanguageTool-{VERSION}"


def download_archive(destination):
    request = urllib.request.Request(
        URL,
        headers={"User-Agent": "Pro-English-AI-Render-Build/1.0"},
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        with destination.open("wb") as archive:
            shutil.copyfileobj(response, archive, length=1024 * 1024)


def main():
    if EXPECTED_DIR.is_dir():
        return

    TARGET_ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary_directory:
        archive_path = Path(temporary_directory) / "languagetool.zip"
        last_error = None
        for attempt in range(1, 4):
            try:
                download_archive(archive_path)
                with zipfile.ZipFile(archive_path) as archive:
                    archive.extractall(TARGET_ROOT)
                if not EXPECTED_DIR.is_dir():
                    raise RuntimeError("LanguageTool archive layout is invalid.")
                return
            except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
                last_error = exc
                archive_path.unlink(missing_ok=True)
                if attempt < 3:
                    time.sleep(attempt * 3)

        raise RuntimeError("LanguageTool could not be installed.") from last_error


if __name__ == "__main__":
    main()
