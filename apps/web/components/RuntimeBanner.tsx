"use client";

import { useEffect, useState } from "react";
import { getRuntimeStatus, RuntimeStatus } from "@/lib/api";

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
    <div className="rounded-lg border border-red-800 bg-red-950 p-4 mb-6">
      <div className="flex items-start gap-3">
        <svg className="text-red-400 mt-0.5 shrink-0" width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
        <div>
          <p className="text-red-300 font-medium">Runtime Offline</p>
          <p className="text-red-400 text-sm mt-1">
            API: {status.api.status} | Floci: {status.floci.status}
          </p>
          <p className="text-red-500 text-xs mt-2 font-mono">docker compose ps</p>
        </div>
      </div>
    </div>
  );
}