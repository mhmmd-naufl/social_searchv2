"""API FastAPI untuk Social Search."""

import logging
from contextlib import asynccontextmanager

from bson import ObjectId
from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from . import jobs
from .config import CORS_ORIGINS
from .database import ensure_indexes, videos
from .scrapper import search_video

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_indexes()
    yield


app = FastAPI(lifespan=lifespan)

# Origin dibatasi, bukan "*". Sesuaikan CORS_ORIGINS di backend/.env.
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


def fix_objectid(data):
    """Ubah ObjectId MongoDB menjadi string agar bisa di-serialize JSON."""
    if isinstance(data, list):
        return [fix_objectid(item) for item in data]
    if isinstance(data, dict):
        return {
            key: str(value) if isinstance(value, ObjectId) else fix_objectid(value)
            for key, value in data.items()
        }
    return data


def run_search_job(job_id: str, keyword: str) -> None:
    """Dijalankan BackgroundTasks, terpisah dari request HTTP."""
    jobs.set_running(job_id)
    try:
        cached = list(videos.find({"keyword": keyword}))
        if cached:
            data, source = fix_objectid(cached), "cache"
        else:
            result = search_video(keyword)
            if not result:
                raise RuntimeError("Tidak ada data ditemukan untuk keyword ini.")
            data, source = fix_objectid(result), "scraper"
        jobs.set_done(job_id, data, source)
    except Exception as exc:
        logger.exception("Job %s gagal untuk keyword %r", job_id, keyword)
        jobs.set_failed(job_id, str(exc))


@app.get("/")
def read_root():
    return {"message": "Social Search API"}


@app.post("/search")
def start_search(
    background_tasks: BackgroundTasks,
    keyword: str = Query(..., min_length=1),
):
    """Mulai job scraping dan langsung kembali dengan job_id."""
    keyword = keyword.strip()
    if not keyword:
        raise HTTPException(status_code=400, detail="Keyword is required")

    # Hindari beberapa scraping bersamaan untuk keyword yang sama.
    active = jobs.get_active_job(keyword)
    if active is not None:
        return {"status": "accepted", "job_id": active.id, "reused": True}

    job = jobs.create_job(keyword)
    background_tasks.add_task(run_search_job, job.id, keyword)
    return {"status": "accepted", "job_id": job.id, "reused": False}


@app.get("/search/status/{job_id}")
def search_status(job_id: str):
    """Frontend melakukan polling ke endpoint ini sampai status done/failed."""
    job = jobs.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job tidak ditemukan")
    return job.to_dict()


@app.get("/search")
def search(keyword: str = Query(..., min_length=1)):
    """Endpoint lama (blocking) — dipertahankan untuk kompatibilitas."""
    keyword = keyword.strip()
    if not keyword:
        raise HTTPException(status_code=400, detail="Keyword is required")

    try:
        cached = list(videos.find({"keyword": keyword}))
        if cached:
            return {"status": "success", "data": fix_objectid(cached), "source": "cache"}

        result = search_video(keyword)
        if not result:
            raise HTTPException(status_code=404, detail="No data found")

        return {"status": "success", "data": fix_objectid(result), "source": "scraper"}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Search gagal untuk keyword %r", keyword)
        raise HTTPException(status_code=500, detail="Scrapper failed") from exc


@app.get("/video")
def get_video(video_id: str = Query(...)):
    data = list(videos.find({"video_id": video_id}))
    return {"status": "success", "data": fix_objectid(data)}
