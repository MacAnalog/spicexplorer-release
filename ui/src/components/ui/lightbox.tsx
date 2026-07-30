"use client";
import { useEffect, useState } from "react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Full-screen image lightbox — for the library's schematic SVGs / template PNGs,
 * whose in-page thumbnails are too small to read. Click the backdrop or press
 * Esc to close; click the image to toggle fit ⇄ 2× (panning via scroll). SVGs
 * scale losslessly, so the zoomed view is readable.
 */
export function Lightbox({
  src,
  alt,
  caption,
  onClose,
}: {
  src: string;
  alt: string;
  caption?: string;
  onClose: () => void;
}) {
  const [zoomed, setZoomed] = useState(false);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    // lock the page scroll behind the overlay
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = prev;
    };
  }, [onClose]);

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label={alt}
      className="fixed inset-0 z-100 flex flex-col bg-black/75 backdrop-blur-[2px]"
      onClick={onClose}
    >
      <div className="flex shrink-0 items-center gap-3 px-4 py-2.5">
        {caption && (
          <span className="min-w-0 truncate font-mono text-[11px] text-white/80">{caption}</span>
        )}
        <div className="flex-1" />
        <span className="font-mono text-[10px] text-white/50">
          {zoomed ? "click image: fit" : "click image: zoom"} · Esc closes
        </span>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close"
          className="rounded-md p-1 text-white/80 transition hover:bg-white/10 hover:text-white"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
      <div
        className={cn(
          "min-h-0 flex-1 p-4 pt-0",
          zoomed ? "overflow-auto" : "flex items-center justify-center overflow-hidden",
        )}
      >
        {/* dynamic API-streamed SVG/PNG; a plain <img> (next/image can't optimize SVG) */}
        <img
          src={src}
          alt={alt}
          onClick={(e) => {
            e.stopPropagation();
            setZoomed((z) => !z);
          }}
          className={cn(
            "rounded-md bg-white",
            zoomed
              ? "mx-auto w-[200%] max-w-none cursor-zoom-out"
              : "max-h-full max-w-full cursor-zoom-in object-contain",
          )}
        />
      </div>
    </div>
  );
}
