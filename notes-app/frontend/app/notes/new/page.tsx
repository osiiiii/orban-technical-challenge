"use client";

import Link from "next/link";
import NoteForm from "@/components/NoteForm";
import { api } from "@/lib/api";

export default function NewNotePage() {
  return (
    <main>
      <Link href="/" className="back-link">
         &laquo; Go back
      </Link>
      <header className="masthead">
        <div>
          <div className="eyebrow">Create</div>
          <h1>New note</h1>
        </div>
      </header>
      <NoteForm
        onSubmit={async (input) => {
          await api.create(input);
        }}
        submitLabel="Create note"
      />
    </main>
  );
}
