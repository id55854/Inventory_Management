import Link from "next/link";
import {
  LayoutDashboard,
  Store,
  Camera,
  Bell,
  LineChart,
  Trash2,
} from "lucide-react";

const items = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/stores", label: "Stores", icon: Store },
  { href: "/scan", label: "Scan", icon: Camera },
  { href: "/alerts", label: "Alerts", icon: Bell },
  { href: "/analytics", label: "Trends", icon: LineChart },
  { href: "/analytics/waste", label: "Waste", icon: Trash2 },
];

export function Sidebar({ pathname }: { pathname: string }) {
  return (
    <aside className="flex w-14 shrink-0 flex-col border-r border-[var(--rp-border)] bg-[var(--rp-sidebar)] md:w-52">
      <div className="p-2 md:p-4">
        <p className="hidden text-xs font-medium uppercase tracking-wider text-[var(--rp-muted)] md:block">
          Navigation
        </p>
        <nav className="mt-3 flex flex-col gap-0.5" aria-label="Main">
          {items.map(({ href, label, icon: Icon }) => {
            const active = pathname === href || (href !== "/" && pathname.startsWith(href));
            return (
              <Link
                key={href}
                href={href}
                title={label}
                className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors ${
                  active
                    ? "bg-[var(--rp-panel)] text-[var(--rp-accent)]"
                    : "text-[var(--rp-muted)] hover:bg-[var(--rp-panel)] hover:text-[var(--rp-fg)]"
                }`}
              >
                <Icon className="h-4 w-4 shrink-0 opacity-80" aria-hidden />
                <span className="hidden md:inline">{label}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </aside>
  );
}
