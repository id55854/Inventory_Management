"use client";

import type { DetectedProduct } from "@/lib/types";

function boxClass(confidence: number, active: boolean, dim: boolean): string {
  let border = "border-amber-400/90";
  if (confidence >= 0.85) border = "border-emerald-400/95";
  else if (confidence >= 0.65) border = "border-amber-400/85";
  else border = "border-orange-400/90";
  const glow = active ? "ring-2 ring-[var(--rp-accent)] ring-offset-2 ring-offset-[var(--rp-bg)]" : "";
  const opacity = dim ? "opacity-35" : "opacity-100";
  return `absolute rounded-sm border-2 ${border} bg-black/15 transition-all ${glow} ${opacity}`;
}

export function ShelfAnnotation({
  imageSrc,
  detections,
  showOverlay,
  hoveredIndex,
  selectedIndex,
  onHover,
  onSelectFromImage,
  listRefs,
  boxRefs,
}: {
  imageSrc: string;
  detections: DetectedProduct[];
  showOverlay: boolean;
  hoveredIndex: number | null;
  selectedIndex: number | null;
  onHover: (i: number | null) => void;
  onSelectFromImage: (i: number) => void;
  listRefs?: React.MutableRefObject<(HTMLLIElement | null)[]>;
  boxRefs: React.MutableRefObject<(HTMLButtonElement | null)[]>;
}) {
  return (
    <div className="relative w-full overflow-hidden rounded-xl border border-[var(--rp-border)] bg-[var(--rp-panel)]">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={imageSrc}
        alt="Shelf scan"
        className="block h-auto w-full max-h-[min(70vh,560px)] object-contain"
        draggable={false}
      />
      {showOverlay
        ? detections.map((d, i) => {
            const { x, y, w, h } = d.boundingBox;
            const active = selectedIndex === i || hoveredIndex === i;
            const dim =
              hoveredIndex !== null
                ? hoveredIndex !== i
                : selectedIndex !== null && selectedIndex !== i;
            return (
              <button
                key={`${d.productName}-${i}`}
                ref={(el) => {
                  boxRefs.current[i] = el;
                }}
                type="button"
                title={d.productName}
                className={`${boxClass(d.confidence, active, dim)} cursor-pointer`}
                style={{
                  left: `${x * 100}%`,
                  top: `${y * 100}%`,
                  width: `${w * 100}%`,
                  height: `${h * 100}%`,
                }}
                onMouseEnter={() => onHover(i)}
                onMouseLeave={() => onHover(null)}
                onClick={() => {
                  onSelectFromImage(i);
                  listRefs?.current[i]?.scrollIntoView({ behavior: "smooth", block: "nearest" });
                }}
              />
            );
          })
        : null}
    </div>
  );
}
