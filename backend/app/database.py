"""Koneksi MongoDB singleton + fallback data contoh untuk mode demo."""

import json
import logging
from pathlib import Path

from pymongo import MongoClient

from .config import COLLECTION_NAME, DB_NAME, MONGO_URI

logger = logging.getLogger(__name__)

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client[DB_NAME]
videos = db[COLLECTION_NAME]

SAMPLE_PATH = Path(__file__).resolve().parents[1] / "demo" / "sample_videos.json"


def ensure_indexes():
    """Buat index yang dipakai query. Aman dipanggil berkali-kali."""
    try:
        videos.create_index("keyword")
        videos.create_index("video_id")
        videos.create_index("scraped_at")
        logger.info("Index MongoDB siap.")
    except Exception as exc:  # Mongo bisa saja belum berjalan saat development
        logger.warning("Gagal membuat index MongoDB: %s", exc)


def _sample_documents(query):
    """Ambil dokumen dari file contoh saat MongoDB tidak tersedia."""
    if not SAMPLE_PATH.is_file():
        logger.warning("File data contoh tidak ditemukan: %s", SAMPLE_PATH)
        return []
    try:
        documents = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        logger.warning("Gagal membaca data contoh: %s", exc)
        return []

    return [
        document
        for document in documents
        if all(document.get(key) == value for key, value in query.items())
    ]


def find_documents(query):
    """Cari dokumen. Jika Mongo gagal, pakai data contoh (mode demo)."""
    try:
        return list(videos.find(query))
    except Exception as exc:
        logger.warning("MongoDB tidak tersedia (%s). Memakai data contoh.", exc)
        matches = _sample_documents(query)
        # Untuk pencarian keyword, tampilkan semua data contoh agar demo
        # tetap bisa dipakai dengan kata kunci apa pun.
        if not matches and "video_id" not in query:
            matches = _sample_documents({})
        return matches
