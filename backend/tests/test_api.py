"""Tes endpoint API tanpa memanggil Selenium atau MongoDB sungguhan."""

from unittest.mock import MagicMock

import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

from app import jobs
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_jobs():
    jobs._jobs.clear()
    yield
    jobs._jobs.clear()


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Social Search API"


def test_search_membuat_job_dan_mengembalikan_hasil(monkeypatch):
    videos = MagicMock()
    videos.find.return_value = [{"video_id": "v1", "keyword": "bwi"}]
    monkeypatch.setattr("app.main.videos", videos)

    response = client.post("/search", params={"keyword": "bwi"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "accepted"
    assert body["reused"] is False

    status = client.get(f"/search/status/{body['job_id']}").json()
    assert status["status"] == "done"
    assert status["source"] == "cache"
    assert status["data"][0]["video_id"] == "v1"


def test_search_menggunakan_job_aktif_yang_sama(monkeypatch):
    monkeypatch.setattr("app.main.videos", MagicMock())
    active = jobs.create_job("bwi")

    body = client.post("/search", params={"keyword": "bwi"}).json()
    assert body["job_id"] == active.id
    assert body["reused"] is True
    assert len(jobs._jobs) == 1


def test_status_job_tidak_ditemukan():
    response = client.get("/search/status/tidak-ada")
    assert response.status_code == 404


def test_get_video_mengubah_objectid(monkeypatch):
    videos = MagicMock()
    videos.find.return_value = [
        {"_id": ObjectId(), "video_id": "v1", "keyword": "bwi"}
    ]
    monkeypatch.setattr("app.main.videos", videos)

    response = client.get("/video", params={"video_id": "v1"})
    assert response.status_code == 200
    assert isinstance(response.json()["data"][0]["_id"], str)
