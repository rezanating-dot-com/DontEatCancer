"use client";

import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";

import EvidenceCard from "@/components/EvidenceCard";
import IngredientCard from "@/components/IngredientCard";
import SearchBar from "@/components/SearchBar";
import { search } from "@/lib/api";
import type { SearchResults } from "@/lib/types";

function SearchContent() {
  const searchParams = useSearchParams();
  const q = searchParams.get("q") || "";
  const [results, setResults] = useState<SearchResults | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!q) return;
    setLoading(true);
    search(q)
      .then(setResults)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [q]);

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Search</h1>
      <div className="mb-8">
        <SearchBar defaultValue={q} />
      </div>

      {loading && <p className="text-gray-400">Searching...</p>}

      {results && !loading && (
        <div className="space-y-8">
          {results.ingredients.length > 0 && (
            <section>
              <h2 className="text-lg font-semibold text-gray-700 mb-3">
                Ingredients ({results.ingredients.length})
              </h2>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {results.ingredients.map((ing) => (
                  <IngredientCard key={ing.id} ingredient={ing} />
                ))}
              </div>
            </section>
          )}

          {results.evidence.length > 0 && (
            <section>
              <h2 className="text-lg font-semibold text-gray-700 mb-3">
                Evidence ({results.evidence.length})
              </h2>
              <div className="flex flex-col gap-3">
                {results.evidence.map((ev) => (
                  <EvidenceCard key={ev.id} evidence={ev} />
                ))}
              </div>
            </section>
          )}

          {results.ingredients.length === 0 && results.evidence.length === 0 && (
            <p className="text-gray-400">No results found for &quot;{q}&quot;.</p>
          )}
        </div>
      )}
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={<p className="text-gray-400">Loading...</p>}>
      <SearchContent />
    </Suspense>
  );
}
