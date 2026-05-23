"use client";

import { useEffect, useState } from "react";
import { getMissions, Mission } from "@/lib/api";
import MissionCard from "./MissionCard";
import Link from "next/link";

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
      <div className="flex flex-col items-center justify-center py-24 gap-4">
        <div className="animate-spin w-10 h-10 border-3 border-blue-500 border-t-transparent rounded-full" />
        <p className="text-slate-400">Loading missions...</p>
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
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-slate-100 mb-2">Mission Map</h2>
        <p className="text-slate-400">Complete missions to earn XP and unlock the next challenge.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {missions.map((mission) => (
          <Link key={mission.id} href={`/missions/${mission.id}`} className="block">
            <MissionCard mission={mission} />
          </Link>
        ))}
      </div>
    </div>
  );
}