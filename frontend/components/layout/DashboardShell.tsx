"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";
import type { StoreApiRow } from "@/lib/types";

export function DashboardShell({
  initialStores,
  children,
}: {
  initialStores: StoreApiRow[];
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const router = useRouter();
  const storeParam = searchParams.get("store");
  const parsed = storeParam ? parseInt(storeParam, 10) : NaN;
  const storeId = Number.isFinite(parsed)
    ? parsed
    : (initialStores[0]?.id ?? 1);

  const setStoreId = (id: number) => {
    const q = new URLSearchParams(searchParams.toString());
    q.set("store", String(id));
    router.push(`${pathname}?${q.toString()}`);
  };

  return (
    <div className="flex min-h-screen bg-[var(--rp-bg)] text-[var(--rp-fg)]">
      <Sidebar pathname={pathname} />
      <div className="flex min-w-0 flex-1 flex-col">
        <Header
          stores={initialStores}
          storeId={Number.isFinite(storeId) ? storeId : initialStores[0]?.id ?? 1}
          onStoreChange={setStoreId}
        />
        <main className="flex-1 overflow-auto p-4 md:p-6">{children}</main>
      </div>
    </div>
  );
}
