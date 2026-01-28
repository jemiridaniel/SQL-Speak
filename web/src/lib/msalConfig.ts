// web/src/lib/msalConfig.ts
import type { Configuration } from "@azure/msal-browser";

export const msalConfig: Configuration = {
  auth: {
    clientId: process.env.NEXT_PUBLIC_AZURE_CLIENT_ID!,
    authority: `https://login.microsoftonline.com/${process.env.NEXT_PUBLIC_AZURE_TENANT_ID}`,
    redirectUri: "http://localhost:3000/",
  },
  system: {
    loggerOptions: {
      logLevel: 3,
    },
  },
};

export const apiScope =
  process.env.NEXT_PUBLIC_AZURE_API_SCOPE!; // api://.../user_impersonation
