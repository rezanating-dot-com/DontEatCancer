import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { mapEvidenceOut } from "@/lib/api-helpers";

export async function GET(request: NextRequest) {
  const sp = request.nextUrl.searchParams;
  const riskLevel = sp.get("risk_level");
  const studyType = sp.get("study_type");
  const yearMin = sp.get("year_min");
  const yearMax = sp.get("year_max");
  const skip = parseInt(sp.get("skip") || "0", 10);
  const limit = parseInt(sp.get("limit") || "50", 10);

  const where: Record<string, unknown> = {};
  if (riskLevel) where.riskLevel = riskLevel;
  if (studyType) where.studyType = studyType;
  if (yearMin || yearMax) {
    where.publicationYear = {
      ...(yearMin ? { gte: parseInt(yearMin, 10) } : {}),
      ...(yearMax ? { lte: parseInt(yearMax, 10) } : {}),
    };
  }

  const evidence = await prisma.evidence.findMany({
    where,
    orderBy: { createdAt: "desc" },
    skip,
    take: limit,
  });

  return NextResponse.json(evidence.map(mapEvidenceOut));
}
