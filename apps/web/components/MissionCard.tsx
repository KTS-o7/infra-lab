import { Mission } from "@/lib/api";
import { clsx } from "clsx";

interface Props {
  mission: Mission;
}

const difficultyColor = {
  beginner: "text-emerald-400",
  intermediate: "text-amber-400",
  boss: "text-rose-400",
};

const statusBadge = {
  locked: "bg-slate-800 text-slate-500",
  available: "bg-blue-900 text-blue-300 border border-blue-700",
  started: "bg-amber-900 text-amber-300 border border-amber-700",
  completed: "bg-emerald-900 text-emerald-300 border border-emerald-700",
};

export default function MissionCard({ mission }: Props) {
  return (
    <div className={clsx(
      "rounded-xl border p-5 transition-all hover:scale-[1.02] duration-200",
      mission.status === "locked"
        ? "bg-slate-900 border-slate-800 opacity-60"
        : "bg-slate-900 border-slate-700 hover:border-slate-600"
    )}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className={clsx("text-xs font-medium uppercase tracking-wide", difficultyColor[mission.difficulty as keyof typeof difficultyColor] || "text-slate-400")}>
            {mission.difficulty}
          </span>
          <span className="text-slate-600">•</span>
          <span className="text-xs text-slate-400">{mission.services.join(", ")}</span>
        </div>
        <span className={clsx("text-xs px-2 py-0.5 rounded-full font-medium", statusBadge[mission.status as keyof typeof statusBadge] || statusBadge.available)}>
          {mission.status}
        </span>
      </div>

      <h3 className="text-lg font-semibold text-slate-100 mb-1">{mission.title}</h3>
      <p className="text-sm text-slate-400 mb-4 line-clamp-2">{mission.summary}</p>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1">
          <span className="text-amber-400">⭐</span>
          <span className="text-sm font-medium text-amber-400">{mission.xp} XP</span>
        </div>
        <div className="flex items-center gap-1 text-slate-500">
          <svg width="14" height="14" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
          </svg>
          <span className="text-xs">{mission.estimatedMinutes}m</span>
        </div>
      </div>

      {mission.status === "locked" && mission.prerequisites.length > 0 && (
        <p className="text-xs text-slate-500 mt-3">Requires: {mission.prerequisites.join(", ")}</p>
      )}
    </div>
  );
}