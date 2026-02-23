import type {
  Ingredient,
  IngredientAlias,
  Evidence,
  ProcessingJob,
} from "@/generated/prisma/client";

// Map Prisma Ingredient → frontend IngredientSummary (snake_case)
export function mapIngredientSummary(i: Ingredient) {
  return {
    id: i.id,
    canonical_name: i.canonicalName,
    slug: i.slug,
    cas_number: i.casNumber,
    e_number: i.eNumber,
    category: i.category,
    overall_risk_level: i.overallRiskLevel,
    evidence_count: i.evidenceCount,
  };
}

// Map Prisma Ingredient + aliases → frontend IngredientDetail (snake_case)
export function mapIngredientDetail(
  i: Ingredient & { aliases: IngredientAlias[] }
) {
  return {
    ...mapIngredientSummary(i),
    description: i.description,
    aliases: i.aliases.map((a) => ({
      id: a.id,
      alias_name: a.aliasName,
      language: a.language,
      is_primary: a.isPrimary,
    })),
  };
}

// Map Prisma Evidence → frontend Evidence (snake_case)
export function mapEvidenceOut(e: Evidence) {
  return {
    id: e.id,
    title: e.title,
    abstract_english: e.abstractEnglish,
    authors: e.authors,
    doi: e.doi,
    journal: e.journal,
    publication_year: e.publicationYear,
    original_language: e.originalLanguage,
    source_database: e.sourceDatabase,
    study_type: e.studyType,
    findings_summary: e.findingsSummary,
    risk_level: e.riskLevel,
    risk_direction: e.riskDirection,
    confidence_score: e.confidenceScore,
    conflict_of_interest: e.conflictOfInterest,
    url: e.url,
    plain_language_summary: e.plainLanguageSummary,
    needs_review: e.needsReview,
    processing_status: e.processingStatus,
    created_at: e.createdAt.toISOString(),
  };
}

// Map Prisma Evidence → frontend EvidenceDetail (with full_text)
export function mapEvidenceDetail(e: Evidence) {
  return {
    ...mapEvidenceOut(e),
    full_text: e.fullText,
  };
}

// Map Prisma ProcessingJob → frontend ProcessingJob (snake_case)
export function mapProcessingJob(j: ProcessingJob) {
  return {
    id: j.id,
    filename: j.filename,
    status: j.status,
    total_records: j.totalRecords,
    processed_count: j.processedCount,
    failed_count: j.failedCount,
    flagged_count: j.flaggedCount,
    result_ingredients: j.resultIngredients,
    created_at: j.createdAt.toISOString(),
    completed_at: j.completedAt?.toISOString() ?? null,
  };
}
