import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { mapEvidenceOut } from "@/lib/api-helpers";

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const evidenceId = parseInt(id, 10);
  const body = await request.json();

  const existing = await prisma.evidence.findUnique({
    where: { id: evidenceId },
  });

  if (!existing) {
    return NextResponse.json({ detail: "Evidence not found" }, { status: 404 });
  }

  const data: Record<string, unknown> = {
    processingStatus: "reviewed",
  };

  if (body.risk_level !== undefined) data.riskLevel = body.risk_level;
  if (body.risk_direction !== undefined) data.riskDirection = body.risk_direction;
  if (body.findings_summary !== undefined) data.findingsSummary = body.findings_summary;
  if (body.plain_language_summary !== undefined) data.plainLanguageSummary = body.plain_language_summary;
  if (body.url !== undefined) data.url = body.url;
  if (body.full_text !== undefined) data.fullText = body.full_text;
  if (body.needs_review !== undefined) data.needsReview = body.needs_review;

  const updated = await prisma.evidence.update({
    where: { id: evidenceId },
    data,
  });

  return NextResponse.json(mapEvidenceOut(updated));
}
