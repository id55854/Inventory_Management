import { Sparkles } from "lucide-react";

export function AiInsightCard({ text }: { text: string }) {
  return (
    <div className="rounded-xl border border-[var(--rp-border)] bg-gradient-to-br from-[var(--rp-panel)] to-[var(--rp-bg)] p-4">
      <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-[var(--rp-accent)]">
        <Sparkles className="h-4 w-4" aria-hidden />
        AI insight (Gemini)
      </div>
      <p className="text-sm leading-relaxed text-[var(--rp-muted)]">{text}</p>
    </div>
  );
}
