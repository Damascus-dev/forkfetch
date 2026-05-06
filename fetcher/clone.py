from __future__ import annotations

import subprocess
from pathlib import Path


def clone_repository(full_name: str, destination: Path | None = None) -> Path:
    target_dir = destination or Path.cwd()
    target_dir.mkdir(parents=True, exist_ok=True)
    repo_url = f"https://github.com/{full_name}.git"
    result = subprocess.run(
        ["git", "clone", repo_url],
        cwd=target_dir,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip() or "git clone failed"
        raise RuntimeError(stderr)
    return target_dir / full_name.split("/")[-1]
