const base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function apiUrl(path: string): string {
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${base}/api/v1${p}`;
}

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${base}/api/v1${path.startsWith("/") ? path : `/${path}`}`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}
