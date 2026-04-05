import { NextRequest, NextResponse } from "next/server";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function GET(
  request: NextRequest,
  context: { params: { proxy: string[] } }
) {
  return proxy(request, context.params.proxy, "GET");
}

export async function POST(
  request: NextRequest,
  context: { params: { proxy: string[] } }
) {
  return proxy(request, context.params.proxy, "POST");
}

async function proxy(request: NextRequest, segments: string[], method: string) {
  const path = segments.join("/");
  const url = `${API}/${path}${request.nextUrl.search}`;
  const init: RequestInit = { method, headers: { "Content-Type": "application/json" } };
  if (method !== "GET") {
    init.body = await request.text();
  }
  const res = await fetch(url, init);
  const text = await res.text();
  return new NextResponse(text, { status: res.status, headers: res.headers });
}
