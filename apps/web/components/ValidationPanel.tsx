"use client";

import { ValidationResult } from "@/lib/api";
import { CheckCircle2, XCircle } from "lucide-react";
import CapstoneScorePanel from "./CapstoneScorePanel";

interface Props {
  result: ValidationResult;
  compact?: boolean;
}

export default function ValidationPanel({ result, compact = false }: Props) {
  return (
    <div
      role="status"
      aria-live="polite"
      tabIndex={-1}
      className={`rounded-lg border border-white/10 bg-[#0b1512]/80 shadow-xl shadow-black/10 backdrop-blur ${compact ? "p-4" : "p-6"}`}
    >
      <div className="mb-4 flex items-center justify-between gap-3">
        <h2 className={`${compact ? "text-base" : "text-lg"} font-semibold text-emerald-50`}>
          {result.scope === "step" ? "Step check" : "Validation results"}
        </h2>
        <span className={`rounded-md border px-3 py-1 text-sm font-medium ${result.passed ? "border-lime-300/20 bg-lime-300/10 text-lime-100" : "border-amber-300/20 bg-amber-300/10 text-amber-100"}`}>
          {result.passed ? "Passed" : "Partial"}
        </span>
      </div>

      {result.xpAwarded > 0 && (
        <div className="mb-4 rounded-md border border-lime-300/20 bg-lime-300/10 p-3 text-center">
          <p className="text-lg font-semibold text-lime-100">+{result.xpAwarded} XP awarded</p>
        </div>
      )}

      {result.capstoneScore ? (
        <div className="mb-4">
          <CapstoneScorePanel score={result.capstoneScore} />
        </div>
      ) : null}

      <div className="space-y-2">
        {result.checks.length === 0 ? (
          <div className="rounded-lg border border-lime-300/20 bg-lime-300/10 p-3">
            <p className="text-sm text-lime-100">
              {result.message ?? "This step has no direct proof check. The full mission validation proves it with the rest of the workflow."}
            </p>
          </div>
        ) : result.checks.map((check) => (
          <div
            key={check.id}
            className={`flex items-start gap-2 p-3 rounded-lg border ${
              check.passed
                ? "border-lime-300/20 bg-lime-300/10"
                : "border-amber-300/20 bg-amber-300/10"
            }`}
          >
            {check.passed ? (
              <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-lime-300" />
            ) : (
              <XCircle className="mt-0.5 h-4 w-4 shrink-0 text-amber-300" />
            )}
            <div className="flex-1">
              <p className={`text-sm ${check.passed ? "text-lime-100" : "text-amber-100"}`}>
                {check.message}
              </p>
              <p className="mt-1 text-xs text-emerald-100/42">{check.type}</p>
            </div>
          </div>
        ))}
      </div>

      {!result.passed && (
        <p className="mt-4 text-sm text-emerald-100/55">
          Attempt #{result.attemptNumber} — Fix the failed checks and try again.
        </p>
      )}
    </div>
  );
}
