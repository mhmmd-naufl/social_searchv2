"""Penyimpanan job scraping in-memory.

Endpoint scraping dijalankan di background agar request tidak menunggu
Selenium selesai. Untuk skala produksi, ganti modul ini dengan Redis/Celery.
"""

import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from uuid import uuid4

_lock = threading.Lock()
_jobs: Dict[str, "Job"] = {}
_MAX_JOBS = 50


@dataclass
class Job:
    id: str
    keyword: str
    status: str = "pending"  # pending | running | done | failed
    source: str = ""
    data: List[dict] = field(default_factory=list)
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)

    def to_dict(self):
        return {
            "job_id": self.id,
            "keyword": self.keyword,
            "status": self.status,
            "source": self.source,
            "data": self.data,
            "error": self.error,
        }


def _prune_locked():
    """Batasi jumlah job yang disimpan agar memori tidak tumbuh terus."""
    if len(_jobs) <= _MAX_JOBS:
        return
    oldest = sorted(_jobs.values(), key=lambda job: job.created_at)[:-_MAX_JOBS]
    for job in oldest:
        _jobs.pop(job.id, None)


def create_job(keyword: str) -> Job:
    job = Job(id=uuid4().hex, keyword=keyword)
    with _lock:
        _jobs[job.id] = job
        _prune_locked()
    return job


def get_job(job_id: str) -> Optional[Job]:
    with _lock:
        return _jobs.get(job_id)


def set_running(job_id: str) -> None:
    with _lock:
        if job_id in _jobs:
            _jobs[job_id].status = "running"


def set_done(job_id: str, data: list, source: str = "") -> None:
    with _lock:
        if job_id in _jobs:
            _jobs[job_id].status = "done"
            _jobs[job_id].data = data
            _jobs[job_id].source = source


def set_failed(job_id: str, error: str) -> None:
    with _lock:
        if job_id in _jobs:
            _jobs[job_id].status = "failed"
            _jobs[job_id].error = error
