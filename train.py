import json
import pickle
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from sklearn.metrics import confusion_matrix, mean_absolute_error
from sklearn.pipeline import FeatureUnion, Pipeline


DATA_PATH = Path("data.csv")
CEFR_SP_PATH = Path("datasets/cefr_sp")
MODEL_PATH = Path("model.pkl")
REPORT_PATH = Path("model_report.json")
LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
LEVEL_TO_INDEX = {level: index for index, level in enumerate(LEVELS)}


def build_pipeline():
    features = FeatureUnion(
        [
            (
                "word_tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    strip_accents="unicode",
                    ngram_range=(1, 3),
                    sublinear_tf=True,
                    min_df=2,
                    max_df=0.995,
                    max_features=100_000,
                ),
            ),
            (
                "char_tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    strip_accents="unicode",
                    analyzer="char_wb",
                    ngram_range=(3, 6),
                    sublinear_tf=True,
                    min_df=2,
                    max_features=120_000,
                ),
            ),
        ]
    )
    return Pipeline([("features", features), ("model", Ridge(alpha=1.0))])


def read_cefr_sp_split(split):
    texts, low_labels, high_labels = [], [], []
    files = [
        CEFR_SP_PATH / "Wiki-Auto" / f"CEFR-SP_Wikiauto_{split}.txt",
        CEFR_SP_PATH / "SCoRE" / f"CEFR-SP_SCoRE_{split}.txt",
    ]

    for path in files:
        if not path.exists():
            raise FileNotFoundError(f"{path} bulunamadı.")
        for line in path.read_text(encoding="utf-8").splitlines():
            text, annotator_a, annotator_b = line.rsplit("\t", 2)
            label_a = int(annotator_a) - 1
            label_b = int(annotator_b) - 1
            texts.append(text)
            low_labels.append(min(label_a, label_b))
            high_labels.append(max(label_a, label_b))

    return (
        np.asarray(texts),
        np.asarray(low_labels, dtype=int),
        np.asarray(high_labels, dtype=int),
    )


def read_project_data():
    if not DATA_PATH.exists():
        return np.asarray([]), np.asarray([], dtype=float)

    df = pd.read_csv(DATA_PATH).dropna(subset=["text", "label"])
    df = df[df["label"].isin(LEVELS)].drop_duplicates(subset=["text"])
    return (
        df["text"].astype(str).to_numpy(),
        df["label"].map(LEVEL_TO_INDEX).astype(float).to_numpy(),
    )


def evaluate_predictions(raw_predictions, low_labels, high_labels):
    predictions = np.clip(np.rint(raw_predictions), 0, len(LEVELS) - 1).astype(int)
    exact_agreement = (predictions >= low_labels) & (predictions <= high_labels)
    distance = np.minimum(
        np.abs(predictions - low_labels),
        np.abs(predictions - high_labels),
    )
    midpoint = (low_labels + high_labels) / 2
    reference_labels = np.rint(midpoint).astype(int)

    return {
        "independent_test_accuracy": round(float(exact_agreement.mean()), 4),
        "within_one_level_accuracy": round(float((distance <= 1).mean()), 4),
        "mean_absolute_error": round(
            float(mean_absolute_error(midpoint, raw_predictions)),
            4,
        ),
        "confusion_matrix": confusion_matrix(
            reference_labels,
            predictions,
            labels=range(len(LEVELS)),
        ).tolist(),
        "predictions": predictions,
    }


def main():
    train_texts, train_low, train_high = read_cefr_sp_split("train")
    dev_texts, dev_low, dev_high = read_cefr_sp_split("dev")
    test_texts, test_low, test_high = read_cefr_sp_split("test")
    project_texts, project_labels = read_project_data()

    fit_texts = np.concatenate([train_texts, dev_texts, project_texts])
    fit_labels = np.concatenate(
        [
            (train_low + train_high) / 2,
            (dev_low + dev_high) / 2,
            project_labels,
        ]
    )

    pipeline = build_pipeline()
    pipeline.fit(fit_texts, fit_labels)
    raw_predictions = pipeline.predict(test_texts)
    evaluation = evaluate_predictions(raw_predictions, test_low, test_high)

    report = {
        "training_samples": int(len(fit_texts)),
        "independent_test_samples": int(len(test_texts)),
        "independent_test_accuracy": evaluation["independent_test_accuracy"],
        "within_one_level_accuracy": evaluation["within_one_level_accuracy"],
        "mean_absolute_error": evaluation["mean_absolute_error"],
        "confusion_matrix": evaluation["confusion_matrix"],
        "levels": LEVELS,
        "dataset": "CEFR-SP (Wiki-Auto + SCoRE) and project data",
        "evaluation_protocol": "Official independent test split; prediction agrees with either expert label",
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }

    bundle = {
        "pipeline": pipeline,
        "levels": LEVELS,
        "report": report,
        "format_version": 3,
    }

    with MODEL_PATH.open("wb") as model_file:
        pickle.dump(bundle, model_file)
    REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Model eğitildi: {len(fit_texts)} örnek")
    print(f"Bağımsız test örneği: {len(test_texts)}")
    print(
        "Uzman etiketiyle kesin uyum: "
        f"%{report['independent_test_accuracy'] * 100:.1f}"
    )
    print(
        "En fazla bir seviye sapma doğruluğu: "
        f"%{report['within_one_level_accuracy'] * 100:.1f}"
    )
    print(f"Ortalama mutlak hata: {report['mean_absolute_error']:.3f} seviye")


if __name__ == "__main__":
    main()
