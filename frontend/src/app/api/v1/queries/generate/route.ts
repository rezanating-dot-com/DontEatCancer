import { NextRequest, NextResponse } from "next/server";

// Known translations for common food additives
const KNOWN_TRANSLATIONS: Record<string, Record<string, string>> = {
  "sodium nitrite": { zh: "亚硝酸钠", ar: "نتريت الصوديوم", fr: "nitrite de sodium", de: "Natriumnitrit" },
  "sodium nitrate": { zh: "硝酸钠", ar: "نترات الصوديوم", fr: "nitrate de sodium", de: "Natriumnitrat" },
  "monosodium glutamate": { zh: "谷氨酸钠", ar: "غلوتامات أحادية الصوديوم", fr: "glutamate monosodique", de: "Mononatriumglutamat" },
  "aspartame": { zh: "阿斯巴甜", ar: "أسبارتام", fr: "aspartame", de: "Aspartam" },
  "butylated hydroxyanisole": { zh: "丁基羟基茴香醚", ar: "بوتيل هيدروكسي أنيسول", fr: "hydroxyanisole butylé", de: "Butylhydroxyanisol" },
  "butylated hydroxytoluene": { zh: "二丁基羟基甲苯", ar: "بوتيل هيدروكسي تولوين", fr: "hydroxytoluène butylé", de: "Butylhydroxytoluol" },
  "titanium dioxide": { zh: "二氧化钛", ar: "ثاني أكسيد التيتانيوم", fr: "dioxyde de titane", de: "Titandioxid" },
  "potassium bromate": { zh: "溴酸钾", ar: "برومات البوتاسيوم", fr: "bromate de potassium", de: "Kaliumbromat" },
  "sodium benzoate": { zh: "苯甲酸钠", ar: "بنزوات الصوديوم", fr: "benzoate de sodium", de: "Natriumbenzoat" },
  "tartrazine": { zh: "柠檬黄", ar: "تارترازين", fr: "tartrazine", de: "Tartrazin" },
  "red 40": { zh: "诱惑红", ar: "أحمر 40", fr: "rouge allura", de: "Allurarot" },
  "caramel color": { zh: "焦糖色", ar: "لون الكراميل", fr: "colorant caramel", de: "Zuckerkulör" },
  "carrageenan": { zh: "卡拉胶", ar: "كاراجينان", fr: "carraghénane", de: "Carrageen" },
  "high fructose corn syrup": { zh: "高果糖玉米糖浆", ar: "شراب الذرة عالي الفركتوز", fr: "sirop de maïs à haute teneur en fructose", de: "Maissirup mit hohem Fructosegehalt" },
  "acesulfame potassium": { zh: "安赛蜜", ar: "أسيسولفام البوتاسيوم", fr: "acésulfame de potassium", de: "Acesulfam-K" },
  "sucralose": { zh: "三氯蔗糖", ar: "سوكرالوز", fr: "sucralose", de: "Sucralose" },
  "polysorbate 80": { zh: "聚山梨酯80", ar: "بوليسوربات 80", fr: "polysorbate 80", de: "Polysorbat 80" },
  "sodium sulfite": { zh: "亚硫酸钠", ar: "كبريتيت الصوديوم", fr: "sulfite de sodium", de: "Natriumsulfit" },
  "propyl gallate": { zh: "没食子酸丙酯", ar: "بروبيل غالات", fr: "gallate de propyle", de: "Propylgallat" },
};

// Health/cancer-related keywords per language
const HEALTH_KEYWORDS: Record<string, string[]> = {
  en: ["cancer", "carcinogen", "tumor", "genotoxic", "mutagenic", "health risk", "toxicity", "safety"],
  zh: ["癌症", "致癌", "肿瘤", "基因毒性", "致突变", "健康风险", "毒性", "安全性"],
  ar: ["سرطان", "مسرطن", "ورم", "سمية جينية", "طفرات", "مخاطر صحية", "سمية", "سلامة"],
  fr: ["cancer", "cancérogène", "tumeur", "génotoxique", "mutagène", "risque sanitaire", "toxicité", "sécurité"],
  de: ["Krebs", "karzinogen", "Tumor", "genotoxisch", "mutagen", "Gesundheitsrisiko", "Toxizität", "Sicherheit"],
};

function healthBoolean(lang: string): string {
  const terms = HEALTH_KEYWORDS[lang] || HEALTH_KEYWORDS.en;
  return terms.map((t) => `"${t}"`).join(" OR ");
}

async function translateViaClaude(ingredient: string): Promise<Record<string, string>> {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) return {};

  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify({
      model: "claude-sonnet-4-20250514",
      max_tokens: 300,
      messages: [
        {
          role: "user",
          content: `Translate the food ingredient/additive "${ingredient}" into these languages. Return ONLY a JSON object with keys: zh, ar, fr, de. Use the standard scientific/regulatory name in each language. Example: {"zh": "亚硝酸钠", "ar": "نتريت الصوديوم", "fr": "nitrite de sodium", "de": "Natriumnitrit"}`,
        },
      ],
    }),
  });

  if (!res.ok) return {};

  const data = await res.json();
  let text: string = data.content?.[0]?.text?.trim() || "";
  if (text.includes("{")) {
    text = text.slice(text.indexOf("{"), text.lastIndexOf("}") + 1);
  }
  try {
    return JSON.parse(text);
  } catch {
    return {};
  }
}

function formatForDatabase(
  queries: Record<string, string>,
  database: string
): Record<string, string> {
  if (database === "scopus") {
    return Object.fromEntries(
      Object.entries(queries).map(([lang, q]) => [lang, `TITLE-ABS-KEY(${q})`])
    );
  }
  if (database === "wos") {
    return Object.fromEntries(
      Object.entries(queries).map(([lang, q]) => [lang, `TS=(${q})`])
    );
  }
  // EBSCO and PubMed: standard Boolean
  return queries;
}

export async function POST(request: NextRequest) {
  const sp = request.nextUrl.searchParams;
  const ingredient = sp.get("ingredient") || "";
  const database = sp.get("database") || "ebsco";

  if (!ingredient) {
    return NextResponse.json(
      { detail: "ingredient parameter is required" },
      { status: 400 }
    );
  }

  const ingredientLower = ingredient.toLowerCase().trim();

  // Get translations
  let translations: Record<string, string>;
  if (ingredientLower in KNOWN_TRANSLATIONS) {
    translations = KNOWN_TRANSLATIONS[ingredientLower];
  } else {
    translations = await translateViaClaude(ingredient);
  }

  // Build queries
  const queries: Record<string, string> = {};
  queries.en = `("${ingredient}") AND (${healthBoolean("en")})`;

  for (const lang of ["zh", "ar", "fr", "de"]) {
    if (lang in translations) {
      queries[lang] = `("${translations[lang]}") AND (${healthBoolean(lang)})`;
    }
  }

  const formatted = formatForDatabase(queries, database);

  return NextResponse.json({
    ingredient,
    database,
    queries: formatted,
  });
}
