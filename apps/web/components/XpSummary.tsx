"use client";

import { useEffect, useState } from "react";
import { getProfile, Profile } from "@/lib/api";

export default function XpSummary() {
  const [profile, setProfile] = useState<Profile | null>(null);

  useEffect(() => {
    getProfile()
      .then((data) => setProfile(data.profile))
      .catch(() => null);
  }, []);

  if (!profile) return null;

  return (
    <div className="rounded-xl border border-slate-700 bg-slate-900 p-6">
      <h2 className="text-lg font-semibold text-slate-100 mb-3">Your Progress</h2>
      <div className="flex items-center gap-3 mb-4">
        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center">
          <span className="text-lg font-bold text-white">{profile.totalXp}</span>
        </div>
        <div>
          <p className="text-xl font-bold text-amber-300">{profile.totalXp} XP</p>
          <p className="text-sm text-slate-400">{profile.displayName}</p>
        </div>
      </div>

      {profile.completedMissionIds.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm text-slate-400">Completed:</p>
          <div className="flex flex-wrap gap-2">
            {profile.completedMissionIds.map((id) => (
              <span key={id} className="px-2 py-1 rounded bg-emerald-900 text-emerald-300 text-xs border border-emerald-700">
                {id}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}