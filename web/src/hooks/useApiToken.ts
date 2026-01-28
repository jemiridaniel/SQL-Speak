// hooks/useApiToken.ts
import { useMsal } from "@azure/msal-react";
import { apiScope } from "@/lib/msalConfig";
import { InteractionRequiredAuthError } from "@azure/msal-browser";

export function useApiToken() {
  const { instance, accounts } = useMsal();

  async function ensureToken(): Promise<string> {
    const account = instance.getActiveAccount() ?? accounts[0];

    if (!account) {
      // Full-page redirect sign-in
      await instance.loginRedirect({
        scopes: [apiScope],
        redirectUri: "http://localhost:3000/", // come back to console
      });
      // This function won't return on first call because of redirect
      throw new Error("Redirecting to sign-in");
    }

    try {
      const result = await instance.acquireTokenSilent({
        scopes: [apiScope],
        account,
      });
      return result.accessToken;
    } catch (err: any) {
      if (err instanceof InteractionRequiredAuthError) {
        await instance.loginRedirect({
          scopes: [apiScope],
          redirectUri: "http://localhost:3000/",
        });
        throw new Error("Redirecting to sign-in");
      }
      throw err;
    }
  }

  return { ensureToken, accounts };
}
