import { NextResponse } from "next/server";

export async function POST() {
  return NextResponse.json(
    {
      detail:
        "Text upload is not available in the web app. Use the Python CLI instead: python -m pipeline.cli process-text 'your text'",
    },
    { status: 501 }
  );
}
