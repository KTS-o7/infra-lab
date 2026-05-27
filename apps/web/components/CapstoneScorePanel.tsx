"use client";

import { Award, ShieldCheck, TrendingUp } from "lucide-react";
import type { CapstoneScore } from "@/lib/api";

interface Props {
  score?: CapstoneScore | null;
}

export default function CapstoneScorePanel({ score }: Props) {
  if (!score) return null;

  const currentScore = score.score ?? score.latestScore ?? null;
  const mastery = score.masteryLevel ?? score.latestMasteryLevel ?? null;
  const bestScore = score.bestScore ?? null;
  const bestMastery = score.bestMasteryLevel ?? null;

  return (
    <section className="rounded-lg border border-amber-300/20 bg-amber-300/10 p-4 text-amber-50">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.16em] text-amber-100/70">Capstone mastery</p>
          <h3 className="mt-1 text-lg font-semibold text-amber-50">
            {currentScore === null ? "Score pending" : `${currentScore}/95`}
          </h3>
        </div>
        <Award className="h-5 w-5 shrink-0 text-amber-200" />
      </div>

      <div className="mt-4 grid gap-2 text-sm sm:grid-cols-2">
        <div className="rounded-md border border-white/10 bg-black/15 p-3">
          <p className="text-xs uppercase tracking-[0.12em] text-amber-100/55">Latest level</p>
          <p className="mt-1 font-medium text-amber-50">{formatLevel(mastery)}</p>
        </div>
        <div className="rounded-md border border-white/10 bg-black/15 p-3">
          <p className="text-xs uppercase tracking-[0.12em] text-amber-100/55">Best replay</p>
          <p className="mt-1 font-medium text-amber-50">
            {bestScore === null ? "Not recorded" : `${bestScore}/95`}
            {bestMastery ? ` · ${formatLevel(bestMastery)}` : ""}
          </p>
        </div>
      </div>

      {typeof score.localSafetyPassed === "boolean" ? (
        <div className="mt-3 flex items-start gap-2 rounded-md border border-white/10 bg-black/15 p-3 text-sm">
          <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-lime-200" />
          <p>{score.localSafetyPassed ? "Local safety gate passed." : "Local safety gate failed. Recheck the local runtime before replaying."}</p>
        </div>
      ) : null}

      {score.dimensions?.length ? (
        <div className="mt-3 space-y-2">
          {score.dimensions.map((dimension, index) => (
            <div key={dimension.id ?? index} className="rounded-md border border-white/10 bg-black/15 p-3">
              <div className="flex items-center justify-between gap-3 text-sm">
                <span className="font-medium text-amber-50">{dimension.label ?? dimension.id ?? "Dimension"}</span>
                <span className="text-amber-100/80">
                  {dimension.score ?? 0}/{dimension.maxScore ?? "-"}
                </span>
              </div>
              {dimension.notes ? <p className="mt-1 text-xs leading-5 text-amber-100/65">{dimension.notes}</p> : null}
            </div>
          ))}
        </div>
      ) : null}

      {bestScore !== null && currentScore !== null && bestScore > currentScore ? (
        <div className="mt-3 flex items-start gap-2 text-sm text-amber-100/75">
          <TrendingUp className="mt-0.5 h-4 w-4 shrink-0" />
          <p>Your best score is preserved even when a replay scores lower.</p>
        </div>
      ) : null}
    </section>
  );
}

function formatLevel(level?: string | null) {
  if (!level) return "Not recorded";
  return level.replaceAll("_", " ");
}
