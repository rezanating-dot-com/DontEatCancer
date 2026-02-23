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
    <div className="overflow-x-auto -mx-4 px-4 sm:mx-0 sm:px-0">
      <div className="flex flex-wrap gap-1.5 sm:gap-1">
        <button
          onClick={() => onSelect(null)}
          className={`min-w-[2.5rem] min-h-[2.5rem] px-2.5 py-1.5 text-sm rounded ${
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
            className={`min-w-[2.5rem] min-h-[2.5rem] px-2.5 py-1.5 text-sm rounded ${
              activeLetter === letter
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {letter}
          </button>
        ))}
      </div>
    </div>
  );
}
