"use client";

import { use, useEffect, useState } from "react";

import EvidenceCard from "@/components/EvidenceCard";
import RiskBadge from "@/components/RiskBadge";
import { getIngredient, getIngredientEvidence } from "@/lib/api";
import type { Evidence, IngredientDetail } from "@/lib/types";

export default function IngredientDetailPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = use(params);
  const [ingredient, setIngredient] = useState<IngredientDetail | null>(null);
  const [evidence, setEvidence] = useState<{ evidence: Evidence; relevance: string }[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getIngredient(slug),
      getIngredientEvidence(slug),
    ])
      .then(([ing, ev]) => {
        setIngredient(ing);
        setEvidence(ev);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [slug]);

  if (loading) return <p className="text-gray-400">Loading...</p>;
  if (!ingredient) return <p className="text-gray-500">Ingredient not found.</p>;

  const LANG_NAMES: Record<string, string> = {
    zh: "Chinese", ar: "Arabic", fr: "French", de: "German", en: "English",
    es: "Spanish", ja: "Japanese", ko: "Korean",
  };

  return (
    <div>
      <div className="mb-6 sm:mb-8">
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3 sm:gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">{ingredient.canonical_name}</h1>
            <div className="mt-2 flex flex-wrap items-center gap-2 sm:gap-3 text-sm text-gray-500">
              {ingredient.e_number && <span className="px-2 py-0.5 bg-gray-100 rounded">{ingredient.e_number}</span>}
              {ingredient.cas_number && <span>CAS: {ingredient.cas_number}</span>}
              {ingredient.category && <span className="capitalize">{ingredient.category}</span>}
            </div>
          </div>
          <RiskBadge level={ingredient.overall_risk_level} />
        </div>

        {ingredient.description && (
          <p className="mt-4 text-gray-600">{ingredient.description}</p>
        )}

        {ingredient.aliases.length > 0 && (
          <div className="mt-4">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Names in other languages</h3>
            <div className="flex flex-wrap gap-2">
              {ingredient.aliases.map((a) => (
                <span
                  key={a.id}
                  className="px-2 py-1 bg-gray-50 border border-gray-200 rounded text-sm"
                >
                  <span className="text-gray-400 mr-1">{LANG_NAMES[a.language] || a.language}:</span>
                  {a.alias_name}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        Evidence ({evidence.length} papers)
      </h2>
      {evidence.length === 0 ? (
        <p className="text-gray-400">No evidence linked yet.</p>
      ) : (
        <div className="flex flex-col gap-3">
          {evidence.map((item) => (
            <EvidenceCard
              key={item.evidence.id}
              evidence={item.evidence}
              relevance={item.relevance}
            />
          ))}
        </div>
      )}
    </div>
  );
}
