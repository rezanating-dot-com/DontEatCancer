"use client";

const RISK_COLORS: Record<string, string> = {
  safe: "bg-green-100 text-green-800 border-green-200",
  low: "bg-blue-100 text-blue-800 border-blue-200",
  moderate: "bg-yellow-100 text-yellow-800 border-yellow-200",
  high: "bg-red-100 text-red-800 border-red-200",
  insufficient: "bg-gray-100 text-gray-600 border-gray-200",
};

export default function RiskBadge({ level }: { level: string | null }) {
  const label = level || "unknown";
  const colors = RISK_COLORS[label] || RISK_COLORS.insufficient;
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${colors}`}
    >
      {label.charAt(0).toUpperCase() + label.slice(1)}
    </span>
  );
}
