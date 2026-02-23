"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import EvidenceCard from "@/components/EvidenceCard";
import SearchBar from "@/components/SearchBar";
import { getCategories, getEvidence, getStats } from "@/lib/api";
import type { Evidence, Stats } from "@/lib/types";

const CATEGORY_COLORS: Record<string, string> = {
  preservative: "bg-red-50 border-red-200 text-red-700",
  colorant: "bg-purple-50 border-purple-200 text-purple-700",
  sweetener: "bg-pink-50 border-pink-200 text-pink-700",
  antioxidant: "bg-green-50 border-green-200 text-green-700",
  emulsifier: "bg-blue-50 border-blue-200 text-blue-700",
  flavor: "bg-orange-50 border-orange-200 text-orange-700",
};

export default function Home() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [categories, setCategories] = useState<string[]>([]);
  const [recentEvidence, setRecentEvidence] = useState<Evidence[]>([]);

  useEffect(() => {
    getStats().then(setStats).catch(() => {});
    getCategories().then(setCategories).catch(() => {});
    getEvidence({ limit: 5 }).then(setRecentEvidence).catch(() => {});
  }, []);

  return (
    <div className="flex flex-col items-center gap-8 sm:gap-12 py-6 sm:py-12">
      <div className="text-center px-2">
        <h1 className="text-2xl sm:text-4xl font-bold text-gray-900">DontEatCancer</h1>
        <p className="mt-3 text-base sm:text-lg text-gray-500 max-w-xl">
          Research repository aggregating scientific evidence on food chemicals and cancer risk
          from Chinese, Middle Eastern, and European sources.
        </p>
      </div>

      <SearchBar />

      {stats && (
        <div className="flex gap-6 sm:gap-8 text-center">
          <div>
            <p className="text-2xl sm:text-3xl font-bold text-gray-900">{stats.ingredient_count}</p>
            <p className="text-sm text-gray-500">Ingredients</p>
          </div>
          <div>
            <p className="text-2xl sm:text-3xl font-bold text-gray-900">{stats.evidence_count}</p>
            <p className="text-sm text-gray-500">Papers</p>
          </div>
          <div>
            <p className="text-2xl sm:text-3xl font-bold text-amber-600">{stats.review_count}</p>
            <p className="text-sm text-gray-500">Needs Review</p>
          </div>
        </div>
      )}

      {categories.length > 0 && (
        <div className="w-full max-w-3xl">
          <h2 className="text-lg font-semibold text-gray-700 mb-4">Browse by Category</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {categories.map((cat) => (
              <Link
                key={cat}
                href={`/ingredients?category=${encodeURIComponent(cat)}`}
                className={`p-4 border rounded-lg text-center capitalize hover:shadow-sm transition-shadow ${
                  CATEGORY_COLORS[cat.toLowerCase()] || "bg-gray-50 border-gray-200 text-gray-700"
                }`}
              >
                {cat}
              </Link>
            ))}
          </div>
        </div>
      )}

      {recentEvidence.length > 0 && (
        <div className="w-full max-w-3xl">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-700">Recently Added</h2>
            <Link href="/evidence" className="text-sm text-blue-600 hover:text-blue-800">
              View all &rarr;
            </Link>
          </div>
          <div className="flex flex-col gap-3">
            {recentEvidence.map((ev) => (
              <EvidenceCard key={ev.id} evidence={ev} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
