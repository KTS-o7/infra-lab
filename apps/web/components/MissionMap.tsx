"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { clsx } from "clsx";
import {
  Award,
  BookOpen,
  CheckCircle2,
  CircleDashed,
  Flag,
  Layers3,
  Loader2,
  Lock,
  PlayCircle,
  Route,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { getCourse, type CapabilityProgress, type CourseModule, type CourseResponse } from "@/lib/api";

const statusStyles = {
  locked: "border-white/10 bg-white/[0.025] text-emerald-100/42",
  available: "border-teal-300/20 bg-teal-300/10 text-teal-100",
  started: "border-amber-300/20 bg-amber-300/10 text-amber-100",
  completed: "border-lime-300/20 bg-lime-300/10 text-lime-100",
};

const capabilityStyles = {
  locked: "border-white/10 bg-white/[0.025] text-emerald-100/42",
  in_progress: "border-amber-300/20 bg-amber-300/10 text-amber-100",
  unlocked: "border-lime-300/20 bg-lime-300/10 text-lime-100",
};

function MissionStatusIcon({ status }: { status: string }) {
  if (status === "completed") return <CheckCircle2 className="h-4 w-4" />;
  if (status === "started") return <PlayCircle className="h-4 w-4" />;
  if (status === "locked") return <Lock className="h-4 w-4" />;
  return <CircleDashed className="h-4 w-4" />;
}

function CapabilitySummary({ capabilities }: { capabilities: CapabilityProgress[] }) {
  if (capabilities.length === 0) return null;

  return (
    <section className="rounded-lg border border-white/10 bg-[#0b1512]/80 p-4 shadow-xl shadow-black/10">
      <div className="mb-3 flex items-center gap-2">
        <ShieldCheck className="h-4 w-4 text-lime-300" />
        <h2 className="text-sm font-semibold text-emerald-50">Capability summary</h2>
      </div>
      <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
        {capabilities.map((capability) => (
          <div
            key={capability.id}
            className={clsx(
              "rounded-md border px-3 py-2",
              capabilityStyles[capability.status as keyof typeof capabilityStyles] ?? capabilityStyles.locked,
            )}
          >
            <p className="text-sm font-medium">{capability.label}</p>
            <p className="mt-1 text-xs opacity-70">
              {capability.status === "unlocked" ? "online" : capability.status.replace("_", " ")}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}

function ModuleCard({
  module,
  nextMissionId,
}: {
  module: CourseModule;
  nextMissionId: string | null;
}) {
  const lessonTotal = module.requiredLessonsTotal + module.requiredCapstonesTotal;
  const lessonDone = module.requiredLessonsCompleted + module.requiredCapstonesCompleted;
  const progressLabel = `${lessonDone}/${lessonTotal} required`;

  return (
    <section className="rounded-lg border border-white/10 bg-white/[0.045] p-4 shadow-xl shadow-black/10 sm:p-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <div className="mb-2 flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1.5 rounded-md border border-lime-300/20 bg-lime-300/10 px-2 py-1 text-xs font-medium uppercase tracking-[0.14em] text-lime-100">
              <Layers3 className="h-3.5 w-3.5" />
              Module {module.order}
            </span>
            <span className={clsx("rounded-md border px-2 py-1 text-xs font-medium", statusStyles[module.status])}>
              {module.status}
            </span>
          </div>
          <h3 className="text-xl font-semibold leading-tight text-emerald-50">{module.title}</h3>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-emerald-100/58">{module.summary}</p>
        </div>
        <div className="shrink-0 rounded-md border border-white/10 bg-black/20 px-3 py-2 text-sm text-emerald-100/65">
          <span className="font-semibold text-emerald-50">{progressLabel}</span>
          <span className="mt-1 block text-xs text-emerald-100/42">{module.capabilityLabel}</span>
        </div>
      </div>

      <div className="mt-5 grid gap-3">
        {module.missions.map((mission) => {
          const isLocked = mission.status === "locked";
          const isNext = mission.id === nextMissionId;
          const isCapstone = mission.missionType === "module_capstone" || mission.missionType === "final_capstone";
          const body = (
            <div
              className={clsx(
                "flex min-h-[5rem] items-start gap-3 rounded-lg border p-4 text-left transition",
                isLocked
                  ? "cursor-not-allowed border-white/10 bg-black/15 opacity-65"
                  : "border-white/10 bg-black/20 hover:border-lime-300/35 hover:bg-white/[0.06]",
                isNext && "ring-1 ring-lime-300/45",
              )}
            >
              <div
                className={clsx(
                  "mt-0.5 rounded-md border p-2",
                  statusStyles[mission.status as keyof typeof statusStyles] ?? statusStyles.available,
                )}
              >
                {isCapstone ? <Flag className="h-4 w-4" /> : <MissionStatusIcon status={mission.status} />}
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <p className="font-medium text-emerald-50">{mission.title}</p>
                  {isNext ? (
                    <span className="rounded-md border border-lime-300/25 bg-lime-300/10 px-2 py-0.5 text-xs font-medium text-lime-100">
                      Next
                    </span>
                  ) : null}
                  {isCapstone ? (
                    <span className="rounded-md border border-amber-300/20 bg-amber-300/10 px-2 py-0.5 text-xs font-medium text-amber-100">
                      Capstone
                    </span>
                  ) : null}
                </div>
                <p className="mt-1 text-xs uppercase tracking-[0.14em] text-emerald-100/38">
                  {mission.required ? "Required" : "Optional"} · {mission.status}
                </p>
                {mission.submodule ? (
                  <p className="mt-1 text-xs text-emerald-100/45">Submodule: {mission.submodule}</p>
                ) : null}
                {isLocked && (mission.prerequisites ?? []).length > 0 ? (
                  <p className="mt-2 text-xs leading-5 text-amber-100/75">
                    Complete prerequisite: {(mission.prerequisites ?? []).join(", ")}
                  </p>
                ) : null}
              </div>
            </div>
          );

          if (isLocked) {
            const href = nextMissionId ? `/missions/${nextMissionId}` : `/missions/${mission.prerequisites?.[0] ?? mission.id}`;
            return (
              <Link key={mission.id} href={href} className="block w-full" aria-label={`${mission.title} is locked. Open the next prerequisite mission.`}>
                {body}
              </Link>
            );
          }

          return (
            <Link key={mission.id} href={`/missions/${mission.id}`} className="block">
              {body}
            </Link>
          );
        })}
      </div>
    </section>
  );
}

export default function MissionMap() {
  const [courseData, setCourseData] = useState<CourseResponse["course"] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    setError(null);
    getCourse()
      .then((data) => setCourseData(data.course))
      .catch(() => setError("Failed to load course map"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const nextMission = useMemo(() => {
    if (!courseData?.progress.nextMissionId) return null;
    for (const module of courseData.modules) {
      const mission = module.missions.find((item) => item.id === courseData.progress.nextMissionId);
      if (mission) return mission;
    }
    return null;
  }, [courseData]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 rounded-lg border border-white/10 bg-white/[0.035] py-24">
        <Loader2 className="h-8 w-8 animate-spin text-lime-300" />
        <p className="text-sm text-emerald-100/55">Loading course map...</p>
      </div>
    );
  }

  if (error || !courseData) {
    return (
      <div className="rounded-lg border border-red-400/20 bg-red-950/45 py-24 text-center">
        <p className="mb-4 text-red-200">{error || "Course map is unavailable"}</p>
        <button onClick={load} className="rounded-md border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-emerald-50 hover:bg-white/[0.075]">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="mb-2 flex items-center gap-2 text-sm font-medium text-lime-200">
            <Route className="h-4 w-4" />
            Course map
          </div>
          <h1 className="text-2xl font-semibold text-emerald-50">{courseData.title}</h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-emerald-100/58">{courseData.summary}</p>
        </div>
        <div className="rounded-lg border border-white/10 bg-[#0b1512]/80 p-4 text-sm text-emerald-100/65">
          <div className="flex items-center gap-2 text-emerald-50">
            <Award className="h-4 w-4 text-lime-300" />
            <span className="font-semibold">{courseData.progress.xp} XP</span>
          </div>
          <p className="mt-1 text-xs text-emerald-100/45">
            {courseData.progress.requiredLessonsCompleted}/{courseData.progress.requiredLessonsTotal} lessons ·{" "}
            {courseData.progress.requiredCapstonesCompleted}/{courseData.progress.requiredCapstonesTotal} capstones
          </p>
        </div>
      </div>

      {nextMission ? (
        <Link
          href={`/missions/${nextMission.id}`}
          className="flex items-center gap-3 rounded-lg border border-lime-300/25 bg-lime-300/10 p-4 text-lime-50 transition hover:bg-lime-300/15"
        >
          <Sparkles className="h-5 w-5 shrink-0 text-lime-300" />
          <span className="min-w-0">
            <span className="block text-sm font-semibold">Next recommended mission</span>
            <span className="block truncate text-sm text-lime-100/75">{nextMission.title}</span>
          </span>
        </Link>
      ) : (
        <div className="flex items-center gap-3 rounded-lg border border-white/10 bg-white/[0.035] p-4 text-emerald-100/62">
          <BookOpen className="h-5 w-5 shrink-0 text-lime-300" />
          <span className="text-sm">No available next mission. Completed modules remain reviewable.</span>
        </div>
      )}

      <CapabilitySummary capabilities={courseData.capabilities} />

      <div className="grid gap-4">
        {courseData.modules.map((module) => (
          <ModuleCard
            key={module.id}
            module={module}
            nextMissionId={courseData.progress.nextMissionId}
          />
        ))}
      </div>
    </div>
  );
}
