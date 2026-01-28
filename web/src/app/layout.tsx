// app/layout.tsx
import "./globals.css";
import type { ReactNode } from "react";
import { AppProviders } from "./providers";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
