"use client";

import { useCallback, useState } from "react";
import { Upload } from "lucide-react";

export function ImageUploader({
  disabled,
  onFile,
}: {
  disabled?: boolean;
  onFile: (file: File) => void;
}) {
  const [drag, setDrag] = useState(false);

  const handleFiles = useCallback(
    (files: FileList | null) => {
      const f = files?.[0];
      if (!f || !f.type.startsWith("image/")) return;
      onFile(f);
    },
    [onFile]
  );

  return (
    <label
      className={`flex min-h-[160px] cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-4 py-10 transition-colors ${
        drag
          ? "border-[var(--rp-accent)] bg-[var(--rp-accent)]/10"
          : "border-[var(--rp-border)] bg-[var(--rp-panel)]/60 hover:border-[var(--rp-muted)]"
      } ${disabled ? "pointer-events-none opacity-50" : ""}`}
      onDragEnter={(e) => {
        e.preventDefault();
        setDrag(true);
      }}
      onDragLeave={(e) => {
        e.preventDefault();
        setDrag(false);
      }}
      onDragOver={(e) => e.preventDefault()}
      onDrop={(e) => {
        e.preventDefault();
        setDrag(false);
        handleFiles(e.dataTransfer.files);
      }}
    >
      <Upload className="mb-2 h-10 w-10 text-[var(--rp-muted)]" aria-hidden />
      <span className="text-sm font-medium text-[var(--rp-fg)]">
        Drop a shelf photo here, or click to browse
      </span>
      <span className="mt-1 text-xs text-[var(--rp-muted)]">PNG, JPG · up to 10MB</span>
      <input
        type="file"
        accept="image/*"
        className="sr-only"
        disabled={disabled}
        onChange={(e) => handleFiles(e.target.files)}
      />
    </label>
  );
}
