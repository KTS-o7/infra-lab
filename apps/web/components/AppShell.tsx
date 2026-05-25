"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { getRuntimeStatus, RuntimeStatus } from "@/lib/api";
import { Activity, Boxes, Database, Settings, ShieldCheck, TerminalSquare, Trophy, WifiOff, type LucideIcon } from "lucide-react";

interface Props {
  children: React.ReactNode;
}

export default function AppShell({ children }: Props) {
  const [status, setStatus] = useState<RuntimeStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const pathname = usePathname();

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
    <div className="min-h-screen bg-[#08110f] text-emerald-50">
      <div className="pointer-events-none fixed inset-0 -z-10 bg-[radial-gradient(circle_at_18%_10%,rgba(132,204,22,0.16),transparent_28%),radial-gradient(circle_at_78%_0%,rgba(45,212,191,0.12),transparent_24%),linear-gradient(180deg,#0b1714_0%,#08110f_42%,#060b0a_100%)]" />

      <header className="sticky top-0 z-20 border-b border-white/10 bg-[#08110f]/88 px-4 py-3 backdrop-blur-xl sm:px-6">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4">
          <div className="flex min-w-0 items-center gap-3">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md border border-lime-300/30 bg-lime-300 text-sm font-black text-[#08110f] shadow-[0_0_28px_rgba(132,204,22,0.2)]">
              IQ
            </div>
            <div className="min-w-0">
              <h1 className="truncate text-base font-semibold text-emerald-50 sm:text-lg">Infra Quest</h1>
              <p className="hidden text-xs text-emerald-100/50 sm:block">Local AWS practice environment</p>
            </div>
          </div>

          <nav aria-label="Primary" className="hidden items-center gap-1 md:flex">
            <NavLink href="/" label="Course" active={pathname === "/"} />
            <NavLink href="/profile" label="Profile" active={pathname === "/profile"} icon={Trophy} />
            <NavLink href="/settings" label="Settings" active={pathname === "/settings"} icon={Settings} />
          </nav>

          <div className="flex items-center gap-2">
            <div className="hidden items-center gap-2 rounded-md border border-white/10 bg-white/[0.04] px-3 py-2 text-xs text-emerald-100/70 md:flex">
              <TerminalSquare className="h-4 w-4 text-lime-300" />
              <span>localhost:3000</span>
            </div>
            <div className="flex items-center gap-2 rounded-md border border-lime-300/25 bg-lime-300/10 px-3 py-2 text-xs font-medium text-lime-100">
              <ShieldCheck className="h-4 w-4 text-lime-300" />
              <span>No real AWS</span>
            </div>
          </div>
        </div>
      </header>

      <nav aria-label="Primary" className="border-b border-white/10 bg-[#08110f]/82 px-4 py-2 md:hidden">
        <div className="mx-auto flex max-w-7xl gap-2 overflow-x-auto">
          <NavLink href="/" label="Course" active={pathname === "/"} />
          <NavLink href="/profile" label="Profile" active={pathname === "/profile"} icon={Trophy} />
          <NavLink href="/settings" label="Settings" active={pathname === "/settings"} icon={Settings} />
        </div>
      </nav>

      {loading ? null : status && !isHealthy ? (
        <div className="mx-auto w-full max-w-7xl px-4 pt-5 sm:px-6">
          <div className="flex items-start gap-3 rounded-lg border border-red-400/20 bg-red-950/45 p-4 shadow-xl shadow-red-950/20">
            <WifiOff className="mt-0.5 h-5 w-5 shrink-0 text-red-300" />
            <div>
              <p className="font-medium text-red-100">Runtime unavailable</p>
              <p className="mt-1 text-sm text-red-200/75">
                API: {status.api.status} / Floci: {status.floci.status} / DB: {status.database.status}
              </p>
              <p className="mt-2 font-mono text-xs text-red-200/55">docker compose ps</p>
            </div>
          </div>
        </div>
      ) : null}

      <main className="px-4 py-6 sm:px-6 sm:py-8">
        <div className="mx-auto max-w-7xl">
          <section className="mb-8 grid gap-4 lg:grid-cols-[1fr_360px]">
            <div className="rounded-lg border border-white/10 bg-white/[0.045] p-5 shadow-2xl shadow-black/20 backdrop-blur sm:p-6">
              <div className="mb-5 flex flex-wrap items-center gap-2">
                <span className="rounded-md border border-lime-300/25 bg-lime-300/10 px-2.5 py-1 text-xs font-semibold uppercase tracking-[0.12em] text-lime-200">
                  Local sandbox
                </span>
                <span className="rounded-md border border-white/10 bg-black/20 px-2.5 py-1 text-xs text-emerald-100/60">
                  Floci endpoint
                </span>
              </div>
              <div className="max-w-3xl">
                <h2 className="text-3xl font-semibold leading-tight text-emerald-50 sm:text-5xl">
                  Practice cloud infrastructure without touching production.
                </h2>
                <p className="mt-4 max-w-2xl text-sm leading-6 text-emerald-100/66 sm:text-base">
                  Run AWS-style missions locally, validate real resources, and unlock the next service only when your lab state proves it is working.
                </p>
              </div>
            </div>

            <div className="grid gap-3 rounded-lg border border-white/10 bg-[#0b1512]/80 p-4 shadow-2xl shadow-black/20 backdrop-blur">
              <RuntimeStat icon={Activity} label="API" value={loading ? "checking" : status?.api.status ?? "unknown"} active={status?.api.status === "online"} />
              <RuntimeStat icon={Boxes} label="Floci" value={loading ? "checking" : status?.floci.status ?? "unknown"} active={status?.floci.status === "online"} />
              <RuntimeStat icon={Database} label="Lab DB" value={loading ? "checking" : status?.database.status ?? "unknown"} active={status?.database.status === "online"} />
            </div>
          </section>

          <div>{children}</div>
        </div>
      </main>

      <footer className="border-t border-white/10 px-4 py-5 text-center text-xs text-emerald-100/40 sm:px-6">
        Infra Quest / Local AWS learning lab
      </footer>
    </div>
  );
}

