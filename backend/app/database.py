"""Satu koneksi MongoDB untuk seluruh aplikasi."""

import logging

from pymongo import MongoClient

from .config import COLLECTION_NAME, DB_NAME, MONGO_URI

logger = logging.getLogger(__name__)

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client[DB_NAME]
videos = db[COLLECTION_NAME]


def ensure_indexes():
    """Buat index yang dipakai query. Aman dipanggil berkali-kali."""
    try:
        videos.create_index("keyword")
        videos.create_index("video_id")
        videos.create_index("scraped_at")
        logger.info("Index MongoDB siap.")
    except Exception as exc:  # Mongo bisa saja belum berjalan saat development
        logger.warning("Gagal membuat index MongoDB: %s", exc)
