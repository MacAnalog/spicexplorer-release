"use client";
import { SetupTab } from "@/components/tabs/SetupTab";
import { useUIStore } from "@/stores/uiStore";

export default function SetupPage() {
  const appConfig = useUIStore((s) => s.appConfig);
  return <SetupTab appConfig={appConfig} />;
}
