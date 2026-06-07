import math
import random


LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
DOMAINS = ["Grammar", "Vocabulary", "Reading"]


def _q(question_id, level, domain, prompt, options, answer, explanation):
    return {
        "id": question_id,
        "level": level,
        "domain": domain,
        "prompt": prompt,
        "options": options,
        "answer": answer,
        "explanation": explanation,
    }


QUESTION_BANK = [
    _q("a1-g1", "A1", "Grammar", "I ___ a student.", ["am", "is", "are", "be"], "am", "'I' öznesiyle 'am' kullanılır."),
    _q("a1-g2", "A1", "Grammar", "She ___ two brothers.", ["have", "has", "having", "is"], "has", "Üçüncü tekil şahısta 'have', 'has' olur."),
    _q("a1-v1", "A1", "Vocabulary", "Which word is a color?", ["table", "green", "teacher", "walk"], "green", "'Green' bir renktir."),
    _q("a1-v2", "A1", "Vocabulary", "What is the opposite of 'big'?", ["long", "fast", "small", "old"], "small", "'Small', 'big' kelimesinin karşıtıdır."),
    _q("a1-r1", "A1", "Reading", "Mia has a cat. The cat is white. What color is the cat?", ["Black", "White", "Brown", "Grey"], "White", "Metinde kedinin beyaz olduğu açıkça belirtilir."),
    _q("a1-r2", "A1", "Reading", "Tom goes to school at eight. Where does Tom go?", ["Home", "School", "Work", "The park"], "School", "Cümlede Tom'un okula gittiği söylenir."),
    _q("a2-g1", "A2", "Grammar", "Yesterday we ___ to the museum.", ["go", "went", "gone", "going"], "went", "'Yesterday' geçmiş zamanı gerektirir; 'go' fiilinin ikinci hali 'went'tir."),
    _q("a2-g2", "A2", "Grammar", "This book is ___ than that one.", ["interesting", "more interesting", "most interesting", "interest"], "more interesting", "Uzun sıfatlarda karşılaştırma 'more + adjective' ile yapılır."),
    _q("a2-v1", "A2", "Vocabulary", "A 'journey' is...", ["a type of food", "travel from one place to another", "a school subject", "a building"], "travel from one place to another", "'Journey' bir yerden başka bir yere yapılan yolculuktur."),
    _q("a2-v2", "A2", "Vocabulary", "Which word means 'very tired'?", ["excited", "exhausted", "surprised", "worried"], "exhausted", "'Exhausted', çok yorgun anlamına gelir."),
    _q("a2-r1", "A2", "Reading", "Leo missed the bus, so he walked to work. Why did he walk?", ["He likes walking.", "He missed the bus.", "His car was new.", "Work was closed."], "He missed the bus.", "'So' sonuç bildirir; otobüsü kaçırdığı için yürümüştür."),
    _q("a2-r2", "A2", "Reading", "The shop opens at nine, but Sara arrived at eight thirty. What happened?", ["The shop was open.", "Sara was early.", "Sara was late.", "The shop closed."], "Sara was early.", "Sara açılıştan otuz dakika önce geldiği için erkendir."),
    _q("b1-g1", "B1", "Grammar", "If it ___ tomorrow, we will stay home.", ["rains", "rained", "will rain", "would rain"], "rains", "First conditional yapısında if cümlesi geniş zaman alır."),
    _q("b1-g2", "B1", "Grammar", "I have lived here ___ 2020.", ["for", "since", "during", "from"], "since", "Belirli bir başlangıç noktasıyla 'since' kullanılır."),
    _q("b1-v1", "B1", "Vocabulary", "A 'reliable' person is someone who...", ["can be trusted", "talks loudly", "works slowly", "changes constantly"], "can be trusted", "'Reliable', güvenilebilir demektir."),
    _q("b1-v2", "B1", "Vocabulary", "Which word is closest to 'opportunity'?", ["chance", "problem", "habit", "rule"], "chance", "'Chance' bu bağlamda 'opportunity' kelimesine en yakındır."),
    _q("b1-r1", "B1", "Reading", "Nora accepted the job even though the salary was lower because it offered flexible hours. What mattered most to her?", ["A high salary", "Flexible hours", "A short contract", "A large office"], "Flexible hours", "Düşük maaşa rağmen işi kabul etmesinin nedeni esnek saatlerdir."),
    _q("b1-r2", "B1", "Reading", "The event was postponed due to heavy rain. It will take place next Friday instead. What changed?", ["The location", "The organizer", "The date", "The price"], "The date", "Etkinlik ertelendiği için tarihi değişmiştir."),
    _q("b2-g1", "B2", "Grammar", "I wish I ___ more carefully before making that decision.", ["think", "thought", "had thought", "would think"], "had thought", "Geçmişteki pişmanlık için 'wish + past perfect' kullanılır."),
    _q("b2-g2", "B2", "Grammar", "The report ___ by the time the manager arrived.", ["completed", "was completing", "had been completed", "has completed"], "had been completed", "Geçmişte başka bir olaydan önce tamamlanan edilgen eylem past perfect passive alır."),
    _q("b2-v1", "B2", "Vocabulary", "Which word is closest to 'meticulous'?", ["careless", "very careful", "impatient", "ordinary"], "very careful", "'Meticulous', ayrıntılara son derece dikkat eden anlamındadır."),
    _q("b2-v2", "B2", "Vocabulary", "To 'mitigate' a problem means to...", ["make it less severe", "ignore it completely", "describe it", "cause it"], "make it less severe", "'Mitigate', bir sorunun etkisini azaltmak demektir."),
    _q("b2-r1", "B2", "Reading", "Despite declining sales, the company increased its research budget, expecting innovation to improve its long-term position. Why was the budget increased?", ["To reduce staff", "To support future competitiveness", "To pay existing debts", "To lower product quality"], "To support future competitiveness", "Şirket inovasyonun uzun vadeli konumunu iyileştirmesini beklemektedir."),
    _q("b2-r2", "B2", "Reading", "The proposal is financially attractive; nevertheless, its environmental impact requires further investigation. What is the writer's position?", ["The proposal should be rejected immediately.", "Only the financial benefit matters.", "There is a benefit but also a concern.", "The environmental impact is positive."], "There is a benefit but also a concern.", "'Nevertheless' finansal faydaya karşı çevresel bir kaygı sunar."),
    _q("c1-g1", "C1", "Grammar", "Seldom ___ such a compelling argument.", ["I have heard", "have I heard", "I heard", "did I have heard"], "have I heard", "Olumsuz anlamlı zarf başa geldiğinde yardımcı fiil ve özne ters çevrilir."),
    _q("c1-g2", "C1", "Grammar", "It is essential that every applicant ___ the required documentation.", ["submits", "submit", "submitted", "will submit"], "submit", "Resmi gereklilik bildiren yapılarda subjunctive yalın fiil kullanılır."),
    _q("c1-v1", "C1", "Vocabulary", "An 'ambiguous' statement is...", ["open to more than one interpretation", "completely false", "highly emotional", "extremely detailed"], "open to more than one interpretation", "'Ambiguous', birden fazla yoruma açık demektir."),
    _q("c1-v2", "C1", "Vocabulary", "Which verb best completes the sentence? 'The evidence appears to ___ the original hypothesis.'", ["corroborate", "decorate", "postpone", "interrupt"], "corroborate", "'Corroborate', kanıtla desteklemek veya doğrulamak anlamındadır."),
    _q("c1-r1", "C1", "Reading", "While the policy may deliver short-term savings, critics contend that it merely transfers costs to future administrations. What is the criticism?", ["The savings are impossible to calculate.", "The policy delays rather than solves the cost problem.", "Future administrations support the policy.", "The policy has no short-term effect."], "The policy delays rather than solves the cost problem.", "'Transfers costs to future administrations' sorunun ertelendiğini ima eder."),
    _q("c1-r2", "C1", "Reading", "The author concedes that automation improves efficiency, yet cautions against treating productivity as the sole measure of social progress. What does the author reject?", ["All forms of automation", "Efficiency improvements", "A single-dimensional view of progress", "Social investment"], "A single-dimensional view of progress", "Yazar verimliliğin tek ölçüt olmasına karşı çıkar."),
    _q("c2-g1", "C2", "Grammar", "Had the findings been disclosed earlier, the committee ___ a different course of action.", ["would adopt", "would have adopted", "adopted", "had adopted"], "would have adopted", "Bu yapı devrik third conditional'dır: 'Had... would have + V3'."),
    _q("c2-g2", "C2", "Grammar", "So compelling ___ that even its staunchest critics reconsidered their position.", ["the evidence was", "was the evidence", "did the evidence", "the evidence did"], "was the evidence", "'So + adjective' başa geldiğinde devrik yapı kullanılır."),
    _q("c2-v1", "C2", "Vocabulary", "Which word best describes a distinction that is subtle but important?", ["negligible", "nuanced", "arbitrary", "obsolete"], "nuanced", "'Nuanced', ince anlam farklılıkları taşıyan demektir."),
    _q("c2-v2", "C2", "Vocabulary", "To 'reify' an abstract idea is to...", ["treat it as if it were concrete", "reject it as meaningless", "translate it accurately", "simplify its grammar"], "treat it as if it were concrete", "'Reify', soyut bir şeyi somut bir varlıkmış gibi ele almaktır."),
    _q("c2-r1", "C2", "Reading", "The essay's apparent neutrality is itself rhetorical: by framing contested assumptions as common sense, it forecloses alternatives before they can be considered. What is the central claim?", ["The essay has no argument.", "Neutral language can conceal ideological choices.", "Common sense is always reliable.", "Alternatives are fully evaluated."], "Neutral language can conceal ideological choices.", "Metin, tarafsız görünen çerçevenin ideolojik tercihleri gizleyebildiğini savunur."),
    _q("c2-r2", "C2", "Reading", "Rather than refuting the theory, the anomalous data expose the limits of the conditions under which it was formulated. How are the data interpreted?", ["As proof that the theory is useless", "As irrelevant measurement errors", "As evidence that the theory has a restricted scope", "As confirmation that the theory is universal"], "As evidence that the theory has a restricted scope", "Veriler teoriyi tümden reddetmez; geçerli olduğu koşulların sınırlı olduğunu gösterir."),
]


