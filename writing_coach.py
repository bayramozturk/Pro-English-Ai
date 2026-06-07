import os
import re
import shutil
from functools import lru_cache
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
RUNTIME_DIR = BASE_DIR / ".runtime"
JAVA_DIR = RUNTIME_DIR / "jre17"
LANGUAGE_TOOL_VERSION = "6.5"

CATEGORY_LABELS = {
    "TYPOS": "Yazım",
    "GRAMMAR": "Dilbilgisi",
    "PUNCTUATION": "Noktalama",
    "CASING": "Büyük/küçük harf",
    "STYLE": "Üslup",
    "REDUNDANCY": "Gereksiz tekrar",
    "TYPOGRAPHY": "Tipografi",
    "COLLOCATIONS": "Kelime kullanımı",
    "CONFUSED_WORDS": "Karıştırılan kelime",
    "SEMANTICS": "Anlam",
    "MISC": "Dil kullanımı",
}

FALLBACK_RULES = (
    (r"\bi\b", "I", "Kişi zamiri “I” her zaman büyük harfle yazılır.", "TYPOS"),
    (r"\bteh\b", "the", "Sık yapılan bir yazım yanlışı.", "TYPOS"),
    (r"\bdont\b", "don't", "Olumsuz yardımcı fiilde kesme işareti gerekir.", "TYPOS"),
    (r"\bcant\b", "can't", "Olumsuz yardımcı fiilde kesme işareti gerekir.", "TYPOS"),
    (r"\bwont\b", "won't", "Olumsuz yardımcı fiilde kesme işareti gerekir.", "TYPOS"),
    (r"\bim\b", "I'm", "“I am” kısaltmasında büyük harf ve kesme işareti gerekir.", "TYPOS"),
    (r"\bive\b", "I've", "“I have” kısaltmasında büyük harf ve kesme işareti gerekir.", "TYPOS"),
    (r"\bdidnt\b", "didn't", "Olumsuz yardımcı fiilde kesme işareti gerekir.", "TYPOS"),
    (r"\bdoesnt\b", "doesn't", "Olumsuz yardımcı fiilde kesme işareti gerekir.", "TYPOS"),
    (r"\bisnt\b", "isn't", "Olumsuz yardımcı fiilde kesme işareti gerekir.", "TYPOS"),
    (r"\barent\b", "aren't", "Olumsuz yardımcı fiilde kesme işareti gerekir.", "TYPOS"),
    (r"\b([Ii]|you|we|they) is\b", r"\1 are", "Özne ile “be” fiili uyumlu olmalıdır.", "GRAMMAR"),
    (r"\b(he|she|it) are\b", r"\1 is", "Tekil özne ile “is” kullanılmalıdır.", "GRAMMAR"),
    (r"\b([Ii]|you|we|they) has\b", r"\1 have", "Özne ile “have” fiili uyumlu olmalıdır.", "GRAMMAR"),
    (r"\b(he|she|it) have\b", r"\1 has", "Üçüncü tekil özne ile “has” kullanılmalıdır.", "GRAMMAR"),
    (r"\bhave went\b", "have gone", "Perfect yapılarda fiilin üçüncü hali kullanılır.", "GRAMMAR"),
    (r"\bhas went\b", "has gone", "Perfect yapılarda fiilin üçüncü hali kullanılır.", "GRAMMAR"),
    (r"\bmore better\b", "better", "Karşılaştırma eki iki kez kullanılmamalıdır.", "GRAMMAR"),
    (r"\ba ([aeiouAEIOU]\w*)\b", r"an \1", "Sesli harfle başlayan sözcüklerden önce genellikle “an” gelir.", "GRAMMAR"),
    (r"\s+([,.;!?])", r"\1", "Noktalama işaretinden önce boşluk bırakılmaz.", "PUNCTUATION"),
    (r"[ \t]{2,}", " ", "Sözcükler arasında tek boşluk kullanılmalıdır.", "TYPOGRAPHY"),
)


def _configure_local_runtime():
    portable_java = JAVA_DIR / "bin" / (
        "java.exe" if os.name == "nt" else "java"
    )
    language_tool_dir = RUNTIME_DIR / f"LanguageTool-{LANGUAGE_TOOL_VERSION}"
    system_java = shutil.which("java")
    if not language_tool_dir.exists() or (
        not portable_java.exists() and not system_java
    ):
        return False

    if portable_java.exists():
        os.environ["JAVA_HOME"] = str(JAVA_DIR)
        java_bin = str(JAVA_DIR / "bin")
        current_path = os.environ.get("PATH", "")
        if java_bin.lower() not in current_path.lower():
            os.environ["PATH"] = f"{java_bin}{os.pathsep}{current_path}"
    os.environ["LTP_PATH"] = str(RUNTIME_DIR)
    return True


@lru_cache(maxsize=1)
def get_language_tool():
    if not _configure_local_runtime():
        return None
    try:
        import language_tool_python

        return language_tool_python.LanguageTool(
            "en-US",
            language_tool_download_version=LANGUAGE_TOOL_VERSION,
        )
    except Exception:
        return None


def _line_and_column(text, offset):
    line = text.count("\n", 0, offset) + 1
    last_newline = text.rfind("\n", 0, offset)
    column = offset + 1 if last_newline == -1 else offset - last_newline
    return line, column


