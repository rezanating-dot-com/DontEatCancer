"use client";

import { useSearchParams } from "next/navigation";
import { Suspense, useCallback, useEffect, useState } from "react";

import AlphabetNav from "@/components/AlphabetNav";
import IngredientCard from "@/components/IngredientCard";
import { getIngredients } from "@/lib/api";
import type { IngredientSummary } from "@/lib/types";

function IngredientsContent() {
  const searchParams = useSearchParams();
  const categoryParam = searchParams.get("category");
  const [ingredients, setIngredients] = useState<IngredientSummary[]>([]);
  const [letter, setLetter] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(() => {
    setLoading(true);
    getIngredients({
      category: categoryParam || undefined,
      letter: letter || undefined,
      limit: 200,
    })
      .then(setIngredients)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [categoryParam, letter]);

  useEffect(() => { load(); }, [load]);

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Ingredients</h1>
      {categoryParam && (
        <p className="text-gray-500 mb-4">Category: <span className="capitalize font-medium">{categoryParam}</span></p>
      )}

      <div className="mb-6">
        <AlphabetNav activeLetter={letter} onSelect={setLetter} />
      </div>

      {loading ? (
        <p className="text-gray-400">Loading...</p>
      ) : ingredients.length === 0 ? (
        <p className="text-gray-400">No ingredients found.</p>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {ingredients.map((ing) => (
            <IngredientCard key={ing.id} ingredient={ing} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function IngredientsPage() {
  return (
    <Suspense fallback={<p className="text-gray-400">Loading...</p>}>
      <IngredientsContent />
    </Suspense>
  );
}