function NavLink({
  href,
  label,
  active,
  icon: Icon,
}: {
  href: string;
  label: string;
  active: boolean;
  icon?: LucideIcon;
}) {
  return (
    <Link
      href={href}
      aria-current={active ? "page" : undefined}
      className={
        active
          ? "inline-flex items-center gap-2 rounded-md border border-lime-300/25 bg-lime-300/10 px-3 py-2 text-sm font-medium text-lime-100"
          : "inline-flex items-center gap-2 rounded-md border border-transparent px-3 py-2 text-sm font-medium text-emerald-100/58 hover:border-white/10 hover:bg-white/[0.04] hover:text-emerald-50"
      }
    >
      {Icon ? <Icon className="h-4 w-4" /> : null}
      {label}
    </Link>
  );
}

function RuntimeStat({
  icon: Icon,
  label,
  value,
  active,
}: {
  icon: LucideIcon;
  label: string;
  value: string;
  active: boolean;
}) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-md border border-white/10 bg-white/[0.035] px-3 py-3">
      <div className="flex min-w-0 items-center gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-black/25 text-emerald-100/70">
          <Icon className="h-4 w-4" />
        </div>
        <div className="min-w-0">
          <p className="text-xs uppercase tracking-[0.14em] text-emerald-100/42">{label}</p>
          <p className="truncate text-sm font-medium text-emerald-50">{value}</p>
        </div>
      </div>
      <span
        className={active ? "h-2.5 w-2.5 rounded-full bg-lime-300 shadow-[0_0_18px_rgba(190,242,100,0.7)]" : "h-2.5 w-2.5 rounded-full bg-red-300"}
      />
    </div>
  );
}
