"""Cookie TikTok tidak lagi disimpan di source code.

Sumber dibaca dengan prioritas:

1. ``TIKTOK_COOKIES_JSON`` — string JSON di environment variable.
2. ``TIKTOK_COOKIES_FILE`` / ``backend/app/cookies.json`` — file lokal yang
   sudah masuk ke ``.gitignore``.
3. Daftar kosong — scraper tetap berjalan tanpa cookie (mode guest).

Cookie bersifat sensitif dan bersifat session. Perbarui file JSON lokal Anda
sendiri saat cookie kedaluwarsa; jangan pernah meng-commit-nya ke repository.
"""

import json
import logging
import os

logger = logging.getLogger(__name__)


def _load_cookies():
    raw_json = os.getenv("TIKTOK_COOKIES_JSON", "").strip()
    if raw_json:
        try:
            cookies = json.loads(raw_json)
            if isinstance(cookies, list):
                return cookies
            logger.warning("TIKTOK_COOKIES_JSON bukan sebuah list, diabaikan.")
        except json.JSONDecodeError as exc:
            logger.warning("TIKTOK_COOKIES_JSON tidak valid: %s", exc)

    path = os.getenv("TIKTOK_COOKIES_FILE") or os.path.join(
        os.path.dirname(__file__), "cookies.json"
    )
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as file:
                cookies = json.load(file)
            if isinstance(cookies, list):
                return cookies
            logger.warning("Isi %s bukan sebuah list, diabaikan.", path)
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Gagal memuat cookies dari %s: %s", path, exc)
    else:
        logger.info("File cookies tidak ditemukan di %s. Lanjut tanpa cookie.", path)

    return []


cookie = _load_cookies()
