"""Perluas leksikon sentimen dari kamus KBBI.

File ``indonesian-adjective-sentiment-raw.csv`` hanya berisi kata dan
definisi, **tanpa label sentimen**. Modul ini memberi skor pada setiap kata
dengan menghitung kata kunci positif/negatif di kolom ``explanation``.

Hasilnya ditulis ke ``lexicon_kbbi.json`` dan bisa dipakai dengan menyetel
``USE_KBBI_LEXICON=1``. Secara default leksikon ini tidak dipakai agar hasil
analisis tetap deterministik.
"""

import csv
import json
import re
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parents[3] / "indonesian-adjective-sentiment-raw.csv"
OUTPUT_PATH = Path(__file__).with_name("lexicon_kbbi.json")

POSITIVE_SEEDS = [
    "baik", "indah", "senang", "bahagia", "cinta", "cantik", "ramah",
    "kuat", "cerah", "tenang", "berhasil", "mulia", "suci", "murni",
    "sejahtera", "nyaman", "puas", "harapan",
]

NEGATIVE_SEEDS = [
    "sakit", "sedih", "jelek", "buruk", "rusak", "benci", "marah",
    "takut", "kotor", "kasar", "sengsara", "gagal", "hina", "kacau",
    "bahaya", "miskin", "kecewa", "susah",
]


def _count_seeds(text, seeds):
    return sum(len(re.findall(rf"\b{re.escape(seed)}\b", text)) for seed in seeds)


def build_lexicon(csv_path=CSV_PATH):
    """Kembalikan dict {kata: skor} dari definisi KBBI."""
    extra = {}
    with open(csv_path, "r", encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            word = (row.get("word") or "").strip().lower()
            explanation = (row.get("explanation") or "").lower()
            if not word or " " in word or "-" in word:
                continue

            positive = _count_seeds(explanation, POSITIVE_SEEDS)
            negative = _count_seeds(explanation, NEGATIVE_SEEDS)
            if positive > negative:
                extra[word] = 1
            elif negative > positive:
                extra[word] = -1
    return extra


def build_and_save(csv_path=CSV_PATH, output_path=OUTPUT_PATH):
    extra = build_lexicon(csv_path)
    output_path.write_text(
        json.dumps(extra, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return extra


def load_extra():
    if OUTPUT_PATH.is_file():
        with open(OUTPUT_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}


if __name__ == "__main__":
    result = build_and_save()
    print(f"Tersimpan {len(result)} entri ke {OUTPUT_PATH}")