def build_assessment(mode="placement", level=None, seed=42):
    if mode == "placement":
        return list(QUESTION_BANK)
    if mode == "level_check":
        if level not in LEVELS:
            raise ValueError("Level check requires a valid CEFR level.")
        level_index = LEVELS.index(level)
        selected_levels = LEVELS[max(0, level_index - 1) : min(6, level_index + 2)]
        questions = [q for q in QUESTION_BANK if q["level"] in selected_levels]
        random.Random(seed).shuffle(questions)
        return questions[:18]
    raise ValueError(f"Unknown assessment mode: {mode}")


def _estimate_ability(questions, answers):
    candidates = [index / 100 for index in range(-50, 551)]
    best_theta, best_log_likelihood = 0.0, float("-inf")

    for theta in candidates:
        log_likelihood = -0.08 * (theta - 2.5) ** 2
        for question, answer in zip(questions, answers):
            difficulty = LEVELS.index(question["level"])
            probability = 1 / (1 + math.exp(-1.35 * (theta - difficulty)))
            probability = min(max(probability, 0.001), 0.999)
            correct = answer == question["answer"]
            log_likelihood += math.log(probability if correct else 1 - probability)
        if log_likelihood > best_log_likelihood:
            best_theta = theta
            best_log_likelihood = log_likelihood

    return best_theta


