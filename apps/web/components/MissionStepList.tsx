import { CheckCircle2, Circle, CircleAlert, CircleDashed, PlayCircle } from "lucide-react";
import { clsx } from "clsx";
import type { MissionStep, StepProgress, ValidationResult } from "@/lib/api";

interface Props {
  steps: MissionStep[];
  activeStepId: string | null;
  resultsByStep: Record<string, ValidationResult>;
  progressByStep?: Record<string, StepProgress>;
  onSelect: (stepId: string) => void;
}

export default function MissionStepList({ steps, activeStepId, resultsByStep, progressByStep = {}, onSelect }: Props) {
  return (
    <div className="rounded-lg border border-white/10 bg-[#0b1512]/80 p-4 shadow-xl shadow-black/10 backdrop-blur">
      <div className="mb-4">
        <p className="text-xs font-medium uppercase tracking-[0.18em] text-lime-200/75">Build path</p>
        <h2 className="mt-1 text-lg font-semibold text-emerald-50">Mission steps</h2>
      </div>
      <div className="space-y-2">
        {steps.map((step, index) => {
          const result = resultsByStep[step.id];
          const progress = progressByStep[step.id];
          const active = step.id === activeStepId;
          const passed = result?.passed || progress?.status === "passed";
          const blocked = progress?.status === "blocked";
          const failed = result?.passed === false || progress?.status === "failed";
          const Icon = passed ? CheckCircle2 : blocked ? CircleDashed : failed ? CircleAlert : active ? PlayCircle : Circle;

          return (
            <button
              key={step.id}
              onClick={() => onSelect(step.id)}
              aria-current={active ? "step" : undefined}
              className={clsx(
                "flex min-h-10 w-full items-start gap-3 rounded-md border p-3 text-left transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-lime-300 focus-visible:ring-offset-2 focus-visible:ring-offset-[#0b1512]",
                active
                  ? "border-lime-300/30 bg-lime-300/10"
                  : blocked
                    ? "border-white/10 bg-white/[0.02] opacity-70 hover:bg-white/[0.04]"
                    : "border-white/10 bg-white/[0.03] hover:bg-white/[0.06]",
              )}
            >
              <Icon className={clsx("mt-0.5 h-4 w-4 shrink-0", passed ? "text-lime-300" : failed ? "text-amber-300" : active ? "text-lime-200" : "text-emerald-100/35")} />
              <span className="min-w-0">
                <span className="block text-xs uppercase tracking-[0.16em] text-emerald-100/38">Step {index + 1}</span>
                <span className="mt-0.5 block text-sm font-medium text-emerald-50">{step.title}</span>
                <span className="mt-1 line-clamp-2 block text-xs leading-5 text-emerald-100/50">{step.goal}</span>
                {progress?.status && progress.status !== "not_started" && (
                  <span className="mt-1 block text-xs text-emerald-100/38">{progress.status.replace("_", " ")}</span>
                )}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
