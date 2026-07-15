import os
import time
from datetime import timedelta

import pytest

import app.downloads as downloads
import app.rate_limit as rate_limit
import app.v1.models as models
import app.v1.routes as routes
from app.config import DOWNLOAD_DIR, loaded_config
from tests import client

video_link = (
    "https://youtu.be/S3wsCRJVUyg?si=SjN17MR1-u7BPgxk?si=svRtQPHef9TSMABt"
)
# https://youtu.be/R3GfuzLMPkA?si=YItOxtgw3LAjKps1


@pytest.mark.parametrize(["query", "limit"], [("hello", 2), ("hey", 1)])
def test_video_search(query, limit):
    resp = client.get("/api/v1/search", params=dict(q=query, limit=limit))
    assert resp.is_success
    videos = models.SearchVideosResponse(**resp.json())
    assert len(videos.results) <= limit


@pytest.mark.parametrize(
    ["url"],
    [
        ("https://youtu.be/HUGcwe93F9E?si=Ajunj8GlRs-DzKnQ",),
        ("HUGcwe93F9E",),
        ("https://www.youtube.com/watch?v=HUGcwe93F9E",),
    ],
)
def test_video_metadata(url):
    resp = client.get("/api/v1/metadata", params=dict(url=url))
    assert resp.is_success
    models.VideoMetadataResponse(**resp.json())


@pytest.mark.parametrize(
    ["url", "quality", "bitrate"],
    [
        ("https://youtu.be/S3wsCRJVUyg?si=SjN17MR1-u7BPgxk", "1080p", None),
        ("https://youtu.be/S3wsCRJVUyg?si=SjN17MR1-u7BPgxk", "720p", "128k"),
        ("https://youtu.be/S3wsCRJVUyg?si=SjN17MR1-u7BPgxk", "medium", "192k"),
        ("https://youtu.be/S3wsCRJVUyg?si=SjN17MR1-u7BPgxk", "medium", None),
    ],
)
def test_download_processing(url, quality, bitrate):
    resp = client.post(
        "/api/v1/download",
        json=dict(
            url=url,
            quality=quality,
            bitrate=bitrate,
        ),
    )
    if not resp.is_success:
        print(resp.text)
    assert resp.is_success
    models.MediaDownloadResponse(**resp.json())
    # This will raise 404 since the static contents are served by flask (wsgi).
    # static_resp = client.get(str(media.link))
    # assert static_resp.is_success


def test_api_key_protection(monkeypatch):
    rate_limit.rate_limiter._requests.clear()
    monkeypatch.setattr(loaded_config, "require_api_key", True)
    monkeypatch.setattr(loaded_config, "api_key", "secret")
    monkeypatch.setattr(routes, "search_videos_by_key", lambda query, limit: [])

    unauthorized = client.get("/api/v1/search", params=dict(q="hello", limit=1))
    assert unauthorized.status_code == 401

    authorized = client.get(
        "/api/v1/search",
        params=dict(q="hello", limit=1),
        headers={"X-API-Key": "secret"},
    )
    assert authorized.status_code == 404

    monkeypatch.setattr(loaded_config, "require_api_key", False)
    monkeypatch.setattr(loaded_config, "api_key", None)


def test_rate_limit(monkeypatch):
    rate_limit.rate_limiter._requests.clear()
    monkeypatch.setattr(loaded_config, "rate_limit_requests", 1)
    monkeypatch.setattr(loaded_config, "rate_limit_window_seconds", 60)
    monkeypatch.setattr(routes, "search_videos_by_key", lambda query, limit: [])

    first = client.get("/api/v1/search", params=dict(q="hello", limit=1))
    second = client.get("/api/v1/search", params=dict(q="hello", limit=1))

    assert first.status_code == 404
    assert second.status_code == 429

    monkeypatch.setattr(loaded_config, "rate_limit_requests", 30)
    rate_limit.rate_limiter._requests.clear()


def test_delete_expired_downloads(monkeypatch):
    monkeypatch.setattr(loaded_config, "download_file_ttl_in_seconds", 1)
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = DOWNLOAD_DIR / "test-delete.txt"
    file_path.write_text("hello", encoding="utf-8")
    current_time = downloads.utc_now()
    old_time = (current_time - timedelta(seconds=5)).timestamp()
    os.utime(file_path, (old_time, old_time))
    monkeypatch.setattr(
        downloads,
        "utc_now",
        lambda: current_time + timedelta(seconds=2),
    )

    deleted = downloads.delete_expired_downloads()

    assert deleted == 1
    assert not file_path.exists()
