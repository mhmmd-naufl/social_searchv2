"""Evaluasi leksikon sentimen dengan contoh komentar berlabel.

Dataset kecil di ``backend/tests/data/labeled_comments.json`` dibuat manual
untuk mendemonstrasikan cara mengukur kinerja. Ini BUKAN benchmark representatif.
"""

import json
from pathlib import Path

try:
    from .analysis_comment import analyze_sentiment_lexicon, preprocess_text
except ImportError:  # dijalankan langsung sebagai script
    from analysis_comment import analyze_sentiment_lexicon, preprocess_text

DATA_PATH = Path(__file__).resolve().parents[2] / "tests" / "data" / "labeled_comments.json"
CLASSES = ("positif", "negatif", "netral")


def load_data(path=DATA_PATH):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def evaluate(data):
    confusion = {actual: {predicted: 0 for predicted in CLASSES} for actual in CLASSES}
    for item in data:
        predicted = analyze_sentiment_lexicon(preprocess_text(item["text"]))
        confusion[item["label"]][predicted] += 1

    correct = sum(confusion[c][c] for c in CLASSES)
    accuracy = correct / len(data) if data else 0.0

    metrics = {}
    for label in CLASSES:
        true_positive = confusion[label][label]
        false_positive = sum(confusion[other][label] for other in CLASSES if other != label)
        false_negative = sum(confusion[label][other] for other in CLASSES if other != label)

        precision = true_positive / (true_positive + false_positive) if (true_positive + false_positive) else 0.0
        recall = true_positive / (true_positive + false_negative) if (true_positive + false_negative) else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

        metrics[label] = {
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1": round(f1, 3),
            "support": sum(confusion[label].values()),
        }

    return {"accuracy": round(accuracy, 3), "metrics": metrics, "confusion": confusion}


def format_report(result):
    lines = [f"Accuracy: {result['accuracy']:.1%}", ""]
    lines.append(f"{'kelas':<10} {'precision':>10} {'recall':>8} {'f1':>8} {'support':>8}")
    for label, values in result["metrics"].items():
        lines.append(
            f"{label:<10} {values['precision']:>10.3f} {values['recall']:>8.3f} "
            f"{values['f1']:>8.3f} {values['support']:>8}"
        )
    lines.append("")
    lines.append("Confusion matrix (baris = aktual, kolom = prediksi):")
    lines.append(f"{'':<10}" + "".join(f"{c:>10}" for c in CLASSES))
    for actual in CLASSES:
        lines.append(f"{actual:<10}" + "".join(f"{result['confusion'][actual][c]:>10}" for c in CLASSES))
    return "\n".join(lines)


if __name__ == "__main__":
    print(format_report(evaluate(load_data())))
