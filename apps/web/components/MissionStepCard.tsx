"use client";

import { useMemo } from "react";
import { Target, Wrench } from "lucide-react";
import type { MissionStep, ValidationResult } from "@/lib/api";
import ValidationPanel from "./ValidationPanel";
import MissionTerminalPanel from "./MissionTerminalPanel";

interface Props {
  step: MissionStep;
  command?: { id: string; label: string; command: string };
  result?: ValidationResult;
  canCheck: boolean;
  checking: boolean;
  onCheck: (stepId: string) => void;
}

export default function MissionStepCard({ step, command, result, canCheck, checking, onCheck }: Props) {
  const targetState = useMemo(() => step.targetState ?? [], [step.targetState]);

  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-white/10 bg-[#0b1512]/80 p-5 shadow-xl shadow-black/10 backdrop-blur sm:p-6">
      <div className="mb-5 flex items-start justify-between gap-4">
        <div>
          <p className="mb-2 text-xs font-medium uppercase tracking-[0.18em] text-lime-200/75">Active step</p>
          <h2 className="text-2xl font-semibold leading-tight text-emerald-50">{step.title}</h2>
        </div>
        {result && (
          <span className={`rounded-md border px-2.5 py-1 text-xs font-medium ${result.passed ? "border-lime-300/20 bg-lime-300/10 text-lime-100" : "border-amber-300/20 bg-amber-300/10 text-amber-100"}`}>
            {result.passed ? "Passed" : "Needs work"}
          </span>
        )}
      </div>

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_20rem]">
        <section className="rounded-md border border-white/10 bg-black/20 p-4">
          <h3 className="mb-2 flex items-center gap-2 text-sm font-semibold text-emerald-50">
            <Target className="h-4 w-4 text-lime-300" />
            Goal
          </h3>
          <p className="text-sm leading-6 text-emerald-100/68">{step.goal}</p>
        </section>

        <section className="rounded-md border border-white/10 bg-black/20 p-4">
          <h3 className="mb-2 flex items-center gap-2 text-sm font-semibold text-emerald-50">
            <Wrench className="h-4 w-4 text-lime-300" />
            Why this matters
          </h3>
          <p className="text-sm leading-6 text-emerald-100/68">{step.why || "This step creates part of the local infrastructure state required by the mission."}</p>
        </section>
      </div>

      {targetState.length > 0 && (
        <section className="mt-4 rounded-md border border-white/10 bg-black/20 p-4">
          <h3 className="mb-3 text-sm font-semibold text-emerald-50">Target state</h3>
          <div className="grid gap-2 sm:grid-cols-2">
            {targetState.map((item) => (
              <div key={`${item.label}-${item.value}`} className="rounded-md border border-white/10 bg-white/[0.035] p-3">
                <p className="text-xs uppercase tracking-[0.16em] text-emerald-100/38">{item.label}</p>
                <p className="mt-1 break-words font-mono text-sm text-emerald-50">{item.value}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      <section className="mt-4 rounded-md border border-white/10 bg-black/20 p-4">
        <h3 className="mb-2 text-sm font-semibold text-emerald-50">Try it</h3>
        <p className="text-sm leading-6 text-emerald-100/68">{step.action}</p>
        {step.notes && <p className="mt-2 text-sm leading-6 text-emerald-100/50">{step.notes}</p>}
      </section>

      </div>
      <MissionTerminalPanel
        command={command}
        canCheck={canCheck}
        checking={checking}
        onCheck={() => onCheck(step.id)}
      />

      {result && (
        <div>
          <ValidationPanel result={result} compact />
        </div>
      )}
    </div>
  );
}
