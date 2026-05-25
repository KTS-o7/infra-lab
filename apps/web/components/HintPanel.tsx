"use client";

import { HelpCircle, Lock, Search, Wrench } from "lucide-react";
import { clsx } from "clsx";
import type { MissionHint } from "@/lib/api";

const levelIcon = {
  nudge: HelpCircle,
  diagnosis: Search,
  repair: Wrench,
};

interface Props {
  hints: MissionHint[];
  onUseHint: (hintId: string) => void;
  missionStarted: boolean;
}

export default function HintPanel({ hints, onUseHint, missionStarted }: Props) {
  return (
    <div className="rounded-lg border border-white/10 bg-[#0b1512]/80 p-6 shadow-xl shadow-black/10 backdrop-blur">
      <h2 className="mb-4 text-lg font-semibold text-emerald-50">Hints</h2>
      <div className="space-y-3">
        {hints.map((hint) => (
          <div key={hint.id} className="rounded-md border border-white/10 bg-black/25 p-4">
            <div className="mb-2 flex items-center justify-between gap-3">
              <div className="flex min-w-0 flex-wrap items-center gap-2">
                {(() => {
                  const Icon = levelIcon[hint.level as keyof typeof levelIcon] ?? HelpCircle;
                  return <Icon className="h-4 w-4 shrink-0 text-lime-300" />;
                })()}
                <span className="text-sm font-medium text-emerald-50">{hint.title}</span>
                {hint.level && (
                  <span className="rounded-md border border-white/10 bg-white/[0.035] px-2 py-0.5 text-xs text-emerald-100/48">
                    {hint.level}
                  </span>
                )}
                {hint.penaltyXp > 0 && (
                  <span className="text-xs text-amber-300">-{hint.penaltyXp} XP</span>
                )}
              </div>
              {!hint.revealed && missionStarted && (
                <button
                  onClick={() => onUseHint(hint.id)}
                  className="shrink-0 rounded-md border border-white/10 bg-white/[0.04] px-3 py-1.5 text-xs text-emerald-100/65 hover:bg-white/[0.075] hover:text-emerald-50"
                >
                  Reveal
                </button>
              )}
            </div>
            {hint.revealed && hint.text && (
              <p className="text-sm leading-6 text-emerald-100/62">{hint.text}</p>
            )}
            {!hint.revealed && (
              <p className={clsx("flex items-center gap-2 text-sm italic", missionStarted ? "text-emerald-100/42" : "text-emerald-100/32")}>
                {!missionStarted && <Lock className="h-3.5 w-3.5" />}
                {missionStarted ? "Reveal this staged hint when you need the next diagnostic move." : "Start the mission to reveal hints."}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
