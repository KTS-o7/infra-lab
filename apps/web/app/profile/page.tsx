"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { getCourse, getProfile, type CourseResponse, type Profile } from "@/lib/api";
import { Award, BadgeCheck, CheckCircle2, Loader2, RefreshCw, Trophy, type LucideIcon } from "lucide-react";

export default function ProfilePage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [course, setCourse] = useState<CourseResponse["course"] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    setError(null);
    Promise.all([getProfile(), getCourse()])
      .then(([profileResponse, courseResponse]) => {
        setProfile(profileResponse.profile);
        setCourse(courseResponse.course);
      })
      .catch(() => setError("Profile is unavailable while the local API cannot be reached."))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const progress = profile?.courseProgress ?? course?.progress ?? null;
  const badges = profile?.badges ?? [];

  return (
    <AppShell>
      {loading ? (
        <div className="flex items-center justify-center rounded-lg border border-white/10 bg-white/[0.035] py-24">
          <Loader2 className="h-8 w-8 animate-spin text-lime-300" />
        </div>
      ) : error || !profile || !progress ? (
        <div className="rounded-lg border border-red-400/20 bg-red-950/45 p-6 text-red-100">
          <p>{error ?? "Profile could not be loaded."}</p>
          <button onClick={load} className="mt-4 inline-flex items-center gap-2 rounded-md border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-emerald-50 hover:bg-white/[0.075]">
            <RefreshCw className="h-4 w-4" />
            Retry
          </button>
        </div>
      ) : (
        <div className="space-y-5">
          <section className="rounded-lg border border-white/10 bg-white/[0.045] p-5 shadow-xl shadow-black/10">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.14em] text-emerald-100/42">Profile</p>
                <h1 className="mt-1 text-2xl font-semibold text-emerald-50">{profile.displayName}</h1>
                <p className="mt-2 text-sm leading-6 text-emerald-100/58">Local learner progress is stored in the lab database and reflects completed required checks.</p>
              </div>
              <div className="grid grid-cols-2 gap-3 sm:min-w-72">
                <Metric icon={Award} label="XP" value={String(profile.totalXp)} />
                <Metric icon={Trophy} label="Status" value={formatStatus(progress.status)} />
              </div>
            </div>
          </section>

          <section className="grid gap-4 lg:grid-cols-[1fr_22rem]">
            <div className="rounded-lg border border-white/10 bg-[#0b1512]/80 p-5 shadow-xl shadow-black/10">
              <h2 className="text-lg font-semibold text-emerald-50">Course progress</h2>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <ProgressTile label="Required lessons" done={progress.requiredLessonsCompleted} total={progress.requiredLessonsTotal} />
                <ProgressTile label="Required capstones" done={progress.requiredCapstonesCompleted} total={progress.requiredCapstonesTotal} />
              </div>
              {progress.completedAt ? (
                <p className="mt-4 text-sm text-lime-100">Course completed {new Date(progress.completedAt).toLocaleString()}.</p>
              ) : progress.nextMissionId ? (
                <p className="mt-4 text-sm text-emerald-100/58">Next mission: <span className="text-emerald-50">{progress.nextMissionId}</span></p>
              ) : (
                <p className="mt-4 text-sm text-emerald-100/58">No next mission is currently available.</p>
              )}
            </div>

            <div className="rounded-lg border border-white/10 bg-[#0b1512]/80 p-5 shadow-xl shadow-black/10">
              <h2 className="text-lg font-semibold text-emerald-50">Capability badges</h2>
              {badges.length ? (
                <div className="mt-4 space-y-2">
                  {badges.map((badge) => (
                    <div key={badge.id} className="flex items-start gap-3 rounded-md border border-lime-300/20 bg-lime-300/10 p-3">
                      <BadgeCheck className="mt-0.5 h-4 w-4 shrink-0 text-lime-300" />
                      <div>
                        <p className="text-sm font-medium text-lime-100">{badge.label ?? badge.title ?? badge.id}</p>
                        {badge.earnedAt ?? badge.awardedAt ? (
                          <p className="mt-1 text-xs text-lime-100/62">{new Date(badge.earnedAt ?? badge.awardedAt ?? "").toLocaleString()}</p>
                        ) : null}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="mt-4 text-sm leading-6 text-emerald-100/58">Complete a module's required work to earn the first capability badge.</p>
              )}
            </div>
          </section>
        </div>
      )}
    </AppShell>
  );
}

function Metric({ icon: Icon, label, value }: { icon: LucideIcon; label: string; value: string }) {
  return (
    <div className="rounded-md border border-white/10 bg-black/20 p-3">
      <div className="mb-2 flex items-center gap-2 text-emerald-100/45">
        <Icon className="h-4 w-4" />
        <span className="text-xs uppercase tracking-[0.12em]">{label}</span>
      </div>
      <p className="text-xl font-semibold text-emerald-50">{value}</p>
    </div>
  );
}

function ProgressTile({ label, done, total }: { label: string; done: number; total: number }) {
  const percent = total > 0 ? Math.round((done / total) * 100) : 0;
  return (
    <div className="rounded-md border border-white/10 bg-black/20 p-4">
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm font-medium text-emerald-50">{label}</p>
        <CheckCircle2 className="h-4 w-4 text-lime-300" />
      </div>
      <p className="mt-2 text-2xl font-semibold text-lime-100">{done}/{total}</p>
      <div className="mt-3 h-2 rounded-full bg-white/10">
        <div className="h-2 rounded-full bg-lime-300" style={{ width: `${percent}%` }} />
      </div>
    </div>
  );
}

function formatStatus(status: string) {
  return status.replaceAll("_", " ");
}
