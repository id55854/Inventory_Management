"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Loader2, Eye, EyeOff } from "lucide-react";
import { ImageUploader } from "./ImageUploader";
import { ShelfAnnotation } from "./ShelfAnnotation";
import { AnalysisResults } from "./AnalysisResults";
import {
  analyzeShelfDeep,
  fileToBase64DataUrl,
  mapAnalysisToResult,
  uploadShelfScan,
  type AnalyzeShelfApiResponse,
  type ShelfAnalysisApi,
} from "@/lib/scan-api";
import type { StoreApiRow } from "@/lib/types";
import { apiGet } from "@/lib/api";

export function ScanWorkspace({ initialStores }: { initialStores: StoreApiRow[] }) {
  const searchParams = useSearchParams();
  const storeParam = searchParams.get("store");
  const parsed = storeParam ? parseInt(storeParam, 10) : NaN;
  const defaultStore = initialStores[0]?.id ?? 1;
  const storeFromUrl = Number.isFinite(parsed) ? parsed : defaultStore;

  const stores = initialStores;
  const [storeId, setStoreId] = useState(storeFromUrl);
  const [aisleId, setAisleId] = useState<number | "">("");
  const [aisles, setAisles] = useState<{ id: number; name: string | null }[]>([]);

  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [raw, setRaw] = useState<ShelfAnalysisApi | null>(null);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [showOverlay, setShowOverlay] = useState(true);
  const [reportLoading, setReportLoading] = useState(false);
  const [report, setReport] = useState<AnalyzeShelfApiResponse | null>(null);

  const listRefs = useRef<(HTMLLIElement | null)[]>([]);
  const boxRefs = useRef<(HTMLButtonElement | null)[]>([]);

  useEffect(() => {
    setStoreId(storeFromUrl);
  }, [storeFromUrl]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const rows = await apiGet<
          { id: number; name: string | null; aisle_number: number | null }[]
        >(`/stores/${storeId}/aisles`);
        if (!cancelled) {
          setAisles(rows.map((a) => ({ id: a.id, name: a.name })));
          setAisleId("");
        }
      } catch {
        if (!cancelled) setAisles([]);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [storeId]);

  const revokePreview = useCallback(() => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
  }, [previewUrl]);

  const onPickFile = useCallback(
    (f: File) => {
      revokePreview();
      setFile(f);
      setPreviewUrl(URL.createObjectURL(f));
      setRaw(null);
      setError(null);
      setReport(null);
      setSelectedIndex(null);
      setHoveredIndex(null);
    },
    [revokePreview]
  );

  useEffect(() => () => revokePreview(), [revokePreview]);

  const runAnalysis = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setReport(null);
    try {
      const res = await uploadShelfScan(
        file,
        storeId,
        aisleId === "" ? null : Number(aisleId)
      );
      setRaw(res);
      setSelectedIndex(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  const selectFromList = (i: number) => {
    setSelectedIndex(i);
    boxRefs.current[i]?.scrollIntoView({
      behavior: "smooth",
      block: "center",
      inline: "nearest",
    });
  };

  const selectFromImage = (i: number) => {
    setSelectedIndex(i);
    listRefs.current[i]?.scrollIntoView({
      behavior: "smooth",
      block: "nearest",
    });
  };

  const onGenerateReport = async () => {
    if (!file) return;
    setReportLoading(true);
    try {
      const dataUrl = await fileToBase64DataUrl(file);
      const base64 = dataUrl.includes(",") ? dataUrl.split(",")[1]! : dataUrl;
      const r = await analyzeShelfDeep(
        base64,
        `store ${storeId}${aisleId !== "" ? `, aisle ${aisleId}` : ""}`
      );
      setReport(r);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Report failed");
    } finally {
      setReportLoading(false);
    }
  };

  const result = raw ? mapAnalysisToResult(raw) : null;

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div>
        <h1 className="text-xl font-semibold tracking-tight text-[var(--rp-fg)]">Shelf scan</h1>
        <p className="mt-1 text-sm text-[var(--rp-muted)]">
          Upload a shelf photo for AI detection, occupancy, and natural-language insight.
        </p>
      </div>

      {stores.length === 0 ? (
        <div className="rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-100">
          No stores loaded. Start the FastAPI backend and set{" "}
          <code className="rounded bg-[var(--rp-bg)] px-1">NEXT_PUBLIC_API_URL</code> if needed.
        </div>
      ) : null}

      <div className="flex flex-wrap items-end gap-4 rounded-xl border border-[var(--rp-border)] bg-[var(--rp-panel)] p-4">
        <label className="flex flex-col gap-1 text-xs text-[var(--rp-muted)]">
          Store
          <select
            className="rounded-md border border-[var(--rp-border)] bg-[var(--rp-bg)] px-3 py-2 text-sm text-[var(--rp-fg)]"
            value={storeId}
            onChange={(e) => setStoreId(Number(e.target.value))}
          >
            {stores.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-xs text-[var(--rp-muted)]">
          Aisle (optional)
          <select
            className="min-w-[12rem] rounded-md border border-[var(--rp-border)] bg-[var(--rp-bg)] px-3 py-2 text-sm text-[var(--rp-fg)]"
            value={aisleId === "" ? "" : String(aisleId)}
            onChange={(e) =>
              setAisleId(e.target.value === "" ? "" : Number(e.target.value))
            }
          >
            <option value="">—</option>
            {aisles.map((a) => (
              <option key={a.id} value={a.id}>
                {a.name || `Aisle ${a.id}`}
              </option>
            ))}
          </select>
        </label>
        <button
          type="button"
          onClick={runAnalysis}
          disabled={!file || loading}
          className="rounded-lg bg-[var(--rp-accent)] px-4 py-2 text-sm font-medium text-[var(--rp-bg)] hover:opacity-90 disabled:opacity-40"
        >
          {loading ? (
            <span className="inline-flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
              Analyzing shelf…
            </span>
          ) : (
            "Analyze shelf"
          )}
        </button>
      </div>

      {error ? (
        <div className="rounded-lg border border-rose-500/40 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
          {error}
        </div>
      ) : null}

      <div className="grid gap-6 lg:grid-cols-[1fr_1fr]">
        <div className="space-y-3">
          {!previewUrl ? (
            <ImageUploader disabled={loading} onFile={onPickFile} />
          ) : (
            <>
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="truncate text-xs text-[var(--rp-muted)]">{file?.name}</p>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setShowOverlay((v) => !v)}
                    className="inline-flex items-center gap-1.5 rounded-md border border-[var(--rp-border)] px-2 py-1 text-xs text-[var(--rp-muted)] hover:bg-[var(--rp-bg)]"
                  >
                    {showOverlay ? (
                      <Eye className="h-3.5 w-3.5" aria-hidden />
                    ) : (
                      <EyeOff className="h-3.5 w-3.5" aria-hidden />
                    )}
                    {showOverlay ? "Hide" : "Show"} detections
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      revokePreview();
                      setFile(null);
                      setPreviewUrl(null);
                      setRaw(null);
                      setReport(null);
                    }}
                    className="text-xs text-[var(--rp-accent)] hover:underline"
                  >
                    Clear image
                  </button>
                </div>
              </div>
              {result && previewUrl ? (
                <ShelfAnnotation
                  imageSrc={previewUrl}
                  detections={result.detections}
                  showOverlay={showOverlay}
                  hoveredIndex={hoveredIndex}
                  selectedIndex={selectedIndex}
                  onHover={setHoveredIndex}
                  onSelectFromImage={selectFromImage}
                  listRefs={listRefs}
                  boxRefs={boxRefs}
                />
              ) : (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={previewUrl}
                  alt="Preview"
                  className="w-full max-h-[min(70vh,560px)] rounded-xl border border-[var(--rp-border)] object-contain"
                />
              )}
            </>
          )}
        </div>

        <div className="min-h-[200px]">
          {loading && !result ? (
            <div className="flex h-64 flex-col items-center justify-center rounded-xl border border-dashed border-[var(--rp-border)] bg-[var(--rp-panel)]/50 text-[var(--rp-muted)]">
              <Loader2 className="mb-3 h-10 w-10 animate-spin text-[var(--rp-accent)]" />
              <p className="text-sm font-medium">Analyzing shelf…</p>
              <p className="mt-1 text-xs">Running detection and insight pipeline</p>
            </div>
          ) : result ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-2 rounded-xl border border-[var(--rp-border)] bg-[var(--rp-panel)] p-3 text-sm sm:grid-cols-4">
                <div>
                  <p className="text-[10px] uppercase text-[var(--rp-muted)]">Occupancy</p>
                  <p className="font-semibold tabular-nums text-[var(--rp-fg)]">
                    {result.overallOccupancy.toFixed(1)}%
                  </p>
                </div>
                <div>
                  <p className="text-[10px] uppercase text-[var(--rp-muted)]">Products</p>
                  <p className="font-semibold tabular-nums text-[var(--rp-fg)]">
                    {result.productsDetected}
                  </p>
                </div>
                <div>
                  <p className="text-[10px] uppercase text-[var(--rp-muted)]">Empty slots</p>
                  <p className="font-semibold tabular-nums text-[var(--rp-fg)]">
                    {result.emptySlots}
                  </p>
                </div>
                <div>
                  <p className="text-[10px] uppercase text-[var(--rp-muted)]">Time</p>
                  <p className="font-semibold tabular-nums text-[var(--rp-fg)]">
                    {result.processingTimeMs}ms
                  </p>
                </div>
              </div>
              <AnalysisResults
                result={result}
                report={report}
                reportLoading={reportLoading}
                onGenerateReport={onGenerateReport}
                selectedIndex={selectedIndex}
                hoveredIndex={hoveredIndex}
                onSelectProduct={selectFromList}
                onHoverProduct={setHoveredIndex}
                listRefs={listRefs}
              />
            </div>
          ) : (
            <div className="rounded-xl border border-dashed border-[var(--rp-border)] bg-[var(--rp-panel)]/40 p-8 text-center text-sm text-[var(--rp-muted)]">
              Choose an image and tap <strong className="text-[var(--rp-fg)]">Analyze shelf</strong>{" "}
              to see detections and overlays.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
