import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { mapIngredientDetail } from "@/lib/api-helpers";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ slug: string }> }
) {
  const { slug } = await params;

  const ingredient = await prisma.ingredient.findUnique({
    where: { slug },
    include: { aliases: true },
  });

  if (!ingredient) {
    return NextResponse.json({ detail: "Ingredient not found" }, { status: 404 });
  }

  return NextResponse.json(mapIngredientDetail(ingredient));
}
