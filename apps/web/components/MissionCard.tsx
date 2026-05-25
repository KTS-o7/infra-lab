import { Mission } from "@/lib/api";
import { clsx } from "clsx";
import { CheckCircle2, Clock3, Lock, PlayCircle, Star, Timer } from "lucide-react";

interface Props {
  mission: Mission;
}

const difficultyColor = {
  beginner: "text-lime-200 bg-lime-300/10 border-lime-300/20",
  intermediate: "text-amber-200 bg-amber-300/10 border-amber-300/20",
  boss: "text-rose-200 bg-rose-300/10 border-rose-300/20",
};

const statusBadge = {
  locked: "bg-white/[0.04] text-emerald-100/40 border-white/10",
  available: "bg-teal-300/10 text-teal-100 border-teal-300/20",
  started: "bg-amber-300/10 text-amber-100 border-amber-300/20",
  completed: "bg-lime-300/10 text-lime-100 border-lime-300/20",
};

export default function MissionCard({ mission }: Props) {
  const StatusIcon =
    mission.status === "completed" ? CheckCircle2 :
      mission.status === "started" ? Clock3 :
        mission.status === "locked" ? Lock :
          PlayCircle;

  return (
    <div className={clsx(
      "group relative h-full overflow-hidden rounded-lg border p-5 transition duration-200",
      mission.status === "locked"
        ? "border-white/10 bg-white/[0.025] opacity-65"
        : "border-white/10 bg-white/[0.055] shadow-xl shadow-black/10 hover:-translate-y-0.5 hover:border-lime-300/35 hover:bg-white/[0.075]"
    )}>
      {mission.status !== "locked" && (
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-lime-300/60 to-transparent opacity-0 transition group-hover:opacity-100" />
      )}

      <div className="mb-5 flex items-start justify-between gap-3">
        <div className="flex min-w-0 flex-wrap items-center gap-2">
          <span className={clsx("rounded-md border px-2 py-1 text-[11px] font-semibold uppercase tracking-[0.12em]", difficultyColor[mission.difficulty as keyof typeof difficultyColor] || "border-white/10 bg-white/[0.04] text-emerald-100/50")}>
            {mission.difficulty}
          </span>
          <span className="truncate rounded-md border border-white/10 bg-black/20 px-2 py-1 text-[11px] uppercase tracking-[0.12em] text-emerald-100/46">
            {mission.services.join(" / ")}
          </span>
        </div>
        <span className={clsx("inline-flex shrink-0 items-center gap-1.5 rounded-md border px-2 py-1 text-xs font-medium", statusBadge[mission.status as keyof typeof statusBadge] || statusBadge.available)}>
          <StatusIcon className="h-3.5 w-3.5" />
          {mission.status}
        </span>
      </div>

      <h3 className="mb-2 text-lg font-semibold text-emerald-50">{mission.title}</h3>
      <p className="mb-5 min-h-[44px] text-sm leading-6 text-emerald-100/58">{mission.summary}</p>

      <div className="flex items-center justify-between border-t border-white/10 pt-4">
        <div className="flex items-center gap-2">
          <Star className="h-4 w-4 fill-lime-300 text-lime-300" />
          <span className="text-sm font-semibold text-lime-100">{mission.xp} XP</span>
        </div>
        <div className="flex items-center gap-1.5 text-emerald-100/45">
          <Timer className="h-4 w-4" />
          <span className="text-xs font-medium">{mission.estimatedMinutes}m</span>
        </div>
      </div>

      {mission.status === "locked" && (mission.prerequisites ?? []).length > 0 && (
        <p className="mt-3 text-xs text-emerald-100/38">Requires: {(mission.prerequisites ?? []).join(", ")}</p>
      )}
    </div>
  );
}
