"use client";

import Link from "next/link";

import type { Evidence } from "@/lib/types";

import RiskBadge from "./RiskBadge";

export default function EvidenceCard({
  evidence,
  relevance,
}: {
  evidence: Evidence;
  relevance?: string;
}) {
  const hasCOI = !!evidence.conflict_of_interest;

  return (
    <Link
      href={`/evidence/${evidence.id}`}
      className={`block p-4 rounded-lg transition-colors ${
        hasCOI
          ? "border-2 border-red-300 bg-red-50/30 hover:border-red-400"
          : "border border-gray-200 hover:border-gray-300"
      }`}
    >
      {hasCOI && (
        <div className="mb-3 px-3 py-2 bg-red-100 border border-red-200 rounded text-sm text-red-800 font-medium flex items-center gap-2">
          <span className="text-red-600 text-base">&#9888;</span>
          Conflict of Interest — authors have industry ties
        </div>
      )}

      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <h4 className="font-medium text-gray-900 line-clamp-2">{evidence.title}</h4>
          <div className="mt-1 flex flex-wrap items-center gap-2 text-sm text-gray-500">
            {evidence.journal && <span>{evidence.journal}</span>}
            {evidence.publication_year && <span>({evidence.publication_year})</span>}
            {evidence.study_type && (
              <span className="px-1.5 py-0.5 bg-gray-100 rounded text-xs">{evidence.study_type}</span>
            )}
            {relevance && relevance !== "primary" && (
              <span className="px-1.5 py-0.5 bg-purple-50 text-purple-600 rounded text-xs">{relevance}</span>
            )}
          </div>
          {evidence.authors && evidence.authors.length > 0 && (
            <p className="mt-1 text-xs text-gray-400 truncate">
              {evidence.authors.slice(0, 3).join(", ")}
              {evidence.authors.length > 3 && " et al."}
            </p>
          )}
        </div>
        <div className="flex flex-col items-end gap-1 shrink-0">
          <RiskBadge level={evidence.risk_level} />
          {evidence.confidence_score !== null && (
            <span className="text-xs text-gray-400">
              {(evidence.confidence_score * 100).toFixed(0)}% conf.
            </span>
          )}
        </div>
      </div>

      {evidence.findings_summary && (
        <p className="mt-3 text-sm text-gray-600 line-clamp-2">{evidence.findings_summary}</p>
      )}

      <div className="mt-2 flex items-center gap-3 text-xs text-gray-400">
        {evidence.original_language && evidence.original_language !== "en" && (
          <span>Original: {evidence.original_language.toUpperCase()}</span>
        )}
        {evidence.needs_review && (
          <span className="px-1.5 py-0.5 bg-amber-50 text-amber-600 rounded">Needs review</span>
        )}
      </div>
    </Link>
  );
}
