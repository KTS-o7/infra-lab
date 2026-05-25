import { CheckCircle2, CircleDashed, Database, FileText, Globe, HelpCircle, MessageSquare, Package, XCircle, Zap } from "lucide-react";
import type { MissionStep, StepProgress, ValidationResult } from "@/lib/api";

interface Props {
  steps: MissionStep[];
  resultsByStep: Record<string, ValidationResult>;
  progressByStep?: Record<string, StepProgress>;
  latestMissionResult?: ValidationResult | null;
}

type ProofState = "pending" | "passed" | "failed" | "stale" | "no_checks";

export default function ResourceProofBoard({ steps, resultsByStep, progressByStep = {}, latestMissionResult }: Props) {
  const rows = buildProofRows(steps, resultsByStep, progressByStep, latestMissionResult);

  return (
    <div className="rounded-lg border border-white/10 bg-[#0b1512]/80 p-5 shadow-xl shadow-black/10 backdrop-blur">
      <div className="mb-4">
        <p className="text-xs font-medium uppercase tracking-[0.18em] text-lime-200/75">Lab proof</p>
        <h2 className="mt-1 text-lg font-semibold text-emerald-50">Resource state</h2>
      </div>
      <div className="space-y-2">
        {rows.map((row) => {
          const Icon = iconFor(row.kind);
          const StateIcon = stateIcon(row.state);
          return (
            <div key={row.id} className="flex items-start gap-3 rounded-md border border-white/10 bg-black/20 p-3">
              <Icon className="mt-0.5 h-4 w-4 shrink-0 text-lime-300" />
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-emerald-50">{row.label}</p>
                <p className="mt-1 break-words font-mono text-xs leading-5 text-emerald-100/48">{row.value}</p>
                {row.state === "stale" ? (
                  <p className="mt-1 text-xs leading-5 text-amber-100/70">Proof was valid before reset. Re-check this step.</p>
                ) : row.state === "no_checks" ? (
                  <p className="mt-1 text-xs leading-5 text-emerald-100/55">Final mission validation proves this step.</p>
                ) : null}
              </div>
              <StateIcon className={`mt-0.5 h-4 w-4 shrink-0 ${row.state === "passed" ? "text-lime-300" : row.state === "failed" || row.state === "stale" ? "text-amber-300" : "text-emerald-100/32"}`} />
            </div>
          );
        })}
      </div>
    </div>
  );
}

function buildProofRows(
  steps: MissionStep[],
  resultsByStep: Record<string, ValidationResult>,
  progressByStep: Record<string, StepProgress>,
  latestMissionResult?: ValidationResult | null,
) {
  const checks = new Map<string, { passed: boolean }>();
  for (const progress of Object.values(progressByStep)) {
    for (const check of progress.latestChecks ?? []) checks.set(check.id, { passed: check.passed });
  }
  for (const result of Object.values(resultsByStep)) {
    for (const check of result.checks) checks.set(check.id, { passed: check.passed });
  }
  for (const check of latestMissionResult?.checks ?? []) checks.set(check.id, { passed: check.passed });

  const rows = [];
  for (const step of steps) {
    const state = stateFor(step, checks, progressByStep[step.id]);
    if (step.targetState.length === 0) {
      rows.push({ id: step.id, kind: "generic", label: step.title, value: step.goal, state });
      continue;
    }
    for (const item of step.targetState) {
      rows.push({
        id: `${step.id}-${item.label}-${item.value}`,
        kind: kindFor(item.label, item.value),
        label: item.label,
        value: item.value,
        state,
      });
    }
  }
  return rows;
}

function stateFor(step: MissionStep, checks: Map<string, { passed: boolean }>, progress?: StepProgress): ProofState {
  if (progress?.status === "stale") return "stale";
  if (progress?.status === "no_checks" || step.checkIds.length === 0) return "no_checks";
  if (!step.checkIds.some((id) => checks.has(id))) return "pending";
  return step.checkIds.every((id) => checks.get(id)?.passed) ? "passed" : "failed";
}

function kindFor(label: string, value: string) {
  const text = `${label} ${value}`.toLowerCase();
  if (text.includes("function") && !text.includes("api")) return "compute";
  if (text.includes("route") || text.includes("endpoint") || text.includes("api")) return "endpoint";
  if (text.includes("bucket") || text.includes("queue") || text.includes("topic")) return "resource";
  if (text.includes("object") || text.includes("body") || text.includes("message")) return "payload";
  if (text.includes("table")) return "database";
  return "generic";
}

function iconFor(kind: string) {
  if (kind === "compute") return Zap;
  if (kind === "endpoint") return Globe;
  if (kind === "database") return Database;
  if (kind === "payload") return FileText;
  if (kind === "resource") return Package;
  if (kind === "message") return MessageSquare;
  return HelpCircle;
}

function stateIcon(state: ProofState) {
  if (state === "passed") return CheckCircle2;
  if (state === "failed") return XCircle;
  return CircleDashed;
}
