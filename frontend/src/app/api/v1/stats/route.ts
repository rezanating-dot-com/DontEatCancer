import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function GET() {
  const [ingredientCount, evidenceCount, reviewCount] = await Promise.all([
    prisma.ingredient.count(),
    prisma.evidence.count(),
    prisma.evidence.count({ where: { needsReview: true } }),
  ]);

  return NextResponse.json({
    ingredient_count: ingredientCount,
    evidence_count: evidenceCount,
    review_count: reviewCount,
  });
}
