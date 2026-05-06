from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


APP_NAME = "fetcher"


@dataclass(slots=True)
class Settings:
    github_token: str | None
    config_path: Path
    data_dir: Path
    database_path: Path


def _default_config_dir() -> Path:
    custom_dir = os.environ.get("FETCHER_CONFIG_DIR")
    if custom_dir:
        return Path(custom_dir)
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / APP_NAME
    return Path.home() / ".config" / APP_NAME


def _default_data_dir() -> Path:
    custom_dir = os.environ.get("FETCHER_DATA_DIR")
    if custom_dir:
        return Path(custom_dir)
    if os.name == "nt":
        local_appdata = os.environ.get("LOCALAPPDATA")
        if local_appdata:
            return Path(local_appdata) / APP_NAME
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / APP_NAME / "data"
    return Path.home() / ".local" / "share" / APP_NAME


def _first_writable_dir(candidates: list[Path]) -> Path:
    for candidate in candidates:
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            return candidate
        except OSError:
            continue
    raise OSError("No writable directory available for fetcher data")


def load_settings() -> Settings:
    local_dir = Path.cwd() / ".fetcher"
    config_dir = _first_writable_dir([local_dir, _default_config_dir()])
    data_dir = _first_writable_dir([local_dir, _default_data_dir()])
    config_path = config_dir / "config.json"
    database_path = data_dir / "repos.db"

    github_token: str | None = None
    if config_path.exists():
        payload = json.loads(config_path.read_text(encoding="utf-8"))
        github_token = payload.get("github_token")

    return Settings(
        github_token=github_token,
        config_path=config_path,
        data_dir=data_dir,
        database_path=database_path,
    )


def save_github_token(token: str) -> Path:
    settings = load_settings()
    settings.config_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"github_token": token.strip()}
    settings.config_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return settings.config_path


def clear_github_token() -> Path:
    settings = load_settings()
    settings.config_path.parent.mkdir(parents=True, exist_ok=True)
    settings.config_path.write_text("{}\n", encoding="utf-8")
    return settings.config_path