def _sentence_at(text, offset):
    start_candidates = [text.rfind(mark, 0, offset) for mark in ".!?\n"]
    start = max(start_candidates) + 1
    end_candidates = [
        position
        for mark in ".!?\n"
        if (position := text.find(mark, offset)) != -1
    ]
    end = min(end_candidates) + 1 if end_candidates else len(text)
    return text[start:end].strip()


def _turkish_explanation(category, original, replacement):
    quoted_original = f"“{original}”" if original else "Bu konum"
    quoted_replacement = f"“{replacement}”" if replacement else "Cümleyi yeniden düzenlemek"
    if category == "TYPOS":
        return (
            f"{quoted_original} standart İngilizce yazıma uymuyor. "
            f"Önerilen biçim: {quoted_replacement}."
        )
    if category == "GRAMMAR":
        return (
            f"{quoted_original} bölümünde özne-fiil, zaman veya sözcük biçimi "
            f"uyumu sorunlu. Önerilen kullanım: {quoted_replacement}."
        )
    if category == "PUNCTUATION":
        return (
            f"{quoted_original} çevresindeki noktalama düzenlenmeli. "
            f"Önerilen kullanım: {quoted_replacement}."
        )
    if category in {"CASING", "TYPOGRAPHY"}:
        return (
            f"{quoted_original} yazım biçimi düzeltilmeli. "
            f"Önerilen biçim: {quoted_replacement}."
        )
    return (
        f"{quoted_original} ifadesi bağlam içinde doğal veya doğru görünmüyor. "
        f"Önerilen kullanım: {quoted_replacement}."
    )


def _normalize_match(match, text):
    offset = int(getattr(match, "offset", 0))
    length = int(getattr(match, "error_length", 0))
    replacements = list(getattr(match, "replacements", []) or [])
    category_code = str(getattr(match, "category", "MISC") or "MISC").upper()
    line, column = _line_and_column(text, offset)
    original = text[offset : offset + length]
    replacement = replacements[0] if replacements else ""
    return {
        "rule_id": str(getattr(match, "rule_id", "LANGUAGE_RULE")),
        "category": CATEGORY_LABELS.get(category_code, "Dil kullanımı"),
        "category_code": category_code,
        "message": _turkish_explanation(category_code, original, replacement),
        "engine_message": str(
            getattr(match, "message", "This usage should be reviewed.")
        ),
        "original": original,
        "replacement": replacement,
        "suggestions": replacements[:5],
        "offset": offset,
        "length": length,
        "line": line,
        "column": column,
        "sentence": _sentence_at(text, offset),
    }


def _fallback_issues(text):
    issues = []
    occupied = []
    for pattern, replacement, message, category in FALLBACK_RULES:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            start, end = match.span()
            if any(start < used_end and end > used_start for used_start, used_end in occupied):
                continue
            corrected = match.expand(replacement)
            if corrected == match.group(0):
                continue
            line, column = _line_and_column(text, start)
            issues.append(
                {
                    "rule_id": f"PRO_ENGLISH_AI_{category}_{len(issues) + 1}",
                    "category": CATEGORY_LABELS[category],
                    "category_code": category,
                    "message": message,
                    "original": match.group(0),
                    "replacement": corrected,
                    "suggestions": [corrected],
                    "offset": start,
                    "length": end - start,
                    "line": line,
                    "column": column,
                    "sentence": _sentence_at(text, start),
                }
            )
            occupied.append((start, end))
    return sorted(issues, key=lambda item: item["offset"])


def apply_corrections(text, issues):
    corrected = text
    applicable = [issue for issue in issues if issue.get("replacement")]
    for issue in sorted(applicable, key=lambda item: item["offset"], reverse=True):
        start = issue["offset"]
        end = start + issue["length"]
        corrected = corrected[:start] + issue["replacement"] + corrected[end:]
    return corrected


def _sentence_comparisons(original, corrected):
    original_sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+|\n+", original)
        if sentence.strip()
    ]
    corrected_sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+|\n+", corrected)
        if sentence.strip()
    ]
    comparisons = []
    for index in range(max(len(original_sentences), len(corrected_sentences))):
        before = original_sentences[index] if index < len(original_sentences) else ""
        after = corrected_sentences[index] if index < len(corrected_sentences) else ""
        if before != after:
            comparisons.append({"before": before, "after": after})
    return comparisons


def analyze_writing(text, checker="auto"):
    clean_text = text.strip()
    if not clean_text:
        return {
            "issues": [],
            "corrected_text": "",
            "sentence_comparisons": [],
            "counts": {},
            "engine": "unavailable",
        }

    engine_mode = os.getenv(
        "PRO_ENGLISH_AI_WRITING_ENGINE",
        "auto",
    ).strip().lower()
    if checker == "auto" and engine_mode == "fallback":
        active_checker = None
    else:
        active_checker = get_language_tool() if checker == "auto" else checker
    engine = "LanguageTool 6.5"
    try:
        raw_matches = active_checker.check(clean_text) if active_checker else []
        issues = [_normalize_match(match, clean_text) for match in raw_matches]
    except Exception:
        issues = []
        active_checker = None

    if active_checker is None:
        issues = _fallback_issues(clean_text)
        engine = "Pro English AI hızlı yazım motoru"

    corrected_text = apply_corrections(clean_text, issues)
    counts = {}
    for issue in issues:
        category = issue["category"]
        counts[category] = counts.get(category, 0) + 1

    return {
        "issues": issues,
        "corrected_text": corrected_text,
        "sentence_comparisons": _sentence_comparisons(clean_text, corrected_text),
        "counts": counts,
        "engine": engine,
    }
