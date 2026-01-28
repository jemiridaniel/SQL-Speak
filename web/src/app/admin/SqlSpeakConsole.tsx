// web/src/app/admin/SqlSpeakConsole.tsx
"use client";

import { useState } from "react";
import { useMsal } from "@azure/msal-react";
import { apiScope } from "@/lib/msalConfig";

type QueryResponse = {
  sql: string;
  results: any[];
  meta: any;
};

export function SqlSpeakConsole() {
  const { instance, accounts } = useMsal();
  const [dataSource, setDataSource] = useState("sqlite-devprod-readonly");
  const [profile, setProfile] = useState("sqlite-dev");
  const [nlQuery, setNlQuery] = useState("");
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const isSignedIn = accounts.length > 0;

  const runQuery = async () => {
    try {
      setError(null);
      setResponse(null);
      setLoading(true);

      if (!isSignedIn) {
        setError("Please sign in first.");
        return;
      }

      const account = instance.getActiveAccount() ?? accounts[0];
      const tokenResult = await instance.acquireTokenSilent({
        scopes: [apiScope],
        account,
      });

      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/query`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${tokenResult.accessToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          data_source: dataSource,
          profile,
          query: nlQuery,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        setError(`${res.status} ${JSON.stringify(data)}`);
      } else {
        setResponse(data);
      }
    } catch (e: any) {
      console.error(e);
      setError(e.message ?? String(e));
    } finally {
      setLoading(false);
    }
  };

  if (!isSignedIn) {
    return <div>Not signed in. Go to /test-api and log in to start querying.</div>;
  }

  return (
    <div>
      <div>Signed in as {accounts[0].username}</div>

      <div>
        <label>
          Data source:
          <select
            value={dataSource}
            onChange={(e) => setDataSource(e.target.value)}
          >
            <option value="sqlite-devprod-readonly">sqlite-devprod-readonly</option>
            {/* add other data sources from your config if needed */}
          </select>
        </label>
      </div>

      <div>
        <label>
          Profile:
          <select
            value={profile}
            onChange={(e) => setProfile(e.target.value)}
          >
            <option value="sqlite-dev">sqlite-dev</option>
            {/* add other profiles */}
          </select>
        </label>
      </div>

      <textarea
        rows={4}
        cols={40}
        value={nlQuery}
        onChange={(e) => setNlQuery(e.target.value)}
        placeholder="Describe the query you want to run…"
      />

      <div>
        <button onClick={runQuery} disabled={loading || !nlQuery}>
          {loading ? "Running…" : "Run query"}
        </button>
      </div>

      {error && <pre>error: {error}</pre>}

      {response && (
        <div>
          <h3>Generated SQL</h3>
          <pre>{response.sql}</pre>

          <h3>Results</h3>
          <pre>{JSON.stringify(response.results, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
