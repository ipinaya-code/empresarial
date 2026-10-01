"""Genera huellas de evidencias seleccionadas y fuentes, sin copiar secretos."""

import argparse
import datetime
import hashlib
import json
import platform
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="Directorio revisado de evidencia, dentro del repositorio")
    args = parser.parse_args()
    directory = (ROOT / args.directory).resolve()
    if not directory.is_relative_to(ROOT) or not directory.is_dir():
        parser.error("Debe existir dentro del repositorio")
    source_paths = []
    for folder in ("app", "tests", "scripts", "migrations", "docker", ".github"):
        source_paths.extend(
            p for p in (ROOT / folder).rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
        )
    source_paths.extend(
        ROOT / name
        for name in (
            "Makefile",
            "Jenkinsfile",
            "alembic.ini",
            "pyproject.toml",
            "requirements.lock",
            "requirements-dev.lock",
            "requirements-browser.lock",
        )
    )
    output = directory / "manifest.json"
    data = {
        "created_utc": datetime.datetime.now(datetime.UTC).isoformat(),
        "commit_base": subprocess.check_output(  # noqa: S603 - executable resolved locally, fixed arguments
            [shutil.which("git") or "/usr/bin/git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "working_tree_dirty": bool(
            subprocess.check_output(  # noqa: S603
                [shutil.which("git") or "/usr/bin/git", "status", "--porcelain"], cwd=ROOT, text=True
            ).strip()
        ),
        "python": platform.python_version(),
        "sources": {str(p.relative_to(ROOT)): digest(p) for p in sorted(source_paths)},
        "artifacts": {
            str(p.relative_to(directory)): digest(p)
            for p in sorted(directory.rglob("*"))
            if p.is_file() and p != output
        },
    }
    output.write_text(json.dumps(data, indent=2) + "\n")
    print(output.relative_to(ROOT))


if __name__ == "__main__":
    main()
