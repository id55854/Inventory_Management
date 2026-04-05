import type { Metadata } from "next";
import "./globals.css";
import { DashboardShell } from "@/components/layout/DashboardShell";
import { apiGet } from "@/lib/api";
import type { StoreApiRow } from "@/lib/types";

export const metadata: Metadata = {
  title: "RetailPulse",
  description: "Shelf & inventory intelligence",
};

async function loadStores(): Promise<StoreApiRow[]> {
  try {
    return await apiGet<StoreApiRow[]>("/stores");
  } catch {
    return [];
  }
}

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const stores = await loadStores();

  return (
    <html lang="en">
      <body className="min-h-screen antialiased">
        <DashboardShell initialStores={stores}>{children}</DashboardShell>
      </body>
    </html>
  );
}
