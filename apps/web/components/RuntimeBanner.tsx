"use client";

import { useEffect, useState } from "react";
import { getRuntimeStatus, RuntimeStatus } from "@/lib/api";
import { WifiOff } from "lucide-react";

export default function RuntimeBanner() {
  const [status, setStatus] = useState<RuntimeStatus | null>(null);

  useEffect(() => {
    getRuntimeStatus()
      .then(setStatus)
      .catch(() => null);
  }, []);

  if (!status) return null;

  const isOffline = status.api.status !== "online" || status.floci.status !== "online";

  if (!isOffline) return null;

  return (
    <div className="mb-6 rounded-lg border border-red-400/20 bg-red-950/45 p-4 shadow-xl shadow-red-950/20">
      <div className="flex items-start gap-3">
        <WifiOff className="mt-0.5 h-5 w-5 shrink-0 text-red-300" />
        <div>
          <p className="font-medium text-red-100">Runtime offline</p>
          <p className="mt-1 text-sm text-red-200/75">
            API: {status.api.status} | Floci: {status.floci.status}
          </p>
          <p className="mt-2 font-mono text-xs text-red-200/55">docker compose ps</p>
        </div>
      </div>
    </div>
  );
}
