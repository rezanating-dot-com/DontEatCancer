import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { mapEvidenceOut } from "@/lib/api-helpers";

export async function GET(request: NextRequest) {
  const sp = request.nextUrl.searchParams;
  const skip = parseInt(sp.get("skip") || "0", 10);
  const limit = parseInt(sp.get("limit") || "50", 10);

  const evidence = await prisma.evidence.findMany({
    where: { needsReview: true },
    orderBy: { createdAt: "desc" },
    skip,
    take: limit,
  });

  return NextResponse.json(evidence.map(mapEvidenceOut));
}
