import { CheckCircle2, Clock3, Server, ShieldCheck, Star } from "lucide-react";
import type { MissionDetail } from "@/lib/api";

interface Props {
  mission: MissionDetail["mission"];
}

export default function MissionBrief({ mission }: Props) {
  return (
    <div className="rounded-lg border border-white/10 bg-white/[0.045] p-5 shadow-2xl shadow-black/20 backdrop-blur sm:p-6">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <div className="mb-3 flex flex-wrap items-center gap-3">
            <span className="inline-flex items-center gap-1.5 rounded-md border border-lime-300/20 bg-lime-300/10 px-2.5 py-1 text-xs font-medium uppercase tracking-[0.16em] text-lime-100">
              <ShieldCheck className="h-3.5 w-3.5" />
              Local sandbox
            </span>
            {mission.status === "completed" && (
              <span className="inline-flex items-center gap-1.5 rounded-md border border-lime-300/20 bg-lime-300/10 px-2.5 py-1 text-xs font-medium text-lime-100">
                <CheckCircle2 className="h-3.5 w-3.5" />
                Completed
              </span>
            )}
          </div>
          <h1 className="text-3xl font-semibold leading-tight text-emerald-50">{mission.title}</h1>
          <p className="mt-4 max-w-3xl whitespace-pre-line text-sm leading-6 text-emerald-100/68 sm:text-base">
            {mission.story}
          </p>
        </div>

        <div className="grid min-w-0 grid-cols-2 gap-2 text-sm sm:grid-cols-4 lg:min-w-[26rem]">
          <span className="inline-flex items-center gap-1.5 rounded-md border border-lime-300/20 bg-lime-300/10 px-2.5 py-2 text-lime-100">
            <Star className="h-4 w-4 fill-lime-300 text-lime-300" />
            {mission.xp} XP
          </span>
          <span className="inline-flex items-center gap-1.5 rounded-md border border-white/10 bg-black/20 px-2.5 py-2 text-emerald-100/60">
            <Clock3 className="h-4 w-4" />
            {mission.estimatedMinutes}m
          </span>
          <span className="inline-flex items-center gap-1.5 rounded-md border border-white/10 bg-black/20 px-2.5 py-2 text-emerald-100/60 sm:col-span-2">
            <Server className="h-4 w-4 shrink-0" />
            <span className="truncate">{mission.services.join(" / ")}</span>
          </span>
        </div>
      </div>
    </div>
  );
}
