"use client";

import { useEffect, useState } from "react";
import { getMissions, Mission } from "@/lib/api";
import MissionCard from "./MissionCard";
import Link from "next/link";
import { Loader2, Route, HardDrive, Zap, Globe, Database, Bell, Cpu } from "lucide-react";

const SERVICE_CONFIG: Record<string, { label: string; icon: React.ElementType; color: string }> = {
  s3: { label: "S3", icon: HardDrive, color: "text-orange-300" },
  sqs: { label: "SQS", icon: Bell, color: "text-blue-300" },
  sns: { label: "SNS", icon: Zap, color: "text-amber-300" },
  lambda: { label: "Lambda", icon: Cpu, color: "text-purple-300" },
  apigateway: { label: "API GW", icon: Globe, color: "text-teal-300" },
  dynamodb: { label: "DynamoDB", icon: Database, color: "text-cyan-300" },
};

const ALL_SERVICES = ["s3", "sqs", "sns", "lambda", "apigateway", "dynamodb"];

function PlatformStatus({ missions }: { missions: Mission[] }) {
  const completedServices = Array.from(
    new Set(
      missions
        .filter((m) => m.status === "completed" && m.services)
        .flatMap((m) => m.services ?? [])
    )
  );

  return (
    <div className="mb-4 flex items-center gap-3 text-xs">
      <span className="text-emerald-100/40">Platform:</span>
      <div className="flex items-center gap-2">
        {ALL_SERVICES.map((service) => {
          const config = SERVICE_CONFIG[service];
          const isActive = completedServices.includes(service);
          const Icon = config.icon;
          return (
            <div
              key={service}
              className={`flex items-center gap-1 rounded-full px-2 py-1 transition-colors ${
                isActive
                  ? `bg-lime-300/10 border border-lime-300/30 ${config.color}`
                  : "border border-white/10 text-white/20"
              }`}
            >
              <Icon className="h-3 w-3" />
              <span>{config.label}</span>
            </div>
          );
        })}
        {!completedServices.length && (
          <span className="text-white/30">Starting fresh...</span>
        )}
      </div>
    </div>
  );
}

export default function MissionMap() {
  const [missions, setMissions] = useState<Mission[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lockedMsg, setLockedMsg] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    setError(null);
    getMissions()
      .then((data) => setMissions(data.missions ?? []))
      .catch(() => setError("Failed to load missions"))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleLockedClick = (mission: Mission) => {
    const prereqs = (mission.prerequisites ?? []).join(", ");
    setLockedMsg(`"${mission.title}" is locked. Complete: ${prereqs}`);
    setTimeout(() => setLockedMsg(null), 3500);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 rounded-lg border border-white/10 bg-white/[0.035] py-24">
        <Loader2 className="h-8 w-8 animate-spin text-lime-300" />
        <p className="text-sm text-emerald-100/55">Loading missions...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-24">
        <p className="text-red-400 mb-4">{error}</p>
        <button onClick={load} className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm">
          Retry
        </button>
      </div>
    );
  }

  if (missions.length === 0) {
    return (
      <div className="text-center py-24 text-slate-400">
        <p>No missions available yet.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="mb-2 flex items-center gap-2 text-sm font-medium text-lime-200">
            <Route className="h-4 w-4" />
            Mission map
          </div>
          <h2 className="text-2xl font-semibold text-emerald-50">Build the stack one service at a time.</h2>
        </div>
        <p className="max-w-md text-sm leading-6 text-emerald-100/55">
          Each card is a live lab checkpoint. Locked missions open after prerequisite resources validate.
        </p>
      </div>

      <PlatformStatus missions={missions} />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {missions.map((mission) =>
          mission.status === "locked" ? (
            <div key={mission.id} className="block cursor-not-allowed" onClick={() => handleLockedClick(mission)}>
              <MissionCard mission={mission} />
            </div>
          ) : (
            <Link key={mission.id} href={`/missions/${mission.id}`} className="block">
              <MissionCard mission={mission} />
            </Link>
          )
        )}
      </div>

      {lockedMsg && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 rounded-lg border border-amber-400/30 bg-amber-950/80 px-5 py-3 text-sm text-amber-200 shadow-xl backdrop-blur">
          {lockedMsg}
        </div>
      )}
    </div>
  );
}
