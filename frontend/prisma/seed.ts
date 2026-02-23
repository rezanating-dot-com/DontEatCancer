import { PrismaClient } from "../src/generated/prisma/client";
import { PrismaNeon } from "@prisma/adapter-neon";

const adapter = new PrismaNeon({ connectionString: process.env.DATABASE_URL });
const prisma = new PrismaClient({ adapter });

interface SeedItem {
  name: string;
  cas: string | null;
  e: string | null;
  cat: string;
  aliases: [string, string][];
}

function slugify(name: string): string {
  return name
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, "")
    .replace(/[\s_]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

const SEED_DATA: SeedItem[] = [
  // Preservatives
  { name: "Sodium Nitrite", cas: "7632-00-0", e: "E250", cat: "preservative",
    aliases: [["亚硝酸钠", "zh"], ["نتريت الصوديوم", "ar"], ["nitrite de sodium", "fr"], ["Natriumnitrit", "de"]] },
  { name: "Sodium Nitrate", cas: "7631-99-4", e: "E251", cat: "preservative",
    aliases: [["硝酸钠", "zh"], ["نترات الصوديوم", "ar"], ["nitrate de sodium", "fr"], ["Natriumnitrat", "de"]] },
  { name: "Sodium Benzoate", cas: "532-32-1", e: "E211", cat: "preservative",
    aliases: [["苯甲酸钠", "zh"], ["بنزوات الصوديوم", "ar"], ["benzoate de sodium", "fr"], ["Natriumbenzoat", "de"]] },
  { name: "Potassium Sorbate", cas: "24634-61-5", e: "E202", cat: "preservative",
    aliases: [["山梨酸钾", "zh"], ["سوربات البوتاسيوم", "ar"], ["sorbate de potassium", "fr"], ["Kaliumsorbat", "de"]] },
  { name: "Sodium Sulfite", cas: "7757-83-7", e: "E221", cat: "preservative",
    aliases: [["亚硫酸钠", "zh"], ["كبريتيت الصوديوم", "ar"], ["sulfite de sodium", "fr"], ["Natriumsulfit", "de"]] },
  { name: "Sodium Metabisulfite", cas: "7681-57-4", e: "E223", cat: "preservative",
    aliases: [["焦亚硫酸钠", "zh"], ["ميتابيسلفيت الصوديوم", "ar"], ["métabisulfite de sodium", "fr"], ["Natriumdisulfit", "de"]] },
  { name: "Potassium Nitrate", cas: "7757-79-1", e: "E252", cat: "preservative",
    aliases: [["硝酸钾", "zh"], ["نترات البوتاسيوم", "ar"], ["nitrate de potassium", "fr"], ["Kaliumnitrat", "de"]] },
  { name: "Calcium Propionate", cas: "4075-81-4", e: "E282", cat: "preservative",
    aliases: [["丙酸钙", "zh"], ["بروبيونات الكالسيوم", "ar"], ["propionate de calcium", "fr"], ["Calciumpropionat", "de"]] },
  { name: "Nisin", cas: "1414-45-5", e: "E234", cat: "preservative",
    aliases: [["乳链菌肽", "zh"], ["نيسين", "ar"], ["nisine", "fr"], ["Nisin", "de"]] },
  { name: "Natamycin", cas: "7681-93-8", e: "E235", cat: "preservative",
    aliases: [["纳他霉素", "zh"], ["ناتاميسين", "ar"], ["natamycine", "fr"], ["Natamycin", "de"]] },

  // Colorants
  { name: "Tartrazine", cas: "1934-21-0", e: "E102", cat: "colorant",
    aliases: [["柠檬黄", "zh"], ["تارترازين", "ar"], ["tartrazine", "fr"], ["Tartrazin", "de"]] },
  { name: "Allura Red AC", cas: "25956-17-6", e: "E129", cat: "colorant",
    aliases: [["诱惑红", "zh"], ["أحمر ألورا", "ar"], ["rouge allura", "fr"], ["Allurarot", "de"]] },
  { name: "Brilliant Blue FCF", cas: "3844-45-9", e: "E133", cat: "colorant",
    aliases: [["亮蓝", "zh"], ["أزرق لامع", "ar"], ["bleu brillant", "fr"], ["Brillantblau", "de"]] },
  { name: "Sunset Yellow FCF", cas: "2783-94-0", e: "E110", cat: "colorant",
    aliases: [["日落黄", "zh"], ["أصفر الغروب", "ar"], ["jaune orangé S", "fr"], ["Gelborange S", "de"]] },
  { name: "Caramel Color", cas: "8028-89-5", e: "E150", cat: "colorant",
    aliases: [["焦糖色", "zh"], ["لون الكراميل", "ar"], ["colorant caramel", "fr"], ["Zuckerkulör", "de"]] },
  { name: "Titanium Dioxide", cas: "13463-67-7", e: "E171", cat: "colorant",
    aliases: [["二氧化钛", "zh"], ["ثاني أكسيد التيتانيوم", "ar"], ["dioxyde de titane", "fr"], ["Titandioxid", "de"]] },
  { name: "Erythrosine", cas: "16423-68-0", e: "E127", cat: "colorant",
    aliases: [["赤藓红", "zh"], ["إريثروسين", "ar"], ["érythrosine", "fr"], ["Erythrosin", "de"]] },
  { name: "Quinoline Yellow", cas: "8004-92-0", e: "E104", cat: "colorant",
    aliases: [["喹啉黄", "zh"], ["أصفر كينولين", "ar"], ["jaune de quinoléine", "fr"], ["Chinolingelb", "de"]] },
  { name: "Amaranth", cas: "915-67-3", e: "E123", cat: "colorant",
    aliases: [["苋菜红", "zh"], ["أمارانث", "ar"], ["amarante", "fr"], ["Amaranth", "de"]] },
  { name: "Carmoisine", cas: "3567-69-9", e: "E122", cat: "colorant",
    aliases: [["偶氮玉红", "zh"], ["كارمويسين", "ar"], ["carmoisine", "fr"], ["Azorubin", "de"]] },
  { name: "Ponceau 4R", cas: "2611-82-7", e: "E124", cat: "colorant",
    aliases: [["胭脂红", "zh"], ["بونسو 4آر", "ar"], ["ponceau 4R", "fr"], ["Cochenillerot A", "de"]] },
  { name: "Patent Blue V", cas: "3536-49-0", e: "E131", cat: "colorant",
    aliases: [["专利蓝V", "zh"], ["أزرق براءة اختراع", "ar"], ["bleu patenté V", "fr"], ["Patentblau V", "de"]] },
  { name: "Indigo Carmine", cas: "860-22-0", e: "E132", cat: "colorant",
    aliases: [["靛蓝", "zh"], ["نيلي كارمين", "ar"], ["carmin d'indigo", "fr"], ["Indigotin", "de"]] },
  { name: "Green S", cas: "3087-16-9", e: "E142", cat: "colorant",
    aliases: [["酸性亮绿", "zh"], ["أخضر إس", "ar"], ["vert S", "fr"], ["Grün S", "de"]] },
  { name: "Fast Green FCF", cas: "2353-45-9", e: "E143", cat: "colorant",
    aliases: [["坚牢绿", "zh"], ["أخضر سريع", "ar"], ["vert solide FCF", "fr"], ["Brillantsäuregrün", "de"]] },

  // Sweeteners
  { name: "Aspartame", cas: "22839-47-0", e: "E951", cat: "sweetener",
    aliases: [["阿斯巴甜", "zh"], ["أسبارتام", "ar"], ["aspartame", "fr"], ["Aspartam", "de"]] },
  { name: "Sucralose", cas: "56038-13-2", e: "E955", cat: "sweetener",
    aliases: [["三氯蔗糖", "zh"], ["سوكرالوز", "ar"], ["sucralose", "fr"], ["Sucralose", "de"]] },
  { name: "Acesulfame Potassium", cas: "55589-62-3", e: "E950", cat: "sweetener",
    aliases: [["安赛蜜", "zh"], ["أسيسولفام البوتاسيوم", "ar"], ["acésulfame de potassium", "fr"], ["Acesulfam-K", "de"]] },
  { name: "Saccharin", cas: "81-07-2", e: "E954", cat: "sweetener",
    aliases: [["糖精", "zh"], ["سكارين", "ar"], ["saccharine", "fr"], ["Saccharin", "de"]] },
  { name: "Cyclamate", cas: "139-05-9", e: "E952", cat: "sweetener",
    aliases: [["甜蜜素", "zh"], ["سيكلامات", "ar"], ["cyclamate", "fr"], ["Cyclamat", "de"]] },
  { name: "Neotame", cas: "165450-17-9", e: "E961", cat: "sweetener",
    aliases: [["纽甜", "zh"], ["نيوتام", "ar"], ["néotame", "fr"], ["Neotam", "de"]] },
  { name: "Steviol Glycosides", cas: "57817-89-7", e: "E960", cat: "sweetener",
    aliases: [["甜菊糖苷", "zh"], ["غليكوسيدات ستيفيول", "ar"], ["glycosides de stéviol", "fr"], ["Steviolglycoside", "de"]] },
  { name: "Xylitol", cas: "87-99-0", e: "E967", cat: "sweetener",
    aliases: [["木糖醇", "zh"], ["إكسيليتول", "ar"], ["xylitol", "fr"], ["Xylit", "de"]] },
  { name: "Sorbitol", cas: "50-70-4", e: "E420", cat: "sweetener",
    aliases: [["山梨糖醇", "zh"], ["سوربيتول", "ar"], ["sorbitol", "fr"], ["Sorbit", "de"]] },
  { name: "Erythritol", cas: "149-32-6", e: "E968", cat: "sweetener",
    aliases: [["赤藓糖醇", "zh"], ["إريثريتول", "ar"], ["érythritol", "fr"], ["Erythrit", "de"]] },
  { name: "High Fructose Corn Syrup", cas: null, e: null, cat: "sweetener",
    aliases: [["高果糖玉米糖浆", "zh"], ["شراب الذرة عالي الفركتوز", "ar"], ["sirop de maïs à haute teneur en fructose", "fr"], ["Maissirup mit hohem Fructosegehalt", "de"]] },

  // Antioxidants
  { name: "Butylated Hydroxyanisole", cas: "25013-16-5", e: "E320", cat: "antioxidant",
    aliases: [["丁基羟基茴香醚", "zh"], ["بوتيل هيدروكسي أنيسول", "ar"], ["hydroxyanisole butylé", "fr"], ["Butylhydroxyanisol", "de"]] },
  { name: "Butylated Hydroxytoluene", cas: "128-37-0", e: "E321", cat: "antioxidant",
    aliases: [["二丁基羟基甲苯", "zh"], ["بوتيل هيدروكسي تولوين", "ar"], ["hydroxytoluène butylé", "fr"], ["Butylhydroxytoluol", "de"]] },
  { name: "Propyl Gallate", cas: "121-79-9", e: "E310", cat: "antioxidant",
    aliases: [["没食子酸丙酯", "zh"], ["بروبيل غالات", "ar"], ["gallate de propyle", "fr"], ["Propylgallat", "de"]] },
  { name: "Tertiary Butylhydroquinone", cas: "1948-33-0", e: "E319", cat: "antioxidant",
    aliases: [["特丁基对苯二酚", "zh"], ["بوتيل هيدروكينون ثالثي", "ar"], ["butylhydroquinone tertiaire", "fr"], ["Tertiärbutylhydrochinon", "de"]] },
  { name: "Ascorbic Acid", cas: "50-81-7", e: "E300", cat: "antioxidant",
    aliases: [["抗坏血酸", "zh"], ["حمض الأسكوربيك", "ar"], ["acide ascorbique", "fr"], ["Ascorbinsäure", "de"]] },
  { name: "Tocopherols", cas: "59-02-9", e: "E306", cat: "antioxidant",
    aliases: [["生育酚", "zh"], ["توكوفيرول", "ar"], ["tocophérols", "fr"], ["Tocopherole", "de"]] },
  { name: "Citric Acid", cas: "77-92-9", e: "E330", cat: "antioxidant",
    aliases: [["柠檬酸", "zh"], ["حمض الستريك", "ar"], ["acide citrique", "fr"], ["Citronensäure", "de"]] },
  { name: "Sodium Erythorbate", cas: "6381-77-7", e: "E316", cat: "antioxidant",
    aliases: [["异抗坏血酸钠", "zh"], ["إريثوربات الصوديوم", "ar"], ["érythorbate de sodium", "fr"], ["Natriumisoascorbat", "de"]] },

  // Emulsifiers
  { name: "Lecithin", cas: "8002-43-5", e: "E322", cat: "emulsifier",
    aliases: [["卵磷脂", "zh"], ["ليسيثين", "ar"], ["lécithine", "fr"], ["Lecithin", "de"]] },
  { name: "Mono- and Diglycerides", cas: "67254-73-3", e: "E471", cat: "emulsifier",
    aliases: [["单甘酯和双甘酯", "zh"], ["أحادي وثنائي الغليسريد", "ar"], ["mono- et diglycérides", "fr"], ["Mono- und Diglyceride", "de"]] },
  { name: "Polysorbate 80", cas: "9005-65-6", e: "E433", cat: "emulsifier",
    aliases: [["聚山梨酯80", "zh"], ["بوليسوربات 80", "ar"], ["polysorbate 80", "fr"], ["Polysorbat 80", "de"]] },
  { name: "Polysorbate 60", cas: "9005-67-8", e: "E435", cat: "emulsifier",
    aliases: [["聚山梨酯60", "zh"], ["بوليسوربات 60", "ar"], ["polysorbate 60", "fr"], ["Polysorbat 60", "de"]] },
  { name: "Carrageenan", cas: "9000-07-1", e: "E407", cat: "emulsifier",
    aliases: [["卡拉胶", "zh"], ["كاراجينان", "ar"], ["carraghénane", "fr"], ["Carrageen", "de"]] },
  { name: "Sodium Stearoyl Lactylate", cas: "25383-99-7", e: "E481", cat: "emulsifier",
    aliases: [["硬脂酰乳酸钠", "zh"], ["ستيارويل لاكتيلات الصوديوم", "ar"], ["stéaroyl-2-lactylate de sodium", "fr"], ["Natriumstearoyllactylat", "de"]] },
  { name: "Sorbitan Monostearate", cas: "1338-41-6", e: "E491", cat: "emulsifier",
    aliases: [["司盘60", "zh"], ["سوربيتان أحادي الستيارات", "ar"], ["monostéarate de sorbitane", "fr"], ["Sorbitanmonostearat", "de"]] },
  { name: "Cellulose Gum", cas: "9004-32-4", e: "E466", cat: "emulsifier",
    aliases: [["羧甲基纤维素钠", "zh"], ["صمغ السليلوز", "ar"], ["gomme de cellulose", "fr"], ["Carboxymethylcellulose", "de"]] },
  { name: "Xanthan Gum", cas: "11138-66-2", e: "E415", cat: "emulsifier",
    aliases: [["黄原胶", "zh"], ["صمغ الزانثان", "ar"], ["gomme xanthane", "fr"], ["Xanthan", "de"]] },
  { name: "Guar Gum", cas: "9000-30-0", e: "E412", cat: "emulsifier",
    aliases: [["瓜尔胶", "zh"], ["صمغ الغوار", "ar"], ["gomme de guar", "fr"], ["Guarkernmehl", "de"]] },

  // Flavor enhancers
  { name: "Monosodium Glutamate", cas: "142-47-2", e: "E621", cat: "flavor enhancer",
    aliases: [["谷氨酸钠", "zh"], ["غلوتامات أحادية الصوديوم", "ar"], ["glutamate monosodique", "fr"], ["Mononatriumglutamat", "de"]] },
  { name: "Disodium Guanylate", cas: "5550-12-9", e: "E627", cat: "flavor enhancer",
    aliases: [["鸟苷酸二钠", "zh"], ["غوانيلات ثنائي الصوديوم", "ar"], ["guanylate disodique", "fr"], ["Dinatriumguanylat", "de"]] },
  { name: "Disodium Inosinate", cas: "4691-65-0", e: "E631", cat: "flavor enhancer",
    aliases: [["肌苷酸二钠", "zh"], ["إينوسينات ثنائي الصوديوم", "ar"], ["inosinate disodique", "fr"], ["Dinatriuminosinat", "de"]] },
  { name: "Maltodextrin", cas: "9050-36-6", e: null, cat: "flavor enhancer",
    aliases: [["麦芽糊精", "zh"], ["مالتوديكسترين", "ar"], ["maltodextrine", "fr"], ["Maltodextrin", "de"]] },
  { name: "Hydrolyzed Vegetable Protein", cas: null, e: null, cat: "flavor enhancer",
    aliases: [["水解植物蛋白", "zh"], ["بروتين نباتي محلل", "ar"], ["protéine végétale hydrolysée", "fr"], ["hydrolysiertes Pflanzenprotein", "de"]] },
  { name: "Yeast Extract", cas: null, e: null, cat: "flavor enhancer",
    aliases: [["酵母提取物", "zh"], ["خلاصة الخميرة", "ar"], ["extrait de levure", "fr"], ["Hefeextrakt", "de"]] },

  // Acidity regulators
  { name: "Phosphoric Acid", cas: "7664-38-2", e: "E338", cat: "acidity regulator",
    aliases: [["磷酸", "zh"], ["حمض الفوسفوريك", "ar"], ["acide phosphorique", "fr"], ["Phosphorsäure", "de"]] },
  { name: "Sodium Phosphate", cas: "7558-80-7", e: "E339", cat: "acidity regulator",
    aliases: [["磷酸钠", "zh"], ["فوسفات الصوديوم", "ar"], ["phosphate de sodium", "fr"], ["Natriumphosphat", "de"]] },
  { name: "Calcium Chloride", cas: "10043-52-4", e: "E509", cat: "acidity regulator",
    aliases: [["氯化钙", "zh"], ["كلوريد الكالسيوم", "ar"], ["chlorure de calcium", "fr"], ["Calciumchlorid", "de"]] },
  { name: "Sodium Citrate", cas: "68-04-2", e: "E331", cat: "acidity regulator",
    aliases: [["柠檬酸钠", "zh"], ["سيترات الصوديوم", "ar"], ["citrate de sodium", "fr"], ["Natriumcitrat", "de"]] },
  { name: "Lactic Acid", cas: "50-21-5", e: "E270", cat: "acidity regulator",
    aliases: [["乳酸", "zh"], ["حمض اللاكتيك", "ar"], ["acide lactique", "fr"], ["Milchsäure", "de"]] },
  { name: "Malic Acid", cas: "6915-15-7", e: "E296", cat: "acidity regulator",
    aliases: [["苹果酸", "zh"], ["حمض الماليك", "ar"], ["acide malique", "fr"], ["Äpfelsäure", "de"]] },
  { name: "Tartaric Acid", cas: "87-69-4", e: "E334", cat: "acidity regulator",
    aliases: [["酒石酸", "zh"], ["حمض الطرطريك", "ar"], ["acide tartrique", "fr"], ["Weinsäure", "de"]] },
  { name: "Fumaric Acid", cas: "110-17-8", e: "E297", cat: "acidity regulator",
    aliases: [["富马酸", "zh"], ["حمض الفوماريك", "ar"], ["acide fumarique", "fr"], ["Fumarsäure", "de"]] },

  // Thickeners
  { name: "Pectin", cas: "9000-69-5", e: "E440", cat: "thickener",
    aliases: [["果胶", "zh"], ["بكتين", "ar"], ["pectine", "fr"], ["Pektin", "de"]] },
  { name: "Gelatin", cas: "9000-70-8", e: "E441", cat: "thickener",
    aliases: [["明胶", "zh"], ["جيلاتين", "ar"], ["gélatine", "fr"], ["Gelatine", "de"]] },
  { name: "Agar", cas: "9002-18-0", e: "E406", cat: "thickener",
    aliases: [["琼脂", "zh"], ["أجار", "ar"], ["agar-agar", "fr"], ["Agar-Agar", "de"]] },
  { name: "Modified Starch", cas: null, e: "E1404", cat: "thickener",
    aliases: [["改性淀粉", "zh"], ["نشا معدل", "ar"], ["amidon modifié", "fr"], ["modifizierte Stärke", "de"]] },
  { name: "Methylcellulose", cas: "9004-67-5", e: "E461", cat: "thickener",
    aliases: [["甲基纤维素", "zh"], ["ميثيل سيليلوز", "ar"], ["méthylcellulose", "fr"], ["Methylcellulose", "de"]] },
  { name: "Locust Bean Gum", cas: "9000-40-2", e: "E410", cat: "thickener",
    aliases: [["刺槐豆胶", "zh"], ["صمغ الخروب", "ar"], ["gomme de caroube", "fr"], ["Johannisbrotkernmehl", "de"]] },
  { name: "Gellan Gum", cas: "71010-52-1", e: "E418", cat: "thickener",
    aliases: [["结冷胶", "zh"], ["صمغ الجيلان", "ar"], ["gomme gellane", "fr"], ["Gellan", "de"]] },

  // Leavening / anti-caking
  { name: "Potassium Bromate", cas: "7758-01-2", e: null, cat: "flour treatment",
    aliases: [["溴酸钾", "zh"], ["برومات البوتاسيوم", "ar"], ["bromate de potassium", "fr"], ["Kaliumbromat", "de"]] },
  { name: "Azodicarbonamide", cas: "123-77-3", e: "E927a", cat: "flour treatment",
    aliases: [["偶氮二甲酰胺", "zh"], ["أزوديكاربوناميد", "ar"], ["azodicarbonamide", "fr"], ["Azodicarbonamid", "de"]] },
  { name: "Silicon Dioxide", cas: "7631-86-9", e: "E551", cat: "anti-caking",
    aliases: [["二氧化硅", "zh"], ["ثاني أكسيد السيليكون", "ar"], ["dioxyde de silicium", "fr"], ["Siliciumdioxid", "de"]] },
  { name: "Calcium Silicate", cas: "1344-95-2", e: "E552", cat: "anti-caking",
    aliases: [["硅酸钙", "zh"], ["سيليكات الكالسيوم", "ar"], ["silicate de calcium", "fr"], ["Calciumsilikat", "de"]] },
  { name: "Sodium Aluminum Phosphate", cas: "7785-88-8", e: "E541", cat: "leavening",
    aliases: [["磷酸铝钠", "zh"], ["فوسفات ألومنيوم الصوديوم", "ar"], ["phosphate d'aluminium et de sodium", "fr"], ["Natriumaluminiumphosphat", "de"]] },
  { name: "Sodium Bicarbonate", cas: "144-55-8", e: "E500", cat: "leavening",
    aliases: [["碳酸氢钠", "zh"], ["بيكربونات الصوديوم", "ar"], ["bicarbonate de sodium", "fr"], ["Natriumhydrogencarbonat", "de"]] },

  // Humectants
  { name: "Propylene Glycol", cas: "57-55-6", e: "E1520", cat: "humectant",
    aliases: [["丙二醇", "zh"], ["بروبيلين غليكول", "ar"], ["propylène glycol", "fr"], ["Propylenglykol", "de"]] },
  { name: "Glycerol", cas: "56-81-5", e: "E422", cat: "humectant",
    aliases: [["甘油", "zh"], ["غليسيرول", "ar"], ["glycérol", "fr"], ["Glycerin", "de"]] },

  // Controversial / widely discussed
  { name: "Potassium Aluminum Sulfate", cas: "7784-24-9", e: "E522", cat: "firming agent",
    aliases: [["硫酸铝钾", "zh"], ["كبريتات ألومنيوم البوتاسيوم", "ar"], ["sulfate d'aluminium et de potassium", "fr"], ["Kaliumaluminiumsulfat", "de"]] },
  { name: "Sodium Carboxymethyl Cellulose", cas: "9004-32-4", e: "E466", cat: "thickener",
    aliases: [["羧甲基纤维素钠", "zh"], ["كربوكسي ميثيل سيليلوز الصوديوم", "ar"], ["carboxyméthylcellulose de sodium", "fr"], ["Natriumcarboxymethylcellulose", "de"]] },
  { name: "Dimethyl Polysiloxane", cas: "63148-62-9", e: "E900", cat: "anti-foaming",
    aliases: [["二甲基聚硅氧烷", "zh"], ["ثنائي ميثيل بولي سيلوكسان", "ar"], ["diméthylpolysiloxane", "fr"], ["Dimethylpolysiloxan", "de"]] },
  { name: "Calcium Disodium EDTA", cas: "62-33-9", e: "E385", cat: "sequestrant",
    aliases: [["乙二胺四乙酸二钠钙", "zh"], ["كالسيوم ثنائي الصوديوم EDTA", "ar"], ["EDTA calcio-disodique", "fr"], ["Calciumdinatrium-EDTA", "de"]] },
  { name: "Brominated Vegetable Oil", cas: "8016-94-2", e: null, cat: "emulsifier",
    aliases: [["溴化植物油", "zh"], ["زيت نباتي مبروم", "ar"], ["huile végétale bromée", "fr"], ["bromiertes Pflanzenöl", "de"]] },
  { name: "Potassium Benzoate", cas: "582-25-2", e: "E212", cat: "preservative",
    aliases: [["苯甲酸钾", "zh"], ["بنزوات البوتاسيوم", "ar"], ["benzoate de potassium", "fr"], ["Kaliumbenzoat", "de"]] },
  { name: "Sodium Lauryl Sulfate", cas: "151-21-3", e: null, cat: "emulsifier",
    aliases: [["十二烷基硫酸钠", "zh"], ["لوريل كبريتات الصوديوم", "ar"], ["laurylsulfate de sodium", "fr"], ["Natriumlaurylsulfat", "de"]] },
  { name: "Propylparaben", cas: "94-13-3", e: "E216", cat: "preservative",
    aliases: [["对羟基苯甲酸丙酯", "zh"], ["بروبيل بارابين", "ar"], ["propylparabène", "fr"], ["Propylparaben", "de"]] },
  { name: "Methylparaben", cas: "99-76-3", e: "E218", cat: "preservative",
    aliases: [["对羟基苯甲酸甲酯", "zh"], ["ميثيل بارابين", "ar"], ["méthylparabène", "fr"], ["Methylparaben", "de"]] },

  // Misc
  { name: "Annatto", cas: "1393-63-1", e: "E160b", cat: "colorant",
    aliases: [["胭脂树橙", "zh"], ["أناتو", "ar"], ["annatto", "fr"], ["Annatto", "de"]] },
  { name: "Paprika Oleoresin", cas: "84625-29-6", e: "E160c", cat: "colorant",
    aliases: [["辣椒红", "zh"], ["راتنج زيتي البابريكا", "ar"], ["oléorésine de paprika", "fr"], ["Paprikaextrakt", "de"]] },
  { name: "Beta-Carotene", cas: "7235-40-7", e: "E160a", cat: "colorant",
    aliases: [["β-胡萝卜素", "zh"], ["بيتا كاروتين", "ar"], ["bêta-carotène", "fr"], ["Beta-Carotin", "de"]] },
  { name: "Riboflavin", cas: "83-88-5", e: "E101", cat: "colorant",
    aliases: [["核黄素", "zh"], ["ريبوفلافين", "ar"], ["riboflavine", "fr"], ["Riboflavin", "de"]] },
  { name: "Chlorophyll", cas: "479-61-8", e: "E140", cat: "colorant",
    aliases: [["叶绿素", "zh"], ["كلوروفيل", "ar"], ["chlorophylle", "fr"], ["Chlorophyll", "de"]] },
];

async function main() {
  let added = 0;
  let skipped = 0;

  for (const item of SEED_DATA) {
    const slug = slugify(item.name);
    const existing = await prisma.ingredient.findUnique({ where: { slug } });
    if (existing) {
      skipped++;
      continue;
    }

    await prisma.ingredient.create({
      data: {
        canonicalName: item.name,
        slug,
        casNumber: item.cas,
        eNumber: item.e,
        category: item.cat,
        overallRiskLevel: "insufficient",
        evidenceCount: 0,
        aliases: {
          create: [
            { aliasName: item.name, language: "en", isPrimary: true },
            ...item.aliases.map(([aliasName, language]) => ({
              aliasName,
              language,
              isPrimary: false,
            })),
          ],
        },
      },
    });
    added++;
  }

  console.log(`Seeded ${added} ingredients (${skipped} already existed)`);
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(() => prisma.$disconnect());
