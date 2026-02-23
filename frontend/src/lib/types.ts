export interface IngredientSummary {
  id: number;
  canonical_name: string;
  slug: string;
  cas_number: string | null;
  e_number: string | null;
  category: string | null;
  overall_risk_level: string | null;
  evidence_count: number;
}

export interface Alias {
  id: number;
  alias_name: string;
  language: string;
  is_primary: boolean;
}

export interface IngredientDetail extends IngredientSummary {
  description: string | null;
  aliases: Alias[];
}

export interface Evidence {
  id: number;
  title: string;
  abstract_english: string | null;
  authors: string[] | null;
  doi: string | null;
  journal: string | null;
  publication_year: number | null;
  original_language: string | null;
  source_database: string | null;
  study_type: string | null;
  findings_summary: string | null;
  risk_level: string | null;
  risk_direction: string | null;
  confidence_score: number | null;
  conflict_of_interest: string | null;
  url: string | null;
  plain_language_summary: string | null;
  needs_review: boolean;
  processing_status: string;
  created_at: string;
}

export interface EvidenceDetail extends Evidence {
  full_text: string | null;
  ingredients: { name: string; slug: string; relevance: string }[];
}

export interface ResultIngredient {
  name: string;
  slug: string;
}

export interface ProcessingJob {
  id: number;
  filename: string;
  status: string;
  total_records: number;
  processed_count: number;
  failed_count: number;
  flagged_count: number;
  result_ingredients: ResultIngredient[] | null;
  created_at: string;
  completed_at: string | null;
}

export interface SearchResults {
  ingredients: IngredientSummary[];
  evidence: Evidence[];
}

export interface Stats {
  ingredient_count: number;
  evidence_count: number;
  review_count: number;
}

export interface QueryResult {
  ingredient: string;
  database: string;
  queries: Record<string, string>;
}

export type RiskLevel = "safe" | "low" | "moderate" | "high" | "insufficient";
