"""Download file retention helpers."""

from datetime import timedelta
from pathlib import Path

from app.config import DOWNLOAD_DIR, loaded_config
from app.utils import logger, utc_now


def delete_file_if_present(file_path: Path):
    if file_path.exists():
        file_path.unlink(missing_ok=True)
        logger.info("Deleted download file %s", file_path.name)


def delete_expired_downloads() -> int:
    """Delete download files older than the configured ttl."""
    if loaded_config.download_file_ttl_in_seconds <= 0 or not DOWNLOAD_DIR.exists():
        return 0

    threshold = utc_now() - timedelta(
        seconds=loaded_config.download_file_ttl_in_seconds
    )
    deleted = 0
    for file_path in DOWNLOAD_DIR.iterdir():
        if not file_path.is_file():
            continue
        modified_on = file_path.stat().st_mtime
        if modified_on <= threshold.timestamp():
            file_path.unlink(missing_ok=True)
            deleted += 1

    if deleted:
        logger.info("Deleted %s expired download files", deleted)

    return deleted
