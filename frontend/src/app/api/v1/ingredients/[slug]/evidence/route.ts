import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { mapEvidenceOut } from "@/lib/api-helpers";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ slug: string }> }
) {
  const { slug } = await params;

  const ingredient = await prisma.ingredient.findUnique({
    where: { slug },
    select: { id: true },
  });

  if (!ingredient) {
    return NextResponse.json({ detail: "Ingredient not found" }, { status: 404 });
  }

  const links = await prisma.ingredientEvidence.findMany({
    where: { ingredientId: ingredient.id },
    include: { evidence: true },
    orderBy: { evidence: { publicationYear: { sort: "desc", nulls: "last" } } },
  });

  return NextResponse.json(
    links.map((link) => ({
      evidence: mapEvidenceOut(link.evidence),
      relevance: link.relevance,
    }))
  );
}
