"use client";

import { useEffect, useState } from "react";
import { getMissions, Mission } from "@/lib/api";
import MissionCard from "./MissionCard";
import Link from "next/link";
import { Loader2, Route } from "lucide-react";

export default function MissionMap() {
  const [missions, setMissions] = useState<Mission[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    setError(null);
    getMissions()
      .then((data) => setMissions(data.missions ?? []))
      .catch(() => setError("Failed to load missions"))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

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

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {missions.map((mission) =>
          mission.status === "locked" ? (
            <div key={mission.id} className="block">
              <MissionCard mission={mission} />
            </div>
          ) : (
            <Link key={mission.id} href={`/missions/${mission.id}`} className="block">
              <MissionCard mission={mission} />
            </Link>
          )
        )}
      </div>
    </div>
  );
}
