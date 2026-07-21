"use client";

import { useCallback, useEffect, useState } from "react";
import ShortenForm from "@/components/ShortenForm";
import UrlDashboard from "@/components/UrlDashboard";
import { listUrls, ApiError, ShortUrl } from "@/lib/api";

const KEY_STORAGE = "shortener_api_key";

export default function Home() {
  const [apiKey, setApiKey] = useState("");
  const [urls, setUrls] = useState<ShortUrl[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Restore the saved API key on first load.
  useEffect(() => {
    const saved = localStorage.getItem(KEY_STORAGE);
    if (saved) setApiKey(saved);
  }, []);

  const refresh = useCallback(async () => {
    if (!apiKey) {
      setUrls([]);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      setUrls(await listUrls(apiKey));
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) {
        setError("That API key was rejected. Check it and try again.");
      } else {
        setError(
          e instanceof ApiError ? e.message : "Could not reach the server."
        );
      }
      setUrls([]);
    } finally {
      setLoading(false);
    }
  }, [apiKey]);

  // Reload the dashboard whenever the key changes.
  useEffect(() => {
    refresh();
  }, [refresh]);

  function saveKey(value: string) {
    setApiKey(value);
    localStorage.setItem(KEY_STORAGE, value);
  }

  function handleCreated(created: ShortUrl) {
    // Optimistically merge, then refetch for authoritative counts.
    setUrls((prev) => {
      const without = prev.filter((u) => u.short_code !== created.short_code);
      return [created, ...without];
    });
    refresh();
  }

  return (
    <main className="page">
      <div className="masthead">
        <h1>
          snip<span className="dot">/</span>
        </h1>
      </div>
      <p className="tagline">
        Paste a long URL, get a short one, and watch the clicks add up.
      </p>

      <div className="transform">
        <span className="long">
          https://example.com/2026/reports/q3/annexes/section-4?ref=newsletter
        </span>
        <span className="arrow">──▶</span>
        <span className="short">snip/7Tw4wW</span>
      </div>

      <div className="card">
        <h2>API key</h2>
        <div className="field" style={{ marginBottom: 0 }}>
          <input
            className="mono"
            type="password"
            placeholder="X-API-Key used to create and list links"
            value={apiKey}
            onChange={(e) => saveKey(e.target.value)}
          />
          <div className="hint">
            Stored in your browser only. Matches <code>API_KEY</code> in the
            backend&apos;s environment.
          </div>
        </div>
      </div>

      <ShortenForm apiKey={apiKey} onCreated={handleCreated} />

      <UrlDashboard
        urls={urls}
        loading={loading}
        error={error}
        onRefresh={refresh}
      />
    </main>
  );
}
