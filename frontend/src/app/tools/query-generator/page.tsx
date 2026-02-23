"use client";

import { useState } from "react";

import { generateQueries } from "@/lib/api";
import type { QueryResult } from "@/lib/types";

const LANG_NAMES: Record<string, string> = {
  en: "English", zh: "Chinese", ar: "Arabic", fr: "French", de: "German",
};

export default function QueryGeneratorPage() {
  const [ingredient, setIngredient] = useState("");
  const [database, setDatabase] = useState("ebsco");
  const [result, setResult] = useState<QueryResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState<string | null>(null);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ingredient.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const data = await generateQueries(ingredient.trim(), database);
      setResult(data);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = (lang: string, query: string) => {
    navigator.clipboard.writeText(query);
    setCopied(lang);
    setTimeout(() => setCopied(null), 2000);
  };

  return (
    <div className="max-w-3xl">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Search Query Generator</h1>
      <p className="text-gray-500 mb-6">
        Generate multilingual Boolean search queries for academic databases (EBSCO, Scopus, Web of Science).
      </p>

      <form onSubmit={handleGenerate} className="flex flex-col gap-4 mb-8">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Ingredient name (English)</label>
          <input
            type="text"
            value={ingredient}
            onChange={(e) => setIngredient(e.target.value)}
            placeholder="e.g., sodium nitrite"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Database format</label>
          <select
            value={database}
            onChange={(e) => setDatabase(e.target.value)}
            className="w-full px-3 py-2.5 border border-gray-300 rounded-lg"
          >
            <option value="ebsco">EBSCO</option>
            <option value="scopus">Scopus</option>
            <option value="wos">Web of Science</option>
            <option value="pubmed">PubMed</option>
          </select>
        </div>
        <button
          type="submit"
          disabled={loading || !ingredient.trim()}
          className="w-full sm:w-auto px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Generating..." : "Generate Queries"}
        </button>
      </form>

      {result && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-700">
            Queries for &quot;{result.ingredient}&quot; ({result.database.toUpperCase()})
          </h2>
          {Object.entries(result.queries).map(([lang, query]) => (
            <div key={lang} className="p-4 bg-white border border-gray-200 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-600">
                  {LANG_NAMES[lang] || lang}
                </span>
                <button
                  onClick={() => handleCopy(lang, query)}
                  className="text-sm px-3 py-1.5 text-blue-600 hover:bg-blue-50 rounded"
                >
                  {copied === lang ? "Copied!" : "Copy"}
                </button>
              </div>
              <pre className="text-sm text-gray-800 whitespace-pre-wrap break-words font-mono bg-gray-50 p-3 rounded">
                {query}
              </pre>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
