import { apiUrl } from "./api";
import type { DetectedProduct, ShelfScanResult } from "./types";

/** Raw FastAPI `ShelfAnalysisResponse` (snake_case JSON). */
export interface ShelfAnalysisApi {
  scan_id: number;
  timestamp: string;
  overall_occupancy: number;
  products_detected: number;
  empty_slots: number;
  detections: {
    product_name: string;
    sku?: string | null;
    bounding_box: { x: number; y: number; w: number; h: number };
    confidence: number;
    quantity_estimated: number;
    shelf_position: number;
  }[];
  issues: { type?: string; severity?: string; product?: string; description?: string }[];
  gemini_insight: string;
  processing_time_ms: number;
  confidence_avg: number;
}

export function mapAnalysisToResult(a: ShelfAnalysisApi): ShelfScanResult {
  const detections: DetectedProduct[] = a.detections.map((d) => ({
    productName: d.product_name,
    sku: d.sku ?? undefined,
    boundingBox: d.bounding_box,
    confidence: d.confidence,
    quantityEstimated: d.quantity_estimated,
    shelfPosition: d.shelf_position,
  }));
  const issues = a.issues.map((i) => {
    const product = "product" in i && typeof (i as { product?: string }).product === "string"
      ? (i as { product: string }).product
      : undefined;
    return {
      type: String(i.type ?? "issue"),
      severity: String(i.severity ?? "medium"),
      description: i.description ?? (product ? `Product: ${product}` : undefined),
    };
  });
  return {
    scanId: a.scan_id,
    timestamp: a.timestamp,
    overallOccupancy: a.overall_occupancy,
    productsDetected: a.products_detected,
    emptySlots: a.empty_slots,
    detections,
    issues,
    geminiInsight: a.gemini_insight,
    processingTimeMs: a.processing_time_ms,
  };
}

export async function uploadShelfScan(
  file: File,
  storeId: number,
  aisleId?: number | null
): Promise<ShelfAnalysisApi> {
  const fd = new FormData();
  fd.append("image", file);
  fd.append("store_id", String(storeId));
  if (aisleId != null && aisleId > 0) {
    fd.append("aisle_id", String(aisleId));
  }

  const res = await fetch(apiUrl("/scans/upload"), {
    method: "POST",
    body: fd,
  });
  if (!res.ok) {
    const t = await res.text();
    throw new Error(t || `${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<ShelfAnalysisApi>;
}

export interface AnalyzeShelfApiResponse {
  summary: string;
  issues: { type?: string; severity?: string; region?: string }[];
  recommendations: string[];
}

export async function analyzeShelfDeep(
  imageBase64: string,
  context?: string
): Promise<AnalyzeShelfApiResponse> {
  const res = await fetch(apiUrl("/insights/analyze-shelf"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image_base64: imageBase64, context: context ?? null }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<AnalyzeShelfApiResponse>;
}

export function fileToBase64DataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const r = new FileReader();
    r.onload = () => resolve(String(r.result));
    r.onerror = () => reject(new Error("read failed"));
    r.readAsDataURL(file);
  });
}
