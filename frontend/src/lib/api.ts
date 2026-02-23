const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

async function fetchAPI<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

import type {
  Evidence,
  EvidenceDetail,
  IngredientDetail,
  IngredientSummary,
  ProcessingJob,
  QueryResult,
  SearchResults,
  Stats,
} from "./types";

// Stats
export const getStats = () => fetchAPI<Stats>("/api/v1/stats");

// Ingredients
export const getIngredients = (params?: {
  category?: string;
  risk_level?: string;
  letter?: string;
  skip?: number;
  limit?: number;
}) => {
  const sp = new URLSearchParams();
  if (params?.category) sp.set("category", params.category);
  if (params?.risk_level) sp.set("risk_level", params.risk_level);
  if (params?.letter) sp.set("letter", params.letter);
  if (params?.skip) sp.set("skip", String(params.skip));
  if (params?.limit) sp.set("limit", String(params.limit));
  const qs = sp.toString();
  return fetchAPI<IngredientSummary[]>(`/api/v1/ingredients${qs ? `?${qs}` : ""}`);
};

export const getIngredient = (slug: string) =>
  fetchAPI<IngredientDetail>(`/api/v1/ingredients/${slug}`);

export const getIngredientEvidence = (slug: string) =>
  fetchAPI<{ evidence: Evidence; relevance: string }[]>(
    `/api/v1/ingredients/${slug}/evidence`
  );

export const getCategories = () =>
  fetchAPI<string[]>("/api/v1/ingredients/categories");

// Evidence
export const getEvidence = (params?: {
  risk_level?: string;
  study_type?: string;
  year_min?: number;
  year_max?: number;
  skip?: number;
  limit?: number;
}) => {
  const sp = new URLSearchParams();
  if (params?.risk_level) sp.set("risk_level", params.risk_level);
  if (params?.study_type) sp.set("study_type", params.study_type);
  if (params?.year_min) sp.set("year_min", String(params.year_min));
  if (params?.year_max) sp.set("year_max", String(params.year_max));
  if (params?.skip) sp.set("skip", String(params.skip));
  if (params?.limit) sp.set("limit", String(params.limit));
  const qs = sp.toString();
  return fetchAPI<Evidence[]>(`/api/v1/evidence${qs ? `?${qs}` : ""}`);
};

export const getEvidenceById = (id: number) =>
  fetchAPI<EvidenceDetail>(`/api/v1/evidence/${id}`);

export const getReviewQueue = () =>
  fetchAPI<Evidence[]>("/api/v1/evidence/review-queue");

export const submitReview = (id: number, review: Partial<Evidence>) =>
  fetchAPI<Evidence>(`/api/v1/evidence/${id}/review`, {
    method: "PATCH",
    body: JSON.stringify(review),
  });

// Search
export const search = (q: string) =>
  fetchAPI<SearchResults>(`/api/v1/search?q=${encodeURIComponent(q)}`);

// Query generator
export const generateQueries = (ingredient: string, database: string) =>
  fetchAPI<QueryResult>(
    `/api/v1/queries/generate?ingredient=${encodeURIComponent(ingredient)}&database=${encodeURIComponent(database)}`,
    { method: "POST" }
  );

// Upload
export const uploadText = (text: string) =>
  fetchAPI<ProcessingJob>("/api/v1/upload/text", {
    method: "POST",
    body: JSON.stringify({ text }),
  });

export const uploadRIS = async (file: File): Promise<ProcessingJob> => {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/api/v1/upload/ris`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
  return res.json();
};

// Processing jobs
export const getJobs = () =>
  fetchAPI<ProcessingJob[]>("/api/v1/processing/jobs");

export const getJob = (id: number) =>
  fetchAPI<ProcessingJob>(`/api/v1/processing/jobs/${id}`);

export const startJob = (id: number) =>
  fetchAPI<ProcessingJob>(`/api/v1/processing/jobs/${id}/start`, {
    method: "POST",
  });
