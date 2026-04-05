export function KPICard({
  title,
  value,
  subtitle,
  accent = "default",
}: {
  title: string;
  value: string | number;
  subtitle?: string;
  accent?: "default" | "amber" | "emerald" | "rose";
}) {
  const ring =
    accent === "amber"
      ? "border-amber-500/20 shadow-[0_0_0_1px_rgba(245,158,11,0.15)]"
      : accent === "emerald"
        ? "border-emerald-500/20 shadow-[0_0_0_1px_rgba(16,185,129,0.15)]"
        : accent === "rose"
          ? "border-rose-500/20 shadow-[0_0_0_1px_rgba(244,63,94,0.15)]"
          : "border-[var(--rp-border)]";

  return (
    <div
      className={`rounded-xl border bg-[var(--rp-panel)] p-4 ${ring}`}
    >
      <p className="text-xs font-medium uppercase tracking-wide text-[var(--rp-muted)]">
        {title}
      </p>
      <p className="mt-2 text-2xl font-semibold tabular-nums tracking-tight text-[var(--rp-fg)]">
        {value}
      </p>
      {subtitle ? (
        <p className="mt-1 text-xs text-[var(--rp-muted)]">{subtitle}</p>
      ) : null}
    </div>
  );
}
