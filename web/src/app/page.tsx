"use client";

import { useApiToken } from "@/hooks/useApiToken";
import { useState } from "react";

type QueryResponse = {
  sql: string;
  results: Array<Record<string, any>>;
  meta: {
    profile: string;
    status: string;
    execution_time_ms: number;
    row_count: number | null;
  };
};

type HistoryItem = {
  timestamp: string;
  data_source: string;
  profile: string;
  nl_query: string;
  sql: string;
  status: string;
  row_count: number;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export default function HomePage() {
  const [query, setQuery] = useState(
    "List the first 10 patients with their id, name, and age."
  );
  const [sql, setSql] = useState("");
  const [results, setResults] = useState<Array<Record<string, any>>>([]);
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // NEW: data source + extended profiles
  const [dataSource, setDataSource] = useState("hospital_sqlite");
  const [profile, setProfile] = useState("sqlite-dev");

  const [history, setHistory] = useState<HistoryItem[]>([]);
  const { ensureToken, accounts } = useApiToken();

  async function refreshHistory() {
    try {
      const token = await ensureToken();
      const res = await fetch(`${API_URL}/history`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const body: HistoryItem[] = await res.json();
        setHistory(body);
      }
    } catch (e) {
      console.error("history error", e);
    }
  }

  async function runQuery(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setStatus(null);
    setSql("");
    setResults([]);

    try {
      const token = await ensureToken();

      const res = await fetch(`${API_URL}/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          data_source: dataSource, // <- use selected data source
          profile,                 // <- use selected profile
          query,
        }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Request failed with ${res.status}`);
      }

      const body: QueryResponse = await res.json();
      setSql(body.sql);
      setResults(body.results);
      setStatus(body.meta.status);

      await refreshHistory();
    } catch (err: any) {
      if (err.message?.startsWith("Redirecting")) return;
      setError(err.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  const columns = results.length > 0 ? Object.keys(results[0]) : [];
  const signedInAs =
    accounts.length > 0 ? accounts[0].username : "Not signed in";

  return (
    <main className="min-h-screen bg-slate-950 text-slate-50 flex items-center justify-center py-10">
      <div className="w-full max-w-5xl px-4">
        <header className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">
              SQL‑Speak Enterprise Console
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Natural language to SQL over your selected data source.
            </p>
          </div>
          <div className="text-xs text-right text-slate-300">
            <div className="font-medium">Signed in</div>
            <div className="truncate max-w-xs text-slate-200">
              {signedInAs}
            </div>
          </div>
        </header>

        <div className="grid gap-6 lg:grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)]">
          {/* Left: query + results */}
          <section className="space-y-4">
            <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-4 shadow-sm">
              <div className="flex flex-wrap items-center gap-4 text-xs mb-3">
                <div>
                  <div className="text-slate-400">Data source</div>
                  {/* NEW: real select for data source */}
                  <select
                    className="mt-1 rounded-md border border-slate-700 bg-slate-900 px-2 py-1 text-xs"
                    value={dataSource}
                    onChange={(e) => setDataSource(e.target.value)}
                  >
                    <option value="hospital_sqlite">
                      hospital_sqlite (SQLite)
                    </option>
                    <option value="benchmark_postgres">
                      benchmark_postgres (Postgres)
                    </option>
                    {/* add azure_postgres etc later */}
                  </select>
                </div>

                <div>
                  <div className="text-slate-400">Profile</div>
                  {/* UPDATED: extend profile select */}
                  <select
                    className="mt-1 rounded-md border border-slate-700 bg-slate-900 px-2 py-1 text-xs"
                    value={profile}
                    onChange={(e) => setProfile(e.target.value)}
                  >
                    <option value="sqlite-dev">sqlite-dev</option>
                    <option value="benchmark-postgres">
                      benchmark-postgres
                    </option>
                    {/* keep prod-readonly if you still have it in config */}
                    {/* <option value="prod-readonly">prod-readonly</option> */}
                  </select>
                </div>

                {status && (
                  <div>
                    <div className="text-slate-400">Last run</div>
                    <div className="text-xs text-emerald-400 font-medium">
                      {status}
                    </div>
                  </div>
                )}
              </div>

              <form onSubmit={runQuery} className="space-y-3">
                <div>
                  <label className="block text-xs text-slate-400 mb-1">
                    Natural language query
                  </label>
                  <textarea
                    className="w-full rounded-md border border-slate-700 bg-slate-950/80 p-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                    rows={3}
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <button
                    type="submit"
                    disabled={loading}
                    className="inline-flex items-center rounded-md bg-blue-600 px-4 py-1.5 text-sm font-medium shadow-sm transition hover:bg-blue-500 disabled:opacity-50"
                  >
                    {loading ? "Running…" : "Run query"}
                  </button>
                  {error && (
                    <div className="text-xs text-red-400 text-right">
                      {error}
                    </div>
                  )}
                </div>
              </form>
            </div>

            {sql && (
              <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-3">
                <div className="text-xs font-medium text-slate-300 mb-1">
                  Generated SQL
                </div>
                <pre className="w-full rounded-md bg-slate-950/80 p-2 text-xs overflow-x-auto">
                  {sql}
                </pre>
              </div>
            )}

            {results.length > 0 && (
              <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-3">
                <div className="text-xs font-medium text-slate-300 mb-2">
                  Results ({results.length})
                </div>
                <div className="overflow-x-auto rounded-md border border-slate-800">
                  <table className="min-w-full text-xs">
                    <thead className="bg-slate-900">
                      <tr>
                        {columns.map((col) => (
                          <th
                            key={col}
                            className="px-3 py-2 text-left font-medium text-slate-300"
                          >
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {results.map((row, idx) => (
                        <tr
                          key={idx}
                          className="border-t border-slate-800 odd:bg-slate-950/40"
                        >
                          {columns.map((col) => (
                            <td key={col} className="px-3 py-2">
                              {String(row[col])}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </section>

          {/* Right: history */}
          <section className="rounded-xl border border-slate-800 bg-slate-900/70 p-4 space-y-3">
            <div className="flex items-center justify-between">
              <div className="text-sm font-medium text-slate-200">
                Recent queries
              </div>
              <button
                type="button"
                onClick={refreshHistory}
                className="text-xs text-slate-400 hover:text-slate-200"
              >
                Refresh
              </button>
            </div>

            {history.length === 0 ? (
              <p className="text-xs text-slate-500">
                No history yet. Run a query to see it here.
              </p>
            ) : (
              <div className="overflow-x-auto rounded-md border border-slate-800">
                <table className="min-w-full text-[11px]">
                  <thead className="bg-slate-900">
                    <tr>
                      <th className="px-3 py-2 text-left">Time</th>
                      <th className="px-3 py-2 text-left">Data source</th>
                      <th className="px-3 py-2 text-left">Profile</th>
                      <th className="px-3 py-2 text-left">Status</th>
                      <th className="px-3 py-2 text-left">NL query</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.map((h, idx) => (
                      <tr
                        key={idx}
                        className="border-t border-slate-800 odd:bg-slate-950/40"
                      >
                        <td className="px-3 py-2 whitespace-nowrap">
                          {h.timestamp}
                        </td>
                        <td className="px-3 py-2">{h.data_source}</td>
                        <td className="px-3 py-2">{h.profile}</td>
                        <td className="px-3 py-2">{h.status}</td>
                        <td className="px-3 py-2 max-w-xs truncate">
                          {h.nl_query}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </div>
      </div>
    </main>
  );
}
