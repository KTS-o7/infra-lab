"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { getRuntimeStatus, type RuntimeStatus } from "@/lib/api";
import { Boxes, Database, Loader2, RefreshCw, ShieldCheck, TerminalSquare, WifiOff, type LucideIcon } from "lucide-react";

export default function SettingsPage() {
  const [status, setStatus] = useState<RuntimeStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const load = () => {
    setLoading(true);
    setError(false);
    getRuntimeStatus()
      .then(setStatus)
      .catch(() => {
        setStatus(null);
        setError(true);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <AppShell>
      <div className="space-y-5">
        <section className="rounded-lg border border-white/10 bg-white/[0.045] p-5 shadow-xl shadow-black/10">
          <p className="text-xs uppercase tracking-[0.14em] text-emerald-100/42">Settings</p>
          <h1 className="mt-1 text-2xl font-semibold text-emerald-50">Local lab runtime</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-emerald-100/58">
            These settings are read-only in the browser. Runtime and reset actions stay local to the Docker lab.
          </p>
        </section>

        <section className="rounded-lg border border-white/10 bg-[#0b1512]/80 p-5 shadow-xl shadow-black/10">
          <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <h2 className="text-lg font-semibold text-emerald-50">Runtime status</h2>
            <button onClick={load} disabled={loading} className="inline-flex items-center justify-center gap-2 rounded-md border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-emerald-50 hover:bg-white/[0.075] disabled:opacity-50">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
              Refresh
            </button>
          </div>

          {loading ? (
            <div className="flex items-center gap-2 text-sm text-emerald-100/55">
              <Loader2 className="h-4 w-4 animate-spin text-lime-300" />
              Checking runtime
            </div>
          ) : error || !status ? (
            <div className="flex items-start gap-3 rounded-md border border-red-400/20 bg-red-950/45 p-4 text-red-100">
              <WifiOff className="mt-0.5 h-5 w-5 shrink-0" />
              <div>
                <p className="font-medium">API offline</p>
                <p className="mt-1 text-sm text-red-200/75">Start or inspect the local stack, then retry.</p>
              </div>
            </div>
          ) : (
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
              <RuntimeTile icon={TerminalSquare} label="API" value={status.api.status} healthy={status.api.status === "online"} />
              <RuntimeTile icon={Boxes} label="Floci" value={status.floci.status} detail={status.floci.endpoint} healthy={status.floci.status === "online"} />
              <RuntimeTile icon={Database} label="Database" value={status.database.status} healthy={status.database.status === "online"} />
              <RuntimeTile icon={ShieldCheck} label="Local only" value={status.localOnly.status} detail={status.localOnly.endpoint} healthy={status.localOnly.status === "enforced" || status.localOnly.status === "online"} />
            </div>
          )}
        </section>

        <section className="grid gap-4 lg:grid-cols-2">
          <InfoPanel title="Reset behavior">
            Mission reset controls live inside each workbench. Resource resets remove mission-owned local resources and mark previous proof stale; progress resets clear step state and hint reveals while preserving completed credit and XP.
          </InfoPanel>
          <InfoPanel title="Troubleshooting">
            Use `docker compose ps` to inspect services and `make reset` for a full lab reset. Validation and reset actions are disabled when the runtime cannot perform them.
          </InfoPanel>
        </section>
      </div>
    </AppShell>
  );
}

function RuntimeTile({ icon: Icon, label, value, detail, healthy }: { icon: LucideIcon; label: string; value: string; detail?: string; healthy: boolean }) {
  return (
    <div className="rounded-md border border-white/10 bg-black/20 p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="flex min-w-0 items-center gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-white/[0.05] text-emerald-100/65">
            <Icon className="h-4 w-4" />
          </div>
          <div className="min-w-0">
            <p className="text-xs uppercase tracking-[0.12em] text-emerald-100/42">{label}</p>
            <p className="mt-1 truncate text-sm font-medium text-emerald-50">{value}</p>
          </div>
        </div>
        <span className={healthy ? "h-2.5 w-2.5 rounded-full bg-lime-300" : "h-2.5 w-2.5 rounded-full bg-red-300"} />
      </div>
      {detail ? <p className="mt-3 truncate font-mono text-xs text-emerald-100/45">{detail}</p> : null}
    </div>
  );
}

function InfoPanel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-white/10 bg-[#0b1512]/80 p-5 shadow-xl shadow-black/10">
      <h2 className="text-lg font-semibold text-emerald-50">{title}</h2>
      <p className="mt-2 text-sm leading-6 text-emerald-100/58">{children}</p>
    </div>
  );
}
