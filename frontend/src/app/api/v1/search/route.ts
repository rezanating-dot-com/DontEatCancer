import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { mapIngredientSummary, mapEvidenceOut } from "@/lib/api-helpers";

export async function GET(request: NextRequest) {
  const q = request.nextUrl.searchParams.get("q") || "";

  const [ingredients, evidence] = await Promise.all([
    prisma.ingredient.findMany({
      where: {
        OR: [
          { canonicalName: { contains: q, mode: "insensitive" } },
          { description: { contains: q, mode: "insensitive" } },
        ],
      },
      take: 20,
    }),
    prisma.evidence.findMany({
      where: {
        OR: [
          { title: { contains: q, mode: "insensitive" } },
          { abstractEnglish: { contains: q, mode: "insensitive" } },
          { findingsSummary: { contains: q, mode: "insensitive" } },
        ],
      },
      take: 20,
    }),
  ]);

  return NextResponse.json({
    ingredients: ingredients.map(mapIngredientSummary),
    evidence: evidence.map(mapEvidenceOut),
  });
}
