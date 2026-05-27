"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { ArrowRight, CheckCircle2, Loader2, Route, ShieldCheck } from "lucide-react";
import { getCourse, type CourseResponse } from "@/lib/api";

interface Props {
  currentMissionId: string;
  currentCapability?: string;
}

export default function CourseContinuityPanel({ currentMissionId, currentCapability }: Props) {
  const [course, setCourse] = useState<CourseResponse["course"] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    getCourse()
      .then((response) => {
        setCourse(response.course);
        setError(false);
      })
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, []);

  const currentModule = useMemo(() => {
    if (!course) return null;
    return course.modules.find((module) => module.missions.some((mission) => mission.id === currentMissionId)) ?? null;
  }, [course, currentMissionId]);

  const currentMission = currentModule?.missions.find((mission) => mission.id === currentMissionId) ?? null;
  const nextMission = useMemo(() => {
    if (!course?.progress.nextMissionId) return null;
    for (const module of course.modules) {
      const mission = module.missions.find((item) => item.id === course.progress.nextMissionId);
      if (mission) return mission;
    }
    return null;
  }, [course]);
  const unlockedCapabilities = course?.capabilities.filter((capability) => capability.status === "unlocked") ?? [];

  return (
    <section className="rounded-lg border border-white/10 bg-[#0b1512]/80 p-4 shadow-xl shadow-black/10">
      <div className="mb-3 flex items-center gap-2">
        <Route className="h-4 w-4 text-lime-300" />
        <h2 className="text-sm font-semibold text-emerald-50">Continuity</h2>
      </div>

      {loading ? (
        <div className="flex items-center gap-2 text-sm text-emerald-100/55">
          <Loader2 className="h-4 w-4 animate-spin text-lime-300" />
          Loading course state
        </div>
      ) : error || !course ? (
        <p className="text-sm leading-6 text-amber-100/75">Course continuity is unavailable while the API cannot answer GET /course.</p>
      ) : (
        <div className="space-y-3">
          <div className="rounded-md border border-white/10 bg-black/15 p-3">
            <p className="text-xs uppercase tracking-[0.12em] text-emerald-100/42">Current module</p>
            <p className="mt-1 text-sm font-medium text-emerald-50">{currentModule?.title ?? "Outside configured course"}</p>
            <p className="mt-1 text-xs text-emerald-100/52">
              {currentMission?.status ?? "unknown"} · {currentModule?.capabilityLabel ?? currentCapability ?? "capability pending"}
            </p>
          </div>

          {nextMission ? (
            <Link
              href={`/missions/${nextMission.id}`}
              className="flex items-center gap-3 rounded-md border border-lime-300/25 bg-lime-300/10 p-3 text-lime-50 transition hover:bg-lime-300/15"
            >
              <ArrowRight className="h-4 w-4 shrink-0 text-lime-300" />
              <span className="min-w-0">
                <span className="block text-xs uppercase tracking-[0.12em] text-lime-100/65">Next mission</span>
                <span className="block truncate text-sm font-medium">{nextMission.title}</span>
              </span>
            </Link>
          ) : (
            <div className="flex items-start gap-2 rounded-md border border-lime-300/20 bg-lime-300/10 p-3 text-sm text-lime-100">
              <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0" />
              <p>No next required mission is currently available.</p>
            </div>
          )}

          <div>
            <p className="mb-2 text-xs uppercase tracking-[0.12em] text-emerald-100/42">Unlocked capabilities</p>
            {unlockedCapabilities.length ? (
              <div className="flex flex-wrap gap-2">
                {unlockedCapabilities.map((capability) => (
                  <span key={`${capability.moduleId}-${capability.id}`} className="inline-flex items-center gap-1.5 rounded-md border border-lime-300/20 bg-lime-300/10 px-2 py-1 text-xs text-lime-100">
                    <ShieldCheck className="h-3.5 w-3.5" />
                    {capability.label}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-sm text-emerald-100/52">Complete required lessons to unlock the first capability.</p>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
