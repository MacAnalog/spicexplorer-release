"use client";
import { OptimizeTab } from "@/components/tabs/OptimizeTab";
import { useUIStore } from "@/stores/uiStore";

export default function OptimizePage() {
  const appConfig = useUIStore((s) => s.appConfig);
  return <OptimizeTab appConfig={appConfig} />;
}
