"use client";

import { useEffect, useState } from "react";
import { getRuntimeStatus, RuntimeStatus } from "@/lib/api";

interface Props {
  children: React.ReactNode;
}

export default function AppShell({ children }: Props) {
  const [status, setStatus] = useState<RuntimeStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getRuntimeStatus()
      .then(setStatus)
      .catch(() => setStatus(null))
      .finally(() => setLoading(false));

    const interval = setInterval(async () => {
      try {
        const s = await getRuntimeStatus();
        setStatus(s);
      } catch {
        // ignore
      }
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const isHealthy = status?.api?.status === "online" && status?.floci?.status === "online";

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-slate-800 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center">
              <span className="text-white font-bold text-sm">IQ</span>
            </div>
            <h1 className="text-xl font-bold text-slate-100">Infra Quest</h1>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">This lab runs locally.</span>
            <span className="px-2 py-0.5 rounded text-xs font-medium bg-green-900 text-green-300 border border-green-700">
              No real AWS
            </span>
          </div>
        </div>
      </header>

      {loading ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full" />
        </div>
      ) : status && (status.api.status !== "online" || status.floci.status !== "online") ? (
        <div className="mx-auto max-w-5xl w-full px-6 py-4">
          <div className="rounded-lg border border-red-800 bg-red-950 p-4 flex items-start gap-3">
            <div className="text-red-400 mt-0.5">
              <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div>
              <p className="text-red-300 font-medium">Runtime Unavailable</p>
              <p className="text-red-400 text-sm mt-1">
                API: {status.api.status} | Floci: {status.floci.status} | DB: {status.database.status}
              </p>
              <p className="text-red-500 text-xs mt-1 font-mono">docker compose ps</p>
            </div>
          </div>
        </div>
      ) : null}

      <main className="flex-1 px-6 py-8">
        <div className="max-w-5xl mx-auto">{children}</div>
      </main>

      <footer className="border-t border-slate-800 px-6 py-4 text-center text-slate-500 text-sm">
        Infra Quest — Local AWS Learning Lab
      </footer>
    </div>
  );
}