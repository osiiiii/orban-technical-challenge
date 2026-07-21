"use client";

import { useState } from "react";
import { shortenUrl, ApiError, ShortUrl } from "@/lib/api";

interface Props {
  apiKey: string;
  onCreated: (url: ShortUrl) => void;
}

export default function ShortenForm({ apiKey, onCreated }: Props) {
  const [longUrl, setLongUrl] = useState("");
  const [expiresInDays, setExpiresInDays] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ShortUrl | null>(null);
  const [copied, setCopied] = useState(false);

  async function submit() {
    setError(null);
    setResult(null);
    if (!apiKey) {
      setError("Add your API key above before creating links.");
      return;
    }
    if (!longUrl.trim()) {
      setError("Paste a URL to shorten.");
      return;
    }
    setLoading(true);
    try {
      const days = expiresInDays ? Number(expiresInDays) : undefined;
      const created = await shortenUrl(apiKey, longUrl.trim(), days);
      setResult(created);
      setLongUrl("");
      setExpiresInDays("");
      onCreated(created);
    } catch (e) {
      const msg =
        e instanceof ApiError ? e.message : "Could not reach the server.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  async function copy() {
    if (!result) return;
    await navigator.clipboard.writeText(result.short_url);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <div className="card">
      <h2>Shorten a link</h2>

      <div className="field">
        <label htmlFor="long">Long URL</label>
        <input
          id="long"
          className="mono"
          type="url"
          placeholder="https://example.com/a/very/long/path?with=params"
          value={longUrl}
          onChange={(e) => setLongUrl(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
        />
      </div>

      <div className="field-row">
        <div className="field">
          <label htmlFor="expiry">Expires in (days)</label>
          <input
            id="expiry"
            type="number"
            min={1}
            placeholder="never"
            value={expiresInDays}
            onChange={(e) => setExpiresInDays(e.target.value)}
          />
          <div className="hint">Leave blank for a link that never expires.</div>
        </div>
        <div className="field" style={{ alignSelf: "flex-start" }}>
          <label>&nbsp;</label>
          <button onClick={submit} disabled={loading}>
            {loading ? "Shortening…" : "Shorten"}
          </button>
        </div>
      </div>

      {error && <div className="banner error">{error}</div>}

      {result && (
        <div className="banner success">
          <span>
            Created <code>{result.short_url}</code>
          </span>
          <button className="ghost tiny" onClick={copy}>
            {copied ? "Copied" : "Copy"}
          </button>
        </div>
      )}
    </div>
  );
}
