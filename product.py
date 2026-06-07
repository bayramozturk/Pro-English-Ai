import json
from datetime import datetime, timezone

import numpy as np

from utils import get_text_metrics


LEVEL_PROFILES = {
    "A1": {
        "name": "Beginner",
        "summary": "Günlük ihtiyaçları anlatan kısa ve temel cümleler kurabiliyorsunuz.",
        "focus": ["Temel zamanlar", "Günlük kelime hazinesi", "Basit cümle bağlantıları"],
        "next_step": "A2 için geçmiş zaman ve günlük rutinler üzerine 5-6 cümlelik paragraflar yazın.",
    },
    "A2": {
        "name": "Elementary",
        "summary": "Tanıdık konularda doğrudan ve anlaşılır bir anlatım kurabiliyorsunuz.",
        "focus": ["Geçmiş ve gelecek zaman", "Bağlaç kullanımı", "Betimleyici kelimeler"],
        "next_step": "B1 için because, although ve if kullanarak fikirlerinizi gerekçelendirin.",
    },
    "B1": {
        "name": "Intermediate",
        "summary": "Deneyimleri ve görüşleri bağlantılı paragraflarla ifade edebiliyorsunuz.",
        "focus": ["Paragraf bütünlüğü", "Koşul cümleleri", "Kelime çeşitliliği"],
        "next_step": "B2 için aynı fikri farklı yapılarla açıklayın ve daha kesin sözcükler seçin.",
    },
    "B2": {
        "name": "Upper Intermediate",
        "summary": "Karmaşık konuları ayrıntılandırıp görüşlerinizi güçlü biçimde savunabiliyorsunuz.",
        "focus": ["Akademik bağlaçlar", "Edilgen yapılar", "Nüanslı kelime seçimi"],
        "next_step": "C1 için karşıt görüşleri tartışan, örnek ve sonuç içeren metinler yazın.",
    },
    "C1": {
        "name": "Advanced",
        "summary": "Soyut ve akademik fikirleri esnek, ayrıntılı ve tutarlı biçimde aktarabiliyorsunuz.",
        "focus": ["Üslup kontrolü", "Deyimsel kullanım", "İleri düzey metin organizasyonu"],
        "next_step": "C2 için ton, ima ve retorik tercihler üzerinde bilinçli denemeler yapın.",
    },
    "C2": {
        "name": "Proficient",
        "summary": "Karmaşık anlamları hassas, doğal ve bağlama uygun bir dille ifade edebiliyorsunuz.",
        "focus": ["Retorik incelik", "Alan dili", "Editoryal hassasiyet"],
        "next_step": "Farklı hedef kitleler için aynı metni akademik, profesyonel ve gündelik tonlarda yeniden yazın.",
    },
}


def _input_quality(metrics):
    word_count = metrics["word_count"]
    sentence_count = metrics["sentence_count"]
    length_score = min(word_count / 80, 1.0)
    sentence_score = min(sentence_count / 4, 1.0)
    quality = round(100 * (0.72 * length_score + 0.28 * sentence_score))

    if word_count < 8:
        label = "Yetersiz örnek"
    elif word_count < 20:
        label = "Sınırlı örnek"
    elif quality < 70:
        label = "İyi örnek"
    else:
        label = "Güçlü örnek"
    return quality, label


def analyze_text(model, levels, text):
    metrics = get_text_metrics(text)
    raw_score = float(model.predict([text])[0])
    level_index = int(np.clip(np.rint(raw_score), 0, len(levels) - 1))
    level = levels[level_index]

    quality_score, quality_label = _input_quality(metrics)
    model_stability = max(0.0, 1 - min(abs(raw_score - level_index), 0.5) / 0.5)
    reliability = round(100 * (0.58 * model_stability + 0.42 * quality_score / 100))

    lower_index = max(0, int(np.floor(raw_score)))
    upper_index = min(len(levels) - 1, int(np.ceil(raw_score)))
    likely_range = (
        levels[lower_index]
        if lower_index == upper_index
        else f"{levels[lower_index]}-{levels[upper_index]}"
    )

    profile = LEVEL_PROFILES[level]
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "level_index": level_index,
        "level_name": profile["name"],
        "summary": profile["summary"],
        "focus": profile["focus"],
        "next_step": profile["next_step"],
        "raw_score": round(raw_score, 3),
        "likely_range": likely_range,
        "reliability": reliability,
        "quality_score": quality_score,
        "quality_label": quality_label,
        "metrics": metrics,
        "text": text,
    }


def build_report(result, validation):
    report = {
        "product": "Pro English AI",
        "analysis": result,
        "model_validation": {
            "independent_test_accuracy": validation.get("independent_test_accuracy"),
            "within_one_level_accuracy": validation.get("within_one_level_accuracy"),
            "independent_test_samples": validation.get("independent_test_samples"),
            "dataset": validation.get("dataset"),
        },
        "disclaimer": "This result is an AI-supported estimate and is not an official language certificate.",
    }
    return json.dumps(report, ensure_ascii=False, indent=2)
