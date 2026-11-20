"""Simpan hasil scraping ke MongoDB.

Gunakan upsert agar keyword/video yang sama tidak menumpuk sebagai duplikat
setiap kali scraping dijalankan ulang.
"""

import logging
from datetime import datetime, timezone

from .database import videos

logger = logging.getLogger(__name__)


def save_to_mongo(data):
    try:
        payload = dict(data)
        payload["scraped_at"] = datetime.now(timezone.utc)

        videos.update_one(
            {"video_id": payload.get("video_id")},
            {"$set": payload},
            upsert=True,
        )
        logger.info("Video %s berhasil disimpan.", payload.get("video_id"))
        return True
    except Exception as exc:
        logger.exception("Gagal menyimpan ke MongoDB: %s", exc)
        return False
