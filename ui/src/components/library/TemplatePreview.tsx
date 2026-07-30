"use client";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { libraryTemplateImageUrl } from "@/lib/api";
import { Lightbox } from "@/components/ui/lightbox";
import { Hatch } from "./Hatch";

/**
 * Functional-template preview — renders the template's committed net-colour-coded PNG
 * render (streamed from `/api/library/templates/{id}/image`), falling back to the hatch
 * placeholder when no render exists (`hasImage` false) or the fetch fails (`onError`).
 *
 * `failed` is per-instance: the browse grid gives each thumbnail its own keyed instance,
 * and the single detail preview should be given `key={id}` by the caller so switching the
 * selected template remounts it (resetting a prior failure).
 */
export function TemplatePreview({
  id,
  hasImage,
  heightClass = "h-[62px]",
  className,
  label,
  enlargeable = false,
}: {
  id: string;
  hasImage: boolean;
  heightClass?: string;
  className?: string;
  label?: React.ReactNode;
  /** Click opens the full-screen lightbox. Leave off inside selectable cards
   *  (their click means "select this template", not "zoom the image"). */
  enlargeable?: boolean;
}) {
  const [failed, setFailed] = useState(false);
  const [enlarged, setEnlarged] = useState(false);
  if (!hasImage || failed) {
    return <Hatch label={label ?? id} heightClass={heightClass} className={className} />;
  }
  const img = (
    /* dynamic external PNG streamed from the API; a plain <img> keeps it simple */
    <img
      src={libraryTemplateImageUrl(id)}
      alt={`${id} schematic`}
      onError={() => setFailed(true)}
      className="max-h-full max-w-full object-contain"
    />
  );
  const frame = cn(
    "flex items-center justify-center overflow-hidden rounded-md border border-hairline bg-white",
    heightClass,
    className,
  );
  if (!enlargeable) return <div className={frame}>{img}</div>;
  return (
    <>
      <button
        type="button"
        onClick={() => setEnlarged(true)}
        title="Click to enlarge"
        className={cn(frame, "w-full cursor-zoom-in")}
      >
        {img}
      </button>
      {enlarged && (
        <Lightbox
          src={libraryTemplateImageUrl(id)}
          alt={`${id} schematic`}
          caption={id}
          onClose={() => setEnlarged(false)}
        />
      )}
    </>
  );
}
