import { StudioShell } from "@/components/shell/StudioShell";

/**
 * Persistent Studio layout. In the App Router a layout does NOT remount when
 * navigating between its child segments — only the segment `page.tsx` swaps — so
 * StudioShell (rail, status bar, and later the right rail + bottom panel + live
 * SSE stream) stays mounted across /setup → /scoring → /optimize → …
 */
export default function StudioLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <StudioShell>{children}</StudioShell>;
}
