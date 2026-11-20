"""Isi MongoDB dengan data contoh untuk mode demo.

Data di ``backend/demo/sample_videos.json`` berisi 12 video beserta komentar
yang sudah dianalisis. Script ini melakukan upsert, aman dijalankan berulang.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "new_tiktok_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "videos")
SAMPLE_PATH = Path(__file__).resolve().parent / "demo" / "sample_videos.json"


def main():
    if not MONGO_URI:
        raise SystemExit("MONGO_URI belum diisi. Tambahkan ke backend/.env lalu jalankan lagi.")

    documents = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
    collection = client[DB_NAME][COLLECTION_NAME]

    collection.create_index("keyword")
    collection.create_index("video_id")

    for document in documents:
        collection.update_one(
            {"video_id": document.get("video_id")},
            {"$set": document},
            upsert=True,
        )

    print(f"Seed selesai: {len(documents)} dokumen ditulis. Total: {collection.count_documents({})}")
    client.close()


if __name__ == "__main__":
    main()
