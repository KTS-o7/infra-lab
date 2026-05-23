"use client";

import { useMemo, useState } from "react";
import { ChevronDown, ClipboardCheck, Eye, Loader2, Target } from "lucide-react";
import type { MissionStep, ValidationResult } from "@/lib/api";
import CommandBlock from "./CommandBlock";
import ValidationPanel from "./ValidationPanel";

interface Props {
  step: MissionStep;
  command?: { id: string; label: string; command: string };
  result?: ValidationResult;
  disabled: boolean;
  onCheck: (stepId: string) => void;
}

export default function MissionStepCard({ step, command, result, disabled, onCheck }: Props) {
  const [showCommand, setShowCommand] = useState(false);
  const targetState = useMemo(() => step.targetState ?? [], [step.targetState]);

  return (
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

      <div className="grid gap-4 lg:grid-cols-2">
        <section className="rounded-md border border-white/10 bg-black/20 p-4">
          <h3 className="mb-2 flex items-center gap-2 text-sm font-semibold text-emerald-50">
            <Target className="h-4 w-4 text-lime-300" />
            Goal
          </h3>
          <p className="text-sm leading-6 text-emerald-100/68">{step.goal}</p>
        </section>

        <section className="rounded-md border border-white/10 bg-black/20 p-4">
          <h3 className="mb-2 text-sm font-semibold text-emerald-50">Why this matters</h3>
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

      <div className="mt-4 space-y-3">
        {command && (
          <div>
            <button
              onClick={() => setShowCommand((value) => !value)}
              className="inline-flex items-center gap-2 rounded-md border border-white/10 bg-white/[0.04] px-3 py-2 text-sm font-medium text-emerald-100/70 hover:bg-white/[0.075] hover:text-emerald-50"
            >
              {showCommand ? <ChevronDown className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              {showCommand ? "Hide CLI syntax" : "Show CLI syntax"}
            </button>
            {showCommand && (
              <div className="mt-3">
                <CommandBlock id={command.id} label={command.label} command={command.command} />
              </div>
            )}
          </div>
        )}

        <button
          onClick={() => onCheck(step.id)}
          disabled={disabled}
          className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-lime-300 px-4 py-3 font-semibold text-[#08110f] transition hover:bg-lime-200 disabled:opacity-50 sm:w-auto"
        >
          {disabled ? <Loader2 className="h-4 w-4 animate-spin" /> : <ClipboardCheck className="h-4 w-4" />}
          Check step
        </button>
      </div>

      {result && (
        <div className="mt-5">
          <ValidationPanel result={result} compact />
        </div>
      )}
    </div>
  );
}
