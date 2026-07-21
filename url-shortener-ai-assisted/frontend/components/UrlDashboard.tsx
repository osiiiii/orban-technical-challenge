"use client";

import { ShortUrl } from "@/lib/api";

interface Props {
  urls: ShortUrl[];
  loading: boolean;
  error: string | null;
  onRefresh: () => void;
}

function isExpired(url: ShortUrl): boolean {
  return url.expires_at != null && new Date(url.expires_at) <= new Date();
}

export default function UrlDashboard({
  urls,
  loading,
  error,
  onRefresh,
}: Props) {
  return (
    <div className="card">
      <div className="dash-head">
        <h2>Your links</h2>
        <button className="ghost tiny" onClick={onRefresh} disabled={loading}>
          Refresh
        </button>
      </div>

      {loading && urls.length === 0 && (
        <div className="state">
          <span className="spinner" />
          Loading your links…
        </div>
      )}

      {error && <div className="banner error">{error}</div>}

      {!loading && !error && urls.length === 0 && (
        <div className="state">
          No links yet. Shorten one above and it will show up here.
        </div>
      )}

      {urls.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Short code</th>
              <th>Destination</th>
              <th className="right">Clicks</th>
            </tr>
          </thead>
          <tbody>
            {urls.map((u) => (
              <tr key={u.short_code}>
                <td>
                  <a
                    className="code-cell"
                    href={u.short_url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    /{u.short_code}
                  </a>{" "}
                  {isExpired(u) && <span className="badge">expired</span>}
                </td>
                <td>
                  <span className="target" title={u.long_url}>
                    {u.long_url}
                  </span>
                </td>
                <td className="right">
                  <span className="clicks">{u.click_count}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
