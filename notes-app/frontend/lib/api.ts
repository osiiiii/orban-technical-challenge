export interface Note {
  id: number;
  title: string;
  body: string;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface NoteInput {
  title: string;
  body: string;
  tags: string[];
}

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";
const KEY = process.env.NEXT_PUBLIC_API_KEY ?? "";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": KEY,
        ...(init.headers ?? {}),
      },
      cache: "no-store",
    });
  } catch {
    throw new ApiError(
      "Could not reach the API. Is the backend running on " + BASE + "?",
      0,
    );
  }

  if (res.status === 204) return undefined as T;

  let data: unknown = null;
  const text = await res.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }

  if (!res.ok) {
    const detail =
      data && typeof data === "object" && "detail" in data
        ? String((data as { detail: unknown }).detail)
        : `Request failed (${res.status})`;
    throw new ApiError(detail, res.status);
  }

  return data as T;
}

export const api = {
  list: () => request<Note[]>("/notes"),
  get: (id: number) => request<Note>(`/notes/${id}`),
  create: (input: NoteInput) =>
    request<Note>("/notes", { method: "POST", body: JSON.stringify(input) }),
  update: (id: number, input: Partial<NoteInput>) =>
    request<Note>(`/notes/${id}`, {
      method: "PUT",
      body: JSON.stringify(input),
    }),
  remove: (id: number) =>
    request<void>(`/notes/${id}`, { method: "DELETE" }),
  search: (params: { q?: string; tag?: string }) => {
    const qs = new URLSearchParams();
    if (params.q) qs.set("q", params.q);
    if (params.tag) qs.set("tag", params.tag);
    return request<Note[]>(`/notes/search?${qs.toString()}`);
  },
};
