import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { mapEvidenceDetail } from "@/lib/api-helpers";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const evidenceId = parseInt(id, 10);

  const evidence = await prisma.evidence.findUnique({
    where: { id: evidenceId },
    include: {
      ingredientLinks: {
        include: {
          ingredient: { select: { canonicalName: true, slug: true } },
        },
      },
    },
  });

  if (!evidence) {
    return NextResponse.json({ detail: "Evidence not found" }, { status: 404 });
  }

  return NextResponse.json({
    ...mapEvidenceDetail(evidence),
    ingredients: evidence.ingredientLinks.map((link) => ({
      name: link.ingredient.canonicalName,
      slug: link.ingredient.slug,
      relevance: link.relevance,
    })),
  });
}
