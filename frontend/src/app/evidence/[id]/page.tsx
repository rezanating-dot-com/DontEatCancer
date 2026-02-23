"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { getEvidenceById } from "@/lib/api";
import type { EvidenceDetail } from "@/lib/types";
import RiskBadge from "@/components/RiskBadge";

const DIRECTION_LABELS: Record<string, { text: string; color: string }> = {
  increases: { text: "Increases risk", color: "text-red-700 bg-red-50 border-red-200" },
  decreases: { text: "Protective (decreases risk)", color: "text-green-700 bg-green-50 border-green-200" },
  neutral: { text: "Neutral", color: "text-gray-700 bg-gray-50 border-gray-200" },
  inconclusive: { text: "Inconclusive", color: "text-amber-700 bg-amber-50 border-amber-200" },
};

export default function EvidenceDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();
  const [evidence, setEvidence] = useState<EvidenceDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getEvidenceById(Number(id))
      .then(setEvidence)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <p className="text-gray-400">Loading...</p>;
  if (!evidence) return <p className="text-gray-500">Evidence not found.</p>;

  const hasCOI = !!evidence.conflict_of_interest;
  const direction = evidence.risk_direction ? DIRECTION_LABELS[evidence.risk_direction] : null;

  return (
    <div className="max-w-4xl">
      <button onClick={() => router.back()} className="text-sm text-blue-600 hover:underline mb-4">
        &larr; Back
      </button>

      {hasCOI && (
        <div className="mb-6 px-4 py-3 bg-red-100 border-2 border-red-300 rounded-lg">
          <p className="text-red-800 font-semibold flex items-center gap-2">
            <span className="text-lg">&#9888;</span>
            Conflict of Interest Detected
          </p>
          <p className="mt-2 text-sm text-red-700">{evidence.conflict_of_interest}</p>
        </div>
      )}

      <h1 className="text-2xl font-bold text-gray-900 leading-tight">{evidence.title}</h1>

      {evidence.authors && evidence.authors.length > 0 && (
        <p className="mt-2 text-sm text-gray-500">{evidence.authors.join(", ")}</p>
      )}

      <div className="mt-3 flex flex-wrap items-center gap-3">
        <RiskBadge level={evidence.risk_level} />
        {direction && (
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${direction.color}`}>
            {direction.text}
          </span>
        )}
        {evidence.study_type && (
          <span className="px-2.5 py-0.5 bg-gray-100 text-gray-600 rounded-full text-xs font-medium border border-gray-200">
            {evidence.study_type}
          </span>
        )}
        {evidence.confidence_score !== null && (
          <span className="text-xs text-gray-400">
            {(evidence.confidence_score * 100).toFixed(0)}% confidence
          </span>
        )}
        {evidence.needs_review && (
          <span className="px-2.5 py-0.5 bg-amber-50 text-amber-600 rounded-full text-xs font-medium border border-amber-200">
            Needs review
          </span>
        )}
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-4 text-sm text-gray-500">
        {evidence.journal && <span>{evidence.journal}</span>}
        {evidence.publication_year && <span>{evidence.publication_year}</span>}
        {evidence.original_language && evidence.original_language !== "en" && (
          <span>Original language: {evidence.original_language.toUpperCase()}</span>
        )}
        {evidence.source_database && <span>Source: {evidence.source_database}</span>}
        {evidence.doi && (
          <a
            href={`https://doi.org/${evidence.doi}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:underline"
          >
            DOI: {evidence.doi}
          </a>
        )}
      </div>

      {evidence.ingredients && evidence.ingredients.length > 0 && (
        <div className="mt-6">
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">Linked Ingredients</h2>
          <div className="flex flex-wrap gap-2">
            {evidence.ingredients.map((ing) => (
              <Link
                key={ing.slug}
                href={`/ingredients/${ing.slug}`}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 text-blue-700 border border-blue-200 rounded-full text-sm hover:bg-blue-100"
              >
                {ing.name}
                <span className="text-blue-400 text-xs">({ing.relevance})</span>
              </Link>
            ))}
          </div>
        </div>
      )}

      {evidence.findings_summary && (
        <div className="mt-6">
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">Findings Summary</h2>
          <p className="text-gray-700 leading-relaxed">{evidence.findings_summary}</p>
        </div>
      )}

      {evidence.abstract_english && (
        <div className="mt-6">
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">Abstract</h2>
          <p className="text-gray-700 leading-relaxed text-sm">{evidence.abstract_english}</p>
        </div>
      )}
    </div>
  );
}
