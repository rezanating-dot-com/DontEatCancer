"use client";

import { useState } from "react";

import { generateOverview } from "@/lib/api";
import type { IngredientOverview as OverviewType } from "@/lib/types";

export default function IngredientOverview({
  slug,
  initialOverview,
}: {
  slug: string;
  initialOverview: OverviewType | null;
}) {
  const [overview, setOverview] = useState<OverviewType | null>(initialOverview);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setGenerating(true);
    setError(null);
    try {
      const data = await generateOverview(slug);
      setOverview(data);
    } catch {
      setError("Failed to generate overview. Please try again.");
    } finally {
      setGenerating(false);
    }
  };

  if (!overview) {
    return (
      <div className="mb-8 rounded-lg border border-dashed border-gray-300 bg-gray-50 p-6 text-center">
        <p className="text-gray-500 mb-3">No overview yet for this ingredient.</p>
        <button
          onClick={handleGenerate}
          disabled={generating}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {generating ? "Generating..." : "Generate Overview"}
        </button>
        {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
      </div>
    );
  }

  return (
    <div className="mb-8 rounded-lg border border-gray-200 bg-white overflow-hidden">
      <div className="px-5 py-3 bg-gray-50 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Overview</h2>
      </div>

      <div className="p-5 space-y-5">
        <Section title="What is it?" text={overview.what_it_is} />
        <Section title="What is it used for?" text={overview.what_its_used_for} />

        <div>
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Commonly found in</h3>
          <div className="flex flex-wrap gap-2">
            {overview.common_foods.map((food) => (
              <span
                key={food}
                className="px-2.5 py-1 bg-amber-50 border border-amber-200 rounded-full text-sm text-amber-800"
              >
                {food}
              </span>
            ))}
          </div>
        </div>

        {overview.other_names.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Also known as</h3>
            <div className="flex flex-wrap gap-2">
              {overview.other_names.map((name) => (
                <span
                  key={name}
                  className="px-2.5 py-1 bg-gray-100 border border-gray-200 rounded-full text-sm text-gray-700"
                >
                  {name}
                </span>
              ))}
            </div>
          </div>
        )}

        <Section title="Regulatory status" text={overview.regulatory_status} />

        <div className="rounded-lg bg-blue-50 border border-blue-200 p-4">
          <h3 className="text-sm font-semibold text-blue-800 mb-1">Safety at a glance</h3>
          <p className="text-sm text-blue-700 leading-relaxed">{overview.quick_safety_note}</p>
        </div>
      </div>
    </div>
  );
}

function Section({ title, text }: { title: string; text: string }) {
  return (
    <div>
      <h3 className="text-sm font-semibold text-gray-700 mb-1">{title}</h3>
      <p className="text-sm text-gray-600 leading-relaxed">{text}</p>
    </div>
  );
}
