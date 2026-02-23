"""Generates multilingual Boolean search queries for academic databases."""

import json

import anthropic

from app.config import settings

# Known translations for common food additives
KNOWN_TRANSLATIONS: dict[str, dict[str, str]] = {
    "sodium nitrite": {"zh": "亚硝酸钠", "ar": "نتريت الصوديوم", "fr": "nitrite de sodium", "de": "Natriumnitrit"},
    "sodium nitrate": {"zh": "硝酸钠", "ar": "نترات الصوديوم", "fr": "nitrate de sodium", "de": "Natriumnitrat"},
    "monosodium glutamate": {"zh": "谷氨酸钠", "ar": "غلوتامات أحادية الصوديوم", "fr": "glutamate monosodique", "de": "Mononatriumglutamat"},
    "aspartame": {"zh": "阿斯巴甜", "ar": "أسبارتام", "fr": "aspartame", "de": "Aspartam"},
    "butylated hydroxyanisole": {"zh": "丁基羟基茴香醚", "ar": "بوتيل هيدروكسي أنيسول", "fr": "hydroxyanisole butylé", "de": "Butylhydroxyanisol"},
    "butylated hydroxytoluene": {"zh": "二丁基羟基甲苯", "ar": "بوتيل هيدروكسي تولوين", "fr": "hydroxytoluène butylé", "de": "Butylhydroxytoluol"},
    "titanium dioxide": {"zh": "二氧化钛", "ar": "ثاني أكسيد التيتانيوم", "fr": "dioxyde de titane", "de": "Titandioxid"},
    "potassium bromate": {"zh": "溴酸钾", "ar": "برومات البوتاسيوم", "fr": "bromate de potassium", "de": "Kaliumbromat"},
    "sodium benzoate": {"zh": "苯甲酸钠", "ar": "بنزوات الصوديوم", "fr": "benzoate de sodium", "de": "Natriumbenzoat"},
    "tartrazine": {"zh": "柠檬黄", "ar": "تارترازين", "fr": "tartrazine", "de": "Tartrazin"},
    "red 40": {"zh": "诱惑红", "ar": "أحمر 40", "fr": "rouge allura", "de": "Allurarot"},
    "caramel color": {"zh": "焦糖色", "ar": "لون الكراميل", "fr": "colorant caramel", "de": "Zuckerkulör"},
    "carrageenan": {"zh": "卡拉胶", "ar": "كاراجينان", "fr": "carraghénane", "de": "Carrageen"},
    "high fructose corn syrup": {"zh": "高果糖玉米糖浆", "ar": "شراب الذرة عالي الفركتوز", "fr": "sirop de maïs à haute teneur en fructose", "de": "Maissirup mit hohem Fructosegehalt"},
    "acesulfame potassium": {"zh": "安赛蜜", "ar": "أسيسولفام البوتاسيوم", "fr": "acésulfame de potassium", "de": "Acesulfam-K"},
    "sucralose": {"zh": "三氯蔗糖", "ar": "سوكرالوز", "fr": "sucralose", "de": "Sucralose"},
    "polysorbate 80": {"zh": "聚山梨酯80", "ar": "بوليسوربات 80", "fr": "polysorbate 80", "de": "Polysorbat 80"},
    "sodium sulfite": {"zh": "亚硫酸钠", "ar": "كبريتيت الصوديوم", "fr": "sulfite de sodium", "de": "Natriumsulfit"},
    "propyl gallate": {"zh": "没食子酸丙酯", "ar": "بروبيل غالات", "fr": "gallate de propyle", "de": "Propylgallat"},
}

# Health/cancer-related keywords per language
HEALTH_KEYWORDS: dict[str, list[str]] = {
    "en": ["cancer", "carcinogen", "tumor", "genotoxic", "mutagenic", "health risk", "toxicity", "safety"],
    "zh": ["癌症", "致癌", "肿瘤", "基因毒性", "致突变", "健康风险", "毒性", "安全性"],
    "ar": ["سرطان", "مسرطن", "ورم", "سمية جينية", "طفرات", "مخاطر صحية", "سمية", "سلامة"],
    "fr": ["cancer", "cancérogène", "tumeur", "génotoxique", "mutagène", "risque sanitaire", "toxicité", "sécurité"],
    "de": ["Krebs", "karzinogen", "Tumor", "genotoxisch", "mutagen", "Gesundheitsrisiko", "Toxizität", "Sicherheit"],
}


def _health_boolean(lang: str) -> str:
    """Build OR clause for health keywords in given language."""
    terms = HEALTH_KEYWORDS.get(lang, HEALTH_KEYWORDS["en"])
    return " OR ".join(f'"{t}"' for t in terms)


def _translate_via_claude(ingredient: str) -> dict[str, str]:
    """Use Claude to translate an ingredient name into zh, ar, fr, de."""
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": (
                f'Translate the food ingredient/additive "{ingredient}" into these languages. '
                "Return ONLY a JSON object with keys: zh, ar, fr, de. "
                "Use the standard scientific/regulatory name in each language. "
                "Example: {\"zh\": \"亚硝酸钠\", \"ar\": \"نتريت الصوديوم\", \"fr\": \"nitrite de sodium\", \"de\": \"Natriumnitrit\"}"
            ),
        }],
    )
    text = response.content[0].text.strip()
    # Extract JSON from response
    if "{" in text:
        text = text[text.index("{"):text.rindex("}") + 1]
    return json.loads(text)


def generate_queries(ingredient: str, use_ai: bool = True) -> dict[str, str]:
    """Generate multilingual Boolean search queries for an ingredient.

    Returns dict mapping language code to search query string.
    """
    ingredient_lower = ingredient.lower().strip()

    # Get translations
    if ingredient_lower in KNOWN_TRANSLATIONS:
        translations = KNOWN_TRANSLATIONS[ingredient_lower]
    elif use_ai:
        translations = _translate_via_claude(ingredient)
    else:
        # Fallback: English only
        translations = {}

    queries: dict[str, str] = {}

    # English query
    health_en = _health_boolean("en")
    queries["en"] = f'("{ingredient}") AND ({health_en})'

    # Translated queries
    for lang in ["zh", "ar", "fr", "de"]:
        if lang not in translations:
            continue
        translated_name = translations[lang]
        health = _health_boolean(lang)
        queries[lang] = f'("{translated_name}") AND ({health})'

    return queries


def format_for_database(queries: dict[str, str], database: str = "ebsco") -> dict[str, str]:
    """Format queries for a specific database's search syntax.

    EBSCO, Scopus, and WoS all accept standard Boolean with quotes.
    Minor adjustments per database.
    """
    if database == "scopus":
        # Scopus uses TITLE-ABS-KEY()
        return {lang: f"TITLE-ABS-KEY({q})" for lang, q in queries.items()}
    elif database == "wos":
        # Web of Science uses TS= (Topic Search)
        return {lang: f"TS=({q})" for lang, q in queries.items()}
    # EBSCO and PubMed: standard Boolean works
    return queries


LANGUAGE_NAMES = {"en": "English", "zh": "Chinese", "ar": "Arabic", "fr": "French", "de": "German"}
