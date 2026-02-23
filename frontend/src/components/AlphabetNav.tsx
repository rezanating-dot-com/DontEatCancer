"use client";

const LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

export default function AlphabetNav({
  activeLetter,
  onSelect,
}: {
  activeLetter: string | null;
  onSelect: (letter: string | null) => void;
}) {
  return (
    <div className="flex flex-wrap gap-1">
      <button
        onClick={() => onSelect(null)}
        className={`px-2 py-1 text-sm rounded ${
          activeLetter === null
            ? "bg-blue-600 text-white"
            : "bg-gray-100 text-gray-600 hover:bg-gray-200"
        }`}
      >
        All
      </button>
      {LETTERS.map((letter) => (
        <button
          key={letter}
          onClick={() => onSelect(letter)}
          className={`px-2 py-1 text-sm rounded ${
            activeLetter === letter
              ? "bg-blue-600 text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          {letter}
        </button>
      ))}
    </div>
  );
}
