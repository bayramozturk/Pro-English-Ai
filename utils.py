import re

import numpy as np
from scipy.sparse import csr_matrix
from sklearn.base import BaseEstimator, TransformerMixin


WORD_PATTERN = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
SENTENCE_PATTERN = re.compile(r"[.!?]+")


def tokenize_words(text):
    """Return English word tokens without requiring downloaded NLTK data."""
    return WORD_PATTERN.findall(str(text).lower())


def clean_text(text):
    """Normalize English text while preserving contractions."""
    return " ".join(tokenize_words(text))


def get_text_metrics(text):
    """Calculate compact, user-facing readability indicators."""
    words = tokenize_words(text)
    sentences = [part for part in SENTENCE_PATTERN.split(str(text)) if part.strip()]
    word_count = len(words)
    sentence_count = max(len(sentences), 1) if word_count else 0
    complex_count = sum(len(word) >= 7 for word in words)
    unique_count = len(set(words))

    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_sent_len": round(word_count / sentence_count, 1) if sentence_count else 0,
        "complex_ratio": round(100 * complex_count / word_count, 1) if word_count else 0,
        "vocabulary_diversity": round(100 * unique_count / word_count, 1) if word_count else 0,
    }


class TextStyleFeatures(BaseEstimator, TransformerMixin):
    """Extract structural language features that complement TF-IDF."""

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        rows = []
        for text in X:
            text = str(text)
            words = tokenize_words(text)
            lengths = np.asarray([len(word) for word in words], dtype=float)

            if not words:
                lengths = np.asarray([0.0])

            word_count = max(len(words), 1)
            rows.append(
                [
                    np.log1p(len(words)),
                    lengths.mean(),
                    lengths.std(),
                    lengths.max(),
                    np.count_nonzero(lengths >= 7) / word_count,
                    np.count_nonzero(lengths >= 10) / word_count,
                    len(set(words)) / word_count,
                    np.log1p(len(text)),
                    text.count(","),
                    text.count(";") + text.count(":"),
                ]
            )

        return csr_matrix(rows, dtype=float)
