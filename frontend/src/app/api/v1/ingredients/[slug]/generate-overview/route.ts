import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function POST(
  _request: NextRequest,
  { params }: { params: Promise<{ slug: string }> }
) {
  const { slug } = await params;

  try {
    const res = await fetch(
      `${BACKEND_URL}/api/v1/ingredients/${slug}/generate-overview`,
      { method: "POST", headers: { "Content-Type": "application/json" } }
    );

    if (!res.ok) {
      const error = await res.text();
      return NextResponse.json(
        { detail: error },
        { status: res.status }
      );
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch {
    return NextResponse.json(
      { detail: "Failed to connect to backend" },
      { status: 502 }
    );
  }
}
