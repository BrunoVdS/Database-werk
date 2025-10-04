"""Configuration helpers for the LCCU database application.

This module centralises the logic that determines which SQLite database file
should be used. The path can be specified via environment variables or simple
configuration files, and falls back to the historical UNC path when nothing is
provided.
"""
from __future__ import annotations

import configparser
import json
import os
from pathlib import Path
from typing import Iterable, Optional

# The historical network location of the production database.  This is the
# default value that is used when no overriding configuration is provided.
DEFAULT_DB_PATH = r"\\\\file01.storage\\smB-usr-lrnas\\lr-lccu\\Bruno\\objecten.db"

# Environment variable that can override the database path.
_ENV_VAR_NAME = "LCCU_DB_PATH"

# Candidate configuration files that may contain a database path override.
_INI_FILENAMES: tuple[str, ...] = ("config.ini", "settings.ini")
_JSON_FILENAMES: tuple[str, ...] = ("config.json", "settings.json")

# Keys that are checked inside INI/JSON files.
_DB_PATH_KEYS: tuple[str, ...] = ("path", "db_path", "database_path")


def _candidate_directories() -> list[Path]:
    """Return directories that might contain configuration files."""
    base_dir = Path(__file__).resolve().parent
    cwd = Path.cwd()
    dirs: list[Path] = []
    for directory in (base_dir, cwd):
        if directory not in dirs:
            dirs.append(directory)
    return dirs


def _load_from_env() -> Optional[str]:
    """Return the database path defined via environment variable."""
    value = os.environ.get(_ENV_VAR_NAME)
    if value:
        value = value.strip()
        if value:
            return os.path.expanduser(value)
    return None


def _load_from_ini_file(file_path: Path) -> Optional[str]:
    parser = configparser.ConfigParser()
    try:
        with file_path.open("r", encoding="utf-8") as fh:
            parser.read_file(fh)
    except OSError:
        return None

    sections_to_check: Iterable[str] = ("database", "DATABASE", "Database", "DEFAULT")
    for section in sections_to_check:
        if parser.has_section(section) or section == "DEFAULT":
            config_section = parser[section] if section in parser else parser.defaults()
            for key in _DB_PATH_KEYS:
                value = config_section.get(key)
                if value:
                    value = value.strip()
                    if value:
                        return os.path.expanduser(value)
    return None


def _load_from_json_file(file_path: Path) -> Optional[str]:
    try:
        with file_path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None

    # Support both nested and flat structures.
    if isinstance(data, dict):
        for key in _DB_PATH_KEYS:
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return os.path.expanduser(value.strip())
        database_section = data.get("database")
        if isinstance(database_section, dict):
            for key in _DB_PATH_KEYS:
                value = database_section.get(key)
                if isinstance(value, str) and value.strip():
                    return os.path.expanduser(value.strip())
    return None


def get_database_path() -> str:
    """Determine the database path to use for SQLite connections."""
    env_value = _load_from_env()
    if env_value:
        return env_value

    for directory in _candidate_directories():
        for filename in _INI_FILENAMES:
            ini_path = directory / filename
            if ini_path.exists():
                value = _load_from_ini_file(ini_path)
                if value:
                    return value
        for filename in _JSON_FILENAMES:
            json_path = directory / filename
            if json_path.exists():
                value = _load_from_json_file(json_path)
                if value:
                    return value

    return DEFAULT_DB_PATH


__all__ = ["DEFAULT_DB_PATH", "get_database_path"]
