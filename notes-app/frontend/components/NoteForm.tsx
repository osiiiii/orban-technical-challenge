"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ApiError, type Note, type NoteInput } from "@/lib/api";

interface Props {
  initial?: Note;
  onSubmit: (input: NoteInput) => Promise<void>;
  submitLabel: string;
}

export default function NoteForm({ initial, onSubmit, submitLabel }: Props) {
  const router = useRouter();
  const [title, setTitle] = useState(initial?.title ?? "");
  const [body, setBody] = useState(initial?.body ?? "");
  const [tags, setTags] = useState((initial?.tags ?? []).join(", "));
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function handleSave() {
    setError(null);

    if (!title.trim()) {
      setError("Give the note a title before saving it.");
      return;
    }

    const input: NoteInput = {
      title: title.trim(),
      body,
      tags: tags
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean),
    };

    setSaving(true);
    try {
      await onSubmit(input);
      router.push("/");
      router.refresh();
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Something went wrong while saving.",
      );
      setSaving(false);
    }
  }

  return (
    <div>
      {error && <div className="banner error">{error}</div>}

      <div className="field">
        <label htmlFor="title">Title</label>
        <input
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="What is this note about?"
          autoFocus
        />
      </div>

      <div className="field">
        <label htmlFor="body">Body</label>
        <textarea
          id="body"
          value={body}
          onChange={(e) => setBody(e.target.value)}
          placeholder="Write the note here…"
        />
      </div>

      <div className="field">
        <label htmlFor="tags">Tags</label>
        <input
          id="tags"
          value={tags}
          onChange={(e) => setTags(e.target.value)}
          placeholder="comma, separated, tags"
        />
      </div>
      <p className="hint">Separate tags with commas.</p>

      <div className="form-actions">
        <button className="btn primary" onClick={handleSave} disabled={saving}>
          {saving ? "Saving…" : submitLabel}
        </button>
        <button
          className="btn"
          onClick={() => router.push("/")}
          disabled={saving}
        >
          Cancel
        </button>
      </div>
    </div>
  );
}
