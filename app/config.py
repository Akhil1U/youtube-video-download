import os
import tomllib
from pathlib import Path

import yaml

from app.models import ConfigModel

PROJECT_DIR = Path(__file__).parent.parent
ENV_CONFIG_FILE_PATH = os.getenv("YDA_CONFIG_FILE_PATH")

if ENV_CONFIG_FILE_PATH:
    CONFIG_FILE_PATH = Path(ENV_CONFIG_FILE_PATH)
else:
    CONFIG_FILE_PATH = PROJECT_DIR / "config.yml"


assert CONFIG_FILE_PATH.exists(), (
    f"Invalid config file path {CONFIG_FILE_PATH.absolute()!r}. Does not exist"
)

config_values = yaml.safe_load(open(CONFIG_FILE_PATH))


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def apply_env_overrides(config: dict) -> dict:
    env_mappings = {
        "YDA_DATABASE_ENGINE": ("database_engine", str),
        "YDA_COOKIEFILE": ("cookiefile", str),
        "YDA_PROXY": ("proxy", str),
        "YDA_REQUIRE_API_KEY": ("require_api_key", _parse_bool),
        "YDA_API_KEY": ("api_key", str),
        "YDA_RATE_LIMIT_REQUESTS": ("rate_limit_requests", int),
        "YDA_RATE_LIMIT_WINDOW_SECONDS": (
            "rate_limit_window_seconds",
            int,
        ),
        "YDA_DOWNLOAD_FILE_TTL_SECONDS": (
            "download_file_ttl_in_seconds",
            int,
        ),
        "YDA_DELETE_DOWNLOAD_AFTER_ACCESS": (
            "delete_download_after_access",
            _parse_bool,
        ),
        "YDA_CLEAR_DOWNLOADED_CONTENTS": (
            "clear_downloaded_contents",
            _parse_bool,
        ),
        "YDA_REMOTE_COMPONENTS": ("remote_components", _parse_list),
    }
    for env_name, (config_key, parser) in env_mappings.items():
        env_value = os.getenv(env_name)
        if env_value is None or env_value == "":
            continue
        config[config_key] = parser(env_value)

    return config


config_values = apply_env_overrides(config_values)

loaded_config = ConfigModel(**config_values)
"""Loaded from .env file"""

WORKING_DIR = Path(loaded_config.working_directory)

DOWNLOAD_DIR = WORKING_DIR / "downloads"

TEMP_DIR = WORKING_DIR / "temps"


PYPROJECT_DOT_TOML_PATH = PROJECT_DIR / "pyproject.toml"

pyproject_dot_toml_details = tomllib.load(open(PYPROJECT_DOT_TOML_PATH, "rb"))
