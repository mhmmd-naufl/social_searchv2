"""Konfigurasi terpusat.

Semua nilai yang sensitif atau bergantung lingkungan dibaca dari environment
variable (file ``backend/.env`` untuk lokal). Jangan pernah menyimpan secret
langsung di source code.
"""

import os

from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "new_tiktok_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "videos")

_raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173")
CORS_ORIGINS = [origin.strip() for origin in _raw_origins.split(",") if origin.strip()]

# Cookie TikTok: JSON string di env lebih diutamakan, fallback ke file lokal.
COOKIES_JSON = os.getenv("TIKTOK_COOKIES_JSON", "")
COOKIES_FILE = os.getenv(
    "TIKTOK_COOKIES_FILE",
    os.path.join(os.path.dirname(__file__), "cookies.json"),
)
