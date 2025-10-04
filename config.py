"""Helpers voor het laden van databaseconfiguratie."""

from __future__ import annotations

import json
import os
from configparser import ConfigParser
from pathlib import Path
from typing import Iterable, Optional

DEFAULT_DB_PATH = (
    r"\\\\file01.storage\\smB-usr-lrnas\\lr-lccu\\Bruno\\objecten.db"
)
ENV_VAR_NAME = "LCCU_DB_PATH"
INI_FILENAMES: tuple[str, ...] = ("config.ini", "settings.ini")
JSON_FILENAMES: tuple[str, ...] = ("config.json", "settings.json")


def _candidate_directories() -> Iterable[Path]:
    """Return plausible directories that may contain configuration files."""
    here = Path(__file__).resolve().parent
    cwd = Path.cwd()
    # Use an ordered set-like approach to avoid duplicates while preserving order
    seen: set[Path] = set()
    for directory in (cwd, here):
        if directory not in seen:
            seen.add(directory)
            yield directory


def _load_from_ini(path: Path) -> Optional[str]:
    parser = ConfigParser()
    try:
        with path.open(encoding="utf-8") as fh:
            parser.read_file(fh)
    except OSError:
        return None
    if parser.has_option("database", "path"):
        value = parser.get("database", "path").strip()
        if value:
            return value
    return None


def _load_from_json(path: Path) -> Optional[str]:
    try:
        with path.open(encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None
    value: Optional[str] = None
    if isinstance(data, dict):
        if "database_path" in data:
            candidate = data.get("database_path")
            if isinstance(candidate, str) and candidate.strip():
                value = candidate.strip()
        if value is None:
            database_section = data.get("database")
            if isinstance(database_section, dict):
                candidate = database_section.get("path")
                if isinstance(candidate, str) and candidate.strip():
                    value = candidate.strip()
    return value


def get_database_path() -> str:
    """Resolve the database path from environment variables or config files."""
    env_value = os.getenv(ENV_VAR_NAME)
    if env_value and env_value.strip():
        return env_value.strip()

    for directory in _candidate_directories():
        for filename in INI_FILENAMES:
            ini_path = directory / filename
            if ini_path.exists():
                value = _load_from_ini(ini_path)
                if value:
                    return value
        for filename in JSON_FILENAMES:
            json_path = directory / filename
            if json_path.exists():
                value = _load_from_json(json_path)
                if value:
                    return value

    return DEFAULT_DB_PATH
