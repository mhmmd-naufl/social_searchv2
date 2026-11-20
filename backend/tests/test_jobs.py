"""Tes untuk penyimpanan job background."""

import pytest

from app import jobs


@pytest.fixture(autouse=True)
def reset_jobs():
    jobs._jobs.clear()
    yield
    jobs._jobs.clear()


def test_create_and_get_job():
    job = jobs.create_job("banyuwangi")
    assert jobs.get_job(job.id) is job
    assert job.status == "pending"
    assert job.keyword == "banyuwangi"


def test_siklus_status_job():
    job = jobs.create_job("tetangga")
    jobs.set_running(job.id)
    assert job.status == "running"

    jobs.set_done(job.id, [{"video_id": "abc"}], "cache")
    assert job.status == "done"
    assert job.source == "cache"
    assert job.data == [{"video_id": "abc"}]

    jobs.set_failed(job.id, "gagal")
    assert job.status == "failed"
    assert job.error == "gagal"


def test_job_aktif_ditemukan_hanya_sebelum_selesai():
    job = jobs.create_job("kominfo")
    assert jobs.get_active_job("kominfo") is job
    assert jobs.get_active_job("keyword lain") is None

    jobs.set_done(job.id, [])
    assert jobs.get_active_job("kominfo") is None


def test_to_dict():
    job = jobs.create_job("bwi")
    data = job.to_dict()
    assert set(data) == {
        "job_id",
        "keyword",
        "status",
        "source",
        "keyword_found",
        "data",
        "error",
    }
    assert data["job_id"] == job.id
