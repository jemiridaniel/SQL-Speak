// web/src/app/test-api/page.tsx
"use client";

import { useState, useEffect } from "react";
import { useMsal } from "@azure/msal-react";
import { apiScope } from "@/lib/msalConfig";
import {
  InteractionStatus,
  InteractionRequiredAuthError,
} from "@azure/msal-browser";

export default function TestApiPage() {
  const { instance, accounts, inProgress } = useMsal();
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  const ensureLogin = async () => {
    const existing = instance.getActiveAccount() ?? accounts[0];
    if (existing) {
      return existing;
    }

    // Use redirect instead of popup
    await instance.loginRedirect({
      scopes: [apiScope],
      redirectUri: "http://localhost:3000/test-api",
    });

    // After redirect back, MSAL will rehydrate accounts and this code will run again
    throw new Error("Redirecting for login...");
  };

  const callBackend = async () => {
    try {
      if (inProgress !== InteractionStatus.None) {
        setError("Auth in progress, please wait...");
        return;
      }

      setError(null);
      setResult(null);

      const account = await ensureLogin();

      let tokenResult;
      try {
        tokenResult = await instance.acquireTokenSilent({
          scopes: [apiScope],
          account,
        });
      } catch (silentErr: any) {
        if (silentErr instanceof InteractionRequiredAuthError) {
          await instance.loginRedirect({
            scopes: [apiScope],
            redirectUri: "http://localhost:3000/test-api",
          });
          throw new Error("Redirecting for consent...");
        } else {
          throw silentErr;
        }
      }

      const accessToken = tokenResult.accessToken;

      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/me`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      const data = await res.json();
      if (!res.ok) {
        setError(`${res.status} ${JSON.stringify(data)}`);
      } else {
        setResult(data);
      }
    } catch (err: any) {
      if (err.message?.startsWith("Redirecting")) {
        // Ignore pseudo-error caused by redirect
        return;
      }
      console.error(err);
      setError(err.message ?? String(err));
    }
  };

  if (!isClient) {
    return <div>Loading…</div>;
  }

  return (
    <div>
      <h1>Test /me via MSAL</h1>

      <div>Auth status: {inProgress}</div>
      <div>
        Accounts:{" "}
        {accounts.length > 0
          ? accounts.map((a) => a.username).join(", ")
          : "none"}
      </div>

      <button onClick={callBackend}>Login & Call /me</button>
      {error && <pre>error: {error}</pre>}
      {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  );
}
