"use client";

import Link from "next/link";

import type { IngredientSummary } from "@/lib/types";

import RiskBadge from "./RiskBadge";

export default function IngredientCard({ ingredient }: { ingredient: IngredientSummary }) {
  return (
    <Link
      href={`/ingredients/${ingredient.slug}`}
      className="block p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-sm transition-all"
    >
      <div className="flex items-start justify-between gap-2">
        <div>
          <h3 className="font-semibold text-gray-900">{ingredient.canonical_name}</h3>
          <div className="mt-1 flex items-center gap-2 text-sm text-gray-500">
            {ingredient.e_number && <span>{ingredient.e_number}</span>}
            {ingredient.cas_number && <span>CAS: {ingredient.cas_number}</span>}
          </div>
          {ingredient.category && (
            <span className="mt-2 inline-block text-xs text-gray-400">{ingredient.category}</span>
          )}
        </div>
        <div className="flex flex-col items-end gap-1">
          <RiskBadge level={ingredient.overall_risk_level} />
          <span className="text-xs text-gray-400">{ingredient.evidence_count} papers</span>
        </div>
      </div>
    </Link>
  );
}
