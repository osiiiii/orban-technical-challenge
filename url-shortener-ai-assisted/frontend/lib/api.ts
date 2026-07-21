// Small typed wrapper around the backend API.
// The API key is passed per-call so the caller controls where it's stored.

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE?.replace(/\/$/, "") || "http://localhost:8000";

export interface ShortUrl {
  short_code: string;
  short_url: string;
  long_url: string;
  click_count: number;
  created_at: string;
  expires_at: string | null;
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function handle<T>(res: Response): Promise<T> {
  if (res.ok) {
    return (await res.json()) as T;
  }
  // FastAPI puts human-readable messages under `detail`.
  let detail = `Request failed (${res.status})`;
  try {
    const body = await res.json();
    if (typeof body?.detail === "string") {
      detail = body.detail;
    } else if (Array.isArray(body?.detail)) {
      // Validation errors come back as an array of issues.
      detail = body.detail.map((d: { msg?: string }) => d.msg).join("; ");
    }
  } catch {
    /* response had no JSON body */
  }
  throw new ApiError(res.status, detail);
}

export async function shortenUrl(
  apiKey: string,
  longUrl: string,
  expiresInDays?: number
): Promise<ShortUrl> {
  const res = await fetch(`${API_BASE}/api/shorten`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-API-Key": apiKey },
    body: JSON.stringify({
      long_url: longUrl,
      expires_in_days: expiresInDays ?? null,
    }),
  });
  return handle<ShortUrl>(res);
}

export async function listUrls(apiKey: string): Promise<ShortUrl[]> {
  const res = await fetch(`${API_BASE}/api/urls`, {
    headers: { "X-API-Key": apiKey },
  });
  return handle<ShortUrl[]>(res);
}
