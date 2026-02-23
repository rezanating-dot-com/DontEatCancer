import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { mapIngredientDetail, mapIngredientSummary } from "@/lib/api-helpers";

export async function GET(request: NextRequest) {
  const sp = request.nextUrl.searchParams;
  const category = sp.get("category");
  const riskLevel = sp.get("risk_level");
  const letter = sp.get("letter");
  const skip = parseInt(sp.get("skip") || "0", 10);
  const limit = parseInt(sp.get("limit") || "50", 10);

  const where: Record<string, unknown> = {};
  if (category) where.category = category;
  if (riskLevel) where.overallRiskLevel = riskLevel;
  if (letter) where.canonicalName = { startsWith: letter, mode: "insensitive" };

  const ingredients = await prisma.ingredient.findMany({
    where,
    orderBy: { canonicalName: "asc" },
    skip,
    take: limit,
  });

  return NextResponse.json(ingredients.map(mapIngredientSummary));
}

export async function POST(request: NextRequest) {
  const body = await request.json();

  const slug = body.canonical_name
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, "")
    .replace(/[\s_]+/g, "-")
    .replace(/^-+|-+$/g, "");

  const ingredient = await prisma.ingredient.create({
    data: {
      canonicalName: body.canonical_name,
      slug,
      casNumber: body.cas_number ?? null,
      eNumber: body.e_number ?? null,
      category: body.category ?? null,
      description: body.description ?? null,
      overallRiskLevel: body.overall_risk_level ?? null,
      aliases: {
        create: (body.aliases ?? []).map(
          (a: { alias_name: string; language: string; is_primary?: boolean }) => ({
            aliasName: a.alias_name,
            language: a.language,
            isPrimary: a.is_primary ?? false,
          })
        ),
      },
    },
    include: { aliases: true },
  });

  return NextResponse.json(mapIngredientDetail(ingredient), { status: 201 });
}
