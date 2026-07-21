"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import NoteForm from "@/components/NoteForm";
import { api, ApiError, type Note } from "@/lib/api";

export default function EditNotePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const noteId = Number(id);

  const [note, setNote] = useState<Note | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        setNote(await api.get(noteId));
      } catch (err) {
        setError(
          err instanceof ApiError ? err.message : "Could not load the note.",
        );
      } finally {
        setLoading(false);
      }
    })();
  }, [noteId]);

  return (
    <main>
      <Link href="/" className="back-link">
      Back to notes
      </Link>
      <header className="masthead">
        <div>
          <div className="eyebrow">Edit</div>
          <h1>Edit note</h1>
        </div>
      </header>

      {loading ? (
        <p className="hint">Loading…</p>
      ) : error ? (
        <div className="banner error">{error}</div>
      ) : note ? (
        <NoteForm
          initial={note}
          onSubmit={async (input) => {
            await api.update(noteId, input);
          }}
          submitLabel="Save changes"
        />
      ) : null}
    </main>
  );
}
