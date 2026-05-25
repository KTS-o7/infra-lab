"use client";

import { useEffect, useState } from "react";
import { getProfile, Profile } from "@/lib/api";
import { Award, Gauge, Trophy } from "lucide-react";

export default function XpSummary() {
  const [profile, setProfile] = useState<Profile | null>(null);

  useEffect(() => {
    getProfile()
      .then((data) => setProfile(data.profile))
      .catch(() => null);
  }, []);

  if (!profile) return null;

  const completedCount = (profile.completedMissionIds ?? []).length;

  return (
    <aside className="rounded-lg border border-white/10 bg-[#0b1512]/80 p-5 shadow-2xl shadow-black/20 backdrop-blur lg:sticky lg:top-24">
      <div className="mb-5 flex items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.14em] text-emerald-100/42">Operator</p>
          <h2 className="mt-1 text-lg font-semibold text-emerald-50">{profile.displayName}</h2>
        </div>
        <div className="flex h-10 w-10 items-center justify-center rounded-md border border-lime-300/25 bg-lime-300/10 text-lime-200">
          <Trophy className="h-5 w-5" />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="rounded-md border border-white/10 bg-white/[0.035] p-3">
          <div className="mb-3 flex items-center gap-2 text-emerald-100/45">
            <Award className="h-4 w-4" />
            <span className="text-xs uppercase tracking-[0.12em]">XP</span>
          </div>
          <p className="text-2xl font-semibold text-lime-100">{profile.totalXp}</p>
        </div>
        <div className="rounded-md border border-white/10 bg-white/[0.035] p-3">
          <div className="mb-3 flex items-center gap-2 text-emerald-100/45">
            <Gauge className="h-4 w-4" />
            <span className="text-xs uppercase tracking-[0.12em]">Done</span>
          </div>
          <p className="text-2xl font-semibold text-emerald-50">{completedCount}</p>
        </div>
      </div>

      {completedCount > 0 ? (
        <div className="mt-5 border-t border-white/10 pt-4">
          <p className="mb-3 text-xs uppercase tracking-[0.14em] text-emerald-100/42">Completed missions</p>
          <div className="flex flex-wrap gap-2">
            {(profile.completedMissionIds ?? []).map((id) => (
              <span key={id} className="rounded-md border border-lime-300/20 bg-lime-300/10 px-2 py-1 text-xs text-lime-100">
                {id}
              </span>
            ))}
          </div>
        </div>
      ) : (
        <p className="mt-5 border-t border-white/10 pt-4 text-sm leading-6 text-emerald-100/52">
          Start with Cloud Explorer to unlock the first resource-building mission.
        </p>
      )}
    </aside>
  );
}
