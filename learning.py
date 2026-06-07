from datetime import date


LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]

DOMAIN_TASKS = {
    "Grammar": [
        ("Pattern practice", "Hedef yapıyla 8 özgün cümle yazın ve 3 tanesini soru biçimine dönüştürün.", 15),
        ("Error correction", "Kendi eski metninizden 5 cümle seçip zaman ve sözdizimi açısından yeniden düzenleyin.", 15),
    ],
    "Vocabulary": [
        ("Active vocabulary", "Hedef seviyenize uygun 10 kelime seçin; her birini kişisel bir bağlamda kullanın.", 20),
        ("Precision drill", "5 genel kelimeyi daha kesin eş anlamlılarla değiştirerek kısa bir paragraf yazın.", 15),
    ],
    "Reading": [
        ("Close reading", "Kısa bir İngilizce makalede ana fikir, iki destekleyici nokta ve yazarın tutumunu çıkarın.", 20),
        ("Inference practice", "Bir paragraf okuyup açıkça yazılmayan üç çıkarımı İngilizce olarak not edin.", 15),
    ],
}

LEVEL_TASKS = {
    "A1": ("Daily foundations", "Günlük rutininizi present simple ile 8 kısa cümlede anlatın."),
    "A2": ("Connected paragraph", "Geçmişte yaşadığınız bir olayı first, then, because ve finally ile anlatın."),
    "B1": ("Opinion builder", "Bir görüşü neden ve örneklerle destekleyen 120 kelimelik paragraf yazın."),
    "B2": ("Argument practice", "Bir konunun avantaj ve dezavantajlarını 180 kelimede karşılaştırın."),
    "C1": ("Critical response", "Soyut bir iddiayı değerlendirip karşı görüş içeren 220 kelimelik metin yazın."),
    "C2": ("Rhetorical control", "Aynı görüşü akademik ve ikna edici iki farklı üslupla yeniden yazın."),
}


def _week_key(today=None):
    today = today or date.today()
    year, week, _ = today.isocalendar()
    return f"{year}-W{week:02d}"


def generate_weekly_plan(current_level, target_level, focus_domain, today=None):
    if current_level not in LEVELS:
        current_level = "A1"
    if target_level not in LEVELS:
        target_level = "B2"
    if focus_domain not in DOMAIN_TASKS:
        focus_domain = "Grammar"

    week = _week_key(today)
    current_index = LEVELS.index(current_level)
    target_index = LEVELS.index(target_level)
    practice_level = LEVELS[min(max(current_index + (target_index > current_index), 0), 5)]
    level_title, level_description = LEVEL_TASKS[practice_level]

    raw_tasks = [
        (*DOMAIN_TASKS[focus_domain][0], focus_domain),
        (*DOMAIN_TASKS[focus_domain][1], focus_domain),
        (level_title, level_description, 25, "Writing"),
        (
            "Speaking transfer",
            "Bugünkü yazma görevinizi notlara bakmadan 2 dakika boyunca sesli özetleyin.",
            10,
            "Speaking",
        ),
        (
            "Weekly reflection",
            "Bu hafta öğrendiğiniz üç yapıyı ve hâlâ zorlandığınız bir noktayı İngilizce yazın.",
            10,
            "Reflection",
        ),
    ]

    return [
        {
            "id": f"{week}-{current_level}-{target_level}-{index}",
            "week": week,
            "title": title,
            "description": description,
            "minutes": minutes,
            "domain": domain,
        }
        for index, (title, description, minutes, domain) in enumerate(raw_tasks, start=1)
    ]


def infer_learning_context(profile, analyses, assessment):
    current_level = analyses[0]["level"] if analyses else "A1"
    focus_domain = "Grammar"
    if assessment and assessment.get("details"):
        focus_domain = assessment["details"].get("focus_domain", focus_domain)
        current_level = assessment["details"].get("level", current_level)
    return {
        "current_level": current_level,
        "target_level": profile.get("target_level", "B2"),
        "focus_domain": focus_domain,
    }
