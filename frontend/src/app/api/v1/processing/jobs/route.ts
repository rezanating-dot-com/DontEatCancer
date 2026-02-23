import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { mapProcessingJob } from "@/lib/api-helpers";

export async function GET(request: NextRequest) {
  const sp = request.nextUrl.searchParams;
  const skip = parseInt(sp.get("skip") || "0", 10);
  const limit = parseInt(sp.get("limit") || "20", 10);

  const jobs = await prisma.processingJob.findMany({
    orderBy: { createdAt: "desc" },
    skip,
    take: limit,
  });

  return NextResponse.json(jobs.map(mapProcessingJob));
}
