"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { api, ApiError, type Note } from "@/lib/api";

function formatDate(iso: string) {
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export default function HomePage() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [query, setQuery] = useState("");
  const [activeTag, setActiveTag] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const q = query.trim();
      const data =
        q || activeTag
          ? await api.search({ q: q || undefined, tag: activeTag || undefined })
          : await api.list();
      setNotes(data);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Could not load notes.",
      );
      setNotes([]);
    } finally {
      setLoading(false);
    }
  }, [query, activeTag]);

  useEffect(() => {
    load();
  }, [activeTag]);

  // Initial load.
  useEffect(() => {
    load();
  }, []);

  async function handleDelete(id: number) {
    if (!confirm("Delete this note? This can't be undone.")) return;
    try {
      await api.remove(id);
      setNotes((prev) => prev.filter((n) => n.id !== id));
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Could not delete the note.",
      );
    }
  }

  return (
    <main>
      <header className="masthead">
        <div>
          <div className="eyebrow">Notes API Demo</div>
          <h1>Notes</h1>
        </div>
        <Link href="/notes/new" className="btn primary">
          New note
        </Link>
      </header>

      <div className="searchbar">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && load()}
          placeholder="Search title and body…"
          aria-label="Search notes"
        />
        <button className="btn" onClick={load}>
          Search
        </button>
        {(query || activeTag) && (
          <button
            className="btn"
            onClick={() => {
              setQuery("");
              setActiveTag(null);
            }}
          >
            Clear
          </button>
        )}
      </div>

      {activeTag && (
        <p className="hint">
          Filtering by tag: <strong>{activeTag}</strong>
        </p>
      )}

      {error && <div className="banner error">{error}</div>}

      {loading ? (
        <p className="hint">Loading…</p>
      ) : notes.length === 0 ? (
        <div className="empty">
          {query || activeTag
            ? "No notes match your search."
            : "No notes yet. Create your first note."}
        </div>
      ) : (
        <div className="note-list">
          {notes.map((note) => (
            <article className="note-card" key={note.id}>
              <h2>{note.title}</h2>
              {note.body && <p className="body">{note.body}</p>}
              <div className="note-meta">
                <div className="tags">
                  {note.tags.map((tag) => (
                    <button
                      key={tag}
                      className={`tag ${activeTag === tag ? "active" : ""}`}
                      onClick={() =>
                        setActiveTag(activeTag === tag ? null : tag)
                      }
                    >
                      #{tag}
                    </button>
                  ))}
                </div>
                <div className="card-actions">
                  <Link href={`/notes/${note.id}/edit`} className="btn">
                    Edit
                  </Link>
                  <button
                    className="btn danger"
                    onClick={() => handleDelete(note.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
              <p className="timestamp" style={{ marginTop: 10 }}>
                updated {formatDate(note.updated_at)}
              </p>
            </article>
          ))}
        </div>
      )}
    </main>
  );
}
