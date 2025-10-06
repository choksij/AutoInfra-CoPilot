import { NextResponse } from "next/server";

export async function GET() {
  try {
    const base = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";
    const res = await fetch(`${base}/status?run_id=latest`, {
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
    });

    if (!res.ok) {
      return NextResponse.json(
        { error: `Backend responded with ${res.status}` },
        { status: res.status }
      );
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (err: any) {
    return NextResponse.json(
      { error: err?.message ?? "Failed to fetch latest status" },
      { status: 500 }
    );
  }
}
