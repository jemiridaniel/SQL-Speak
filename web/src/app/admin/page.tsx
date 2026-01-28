"use client";

import { useState } from "react";

type HistoryItem = {
  timestamp: string;
  data_source: string;
  profile: string;
  nl_query: string;
  sql: string;
  status: string;
  row_count: number;
};

export default function AdminPage() {
  const [userId, setUserId] = useState("daniel");
  const [statusFilter, setStatusFilter] = useState<"all" | "success" | "error">(
    "all"
  );
  const [timeFilter, setTimeFilter] = useState("");
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadHistory(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await fetch("http://127.0.0.1:8000/history", {
        headers: {
          "X-User-Id": userId,
          "X-User-Name": userId,
        },
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Request failed with ${res.status}`);
      }

      let items: HistoryItem[] = await res.json();

      if (statusFilter !== "all") {
        items = items.filter((h) => h.status === statusFilter);
      }
      if (timeFilter.trim()) {
        items = items.filter((h) =>
          h.timestamp.includes(timeFilter.trim())
        );
      }

      setHistory(items);
    } catch (err: any) {
      setError(err.message || "Unknown error");
      setHistory([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center py-10">
      <div className="w-full max-w-5xl space-y-6 px-4">
        <h1 className="text-2xl font-semibold">
          SQL-Speak Admin – Query History
        </h1>

        <form onSubmit={loadHistory} className="flex flex-wrap gap-4 text-sm">
          <div>
            <label className="block mb-1">User ID</label>
            <input
              className="rounded-md border border-slate-700 bg-slate-900 p-1 text-sm"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
            />
          </div>

          <div>
            <label className="block mb-1">Status</label>
            <select
              className="rounded-md border border-slate-700 bg-slate-900 p-1 text-sm"
              value={statusFilter}
              onChange={(e) =>
                setStatusFilter(e.target.value as "all" | "success" | "error")
              }
            >
              <option value="all">All</option>
              <option value="success">Success</option>
              <option value="error">Error</option>
            </select>
          </div>

          <div>
            <label className="block mb-1">Time contains</label>
            <input
              placeholder="2026-01-28T11:0"
              className="rounded-md border border-slate-700 bg-slate-900 p-1 text-sm"
              value={timeFilter}
              onChange={(e) => setTimeFilter(e.target.value)}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="self-end px-4 py-2 rounded-md bg-blue-600 text-sm font-medium disabled:opacity-50"
          >
            {loading ? "Loading..." : "Load history"}
          </button>
        </form>

        {error && (
          <div className="text-sm text-red-400">
            Error: {error}
          </div>
        )}

        {history.length > 0 && (
          <div className="space-y-2">
            <div className="text-sm font-medium">
              Results ({history.length})
            </div>
            <div className="overflow-x-auto rounded-md border border-slate-700">
              <table className="min-w-full text-xs">
                <thead className="bg-slate-900">
                  <tr>
                    <th className="px-3 py-2 text-left">Time</th>
                    <th className="px-3 py-2 text-left">User</th>
                    <th className="px-3 py-2 text-left">Data source</th>
                    <th className="px-3 py-2 text-left">Profile</th>
                    <th className="px-3 py-2 text-left">Status</th>
                    <th className="px-3 py-2 text-left">Rows</th>
                    <th className="px-3 py-2 text-left">NL query</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((h, idx) => (
                    <tr key={idx} className="border-t border-slate-800">
                      <td className="px-3 py-2">{h.timestamp}</td>
                      <td className="px-3 py-2">{userId}</td>
                      <td className="px-3 py-2">{h.data_source}</td>
                      <td className="px-3 py-2">{h.profile}</td>
                      <td className="px-3 py-2">{h.status}</td>
                      <td className="px-3 py-2">{h.row_count}</td>
                      <td className="px-3 py-2">{h.nl_query}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {history.length === 0 && !loading && !error && (
          <div className="text-sm text-slate-400">
            No history yet for this filter.
          </div>
        )}
      </div>
    </main>
  );
}
