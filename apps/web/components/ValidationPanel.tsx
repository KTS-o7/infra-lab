"use client";

import { ValidationResult } from "@/lib/api";

interface Props {
  result: ValidationResult;
}

export default function ValidationPanel({ result }: Props) {
  return (
    <div className="rounded-xl border bg-slate-900 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-slate-100">Validation Results</h2>
        <span className={`text-sm font-medium px-3 py-1 rounded-full ${result.passed ? "bg-emerald-900 text-emerald-300 border border-emerald-700" : "bg-amber-900 text-amber-300 border border-amber-700"}`}>
          {result.passed ? "Passed" : "Partial"}
        </span>
      </div>

      {result.xpAwarded > 0 && (
        <div className="mb-4 p-3 rounded-lg bg-emerald-950 border border-emerald-800 text-center">
          <p className="text-lg font-bold text-emerald-300">+{result.xpAwarded} XP Awarded!</p>
        </div>
      )}

      <div className="space-y-2">
        {result.checks.map((check) => (
          <div
            key={check.id}
            className={`flex items-start gap-2 p-3 rounded-lg border ${
              check.passed
                ? "bg-emerald-950 border-emerald-800"
                : "bg-amber-950 border-amber-800"
            }`}
          >
            <span className={`mt-0.5 ${check.passed ? "text-emerald-400" : "text-amber-400"}`}>
              {check.passed ? "✓" : "✗"}
            </span>
            <div className="flex-1">
              <p className={`text-sm ${check.passed ? "text-emerald-300" : "text-amber-300"}`}>
                {check.message}
              </p>
              <p className="text-xs text-slate-500 mt-1">{check.type}</p>
            </div>
          </div>
        ))}
      </div>

      {!result.passed && (
        <p className="text-sm text-slate-400 mt-4">
          Attempt #{result.attemptNumber} — Fix the failed checks and try again.
        </p>
      )}
    </div>
  );
}