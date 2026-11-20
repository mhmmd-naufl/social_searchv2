"""Tes untuk pra-pemrosesan dan analisis sentimen."""

import pytest

from app.analysis.analysis_comment import (
    analyze_comments_from_data,
    analyze_sentiment_lexicon,
    preprocess_text,
)


@pytest.mark.parametrize(
    "text, expected",
    [
        ("sangat bagus", "positif"),
        ("saya suka tempat ini", "positif"),
        ("tidak suka", "negatif"),
        ("gak bagus", "negatif"),
        ("luar biasa", "positif"),
        ("sakit hati", "negatif"),
        ("murah hati", "positif"),
        ("😂", "positif"),
    ],
)
def test_sentimen(text, expected):
    tokens = preprocess_text(text)
    assert analyze_sentiment_lexicon(tokens) == expected


def test_preprocess_tetap_simpan_kata_negasi():
    tokens = preprocess_text("tidak suka")
    assert "tidak" in tokens


def test_preprocess_tetap_simpan_emoji():
    assert preprocess_text("😂") == ["😂"]


def test_normalisasi_slang():
    assert "tidak" in preprocess_text("gak")


def test_hasil_analisis_memiliki_struktur_yang_diharapkan():
    result = analyze_comments_from_data(["bagus sekali", "jelek"])
    assert len(result) == 2
    assert set(result[0]) == {"text", "sentiment"}
    assert result[0]["text"] == "bagus sekali"
    assert result[0]["sentiment"] == "positif"
    assert result[1]["sentiment"] == "negatif"