def score_assessment(questions, answers):
    if len(questions) != len(answers):
        raise ValueError("Question and answer counts must match.")
    if not questions:
        raise ValueError("Assessment must contain questions.")

    correct_count = sum(
        answer == question["answer"]
        for question, answer in zip(questions, answers)
    )
    ability = _estimate_ability(questions, answers)
    # A conservative cut prevents a borderline score from promoting the
    # learner before there is enough evidence at the next CEFR level.
    level_index = min(max(math.floor(ability + 0.25), 0), len(LEVELS) - 1)

    domain_scores = {}
    for domain in DOMAINS:
        pairs = [
            (question, answer)
            for question, answer in zip(questions, answers)
            if question["domain"] == domain
        ]
        correct = sum(answer == question["answer"] for question, answer in pairs)
        domain_scores[domain] = round(correct / len(pairs) * 100) if pairs else 0

    level_scores = {}
    for level in LEVELS:
        pairs = [
            (question, answer)
            for question, answer in zip(questions, answers)
            if question["level"] == level
        ]
        if pairs:
            correct = sum(answer == question["answer"] for question, answer in pairs)
            level_scores[level] = round(correct / len(pairs) * 100)

    ordered_domains = sorted(domain_scores, key=domain_scores.get, reverse=True)
    confidence = min(99, round(55 + len(questions) * 1.1))
    return {
        "level": LEVELS[level_index],
        "level_index": level_index,
        "ability": round(ability, 2),
        "correct": correct_count,
        "total": len(questions),
        "score_percent": round(correct_count / len(questions) * 100),
        "domain_scores": domain_scores,
        "level_scores": level_scores,
        "strongest_domain": ordered_domains[0],
        "focus_domain": ordered_domains[-1],
        "confidence": confidence,
    }
