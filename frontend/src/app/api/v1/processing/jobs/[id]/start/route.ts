import { NextResponse } from "next/server";

export async function POST() {
  return NextResponse.json(
    {
      detail:
        "Job processing is not available in the web app. Use the Python CLI instead: python -m pipeline.cli process file.ris",
    },
    { status: 501 }
  );
}
