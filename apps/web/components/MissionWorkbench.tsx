"use client";

import { useMemo, useState } from "react";
import { CheckCircle2, Loader2 } from "lucide-react";
import type { MissionDetail, ValidationResult } from "@/lib/api";
import MissionBrief from "./MissionBrief";
import MissionStepList from "./MissionStepList";
import MissionStepCard from "./MissionStepCard";
import ResourceProofBoard from "./ResourceProofBoard";
import HintPanel from "./HintPanel";
import ResetControl from "./ResetControl";
import ValidationPanel from "./ValidationPanel";

interface Props {
  data: MissionDetail;
  actionLoading: boolean;
  validationResult: ValidationResult | null;
  onStart: () => void;
  onValidateMission: () => void;
  onValidateStep: (stepId: string) => Promise<ValidationResult | null>;
  onReset: (mode: string) => void;
  onUseHint: (hintId: string) => void;
}

export default function MissionWorkbench({
  data,
  actionLoading,
  validationResult,
  onStart,
  onValidateMission,
  onValidateStep,
  onReset,
  onUseHint,
}: Props) {
  const mission = data.mission;
  const steps = mission.steps ?? [];
  const [activeStepId, setActiveStepId] = useState(steps[0]?.id ?? null);
  const [resultsByStep, setResultsByStep] = useState<Record<string, ValidationResult>>({});

  const activeStep = useMemo(
    () => steps.find((step) => step.id === activeStepId) ?? steps[0],
    [activeStepId, steps],
  );
  const commandsById = useMemo(
    () => new Map(mission.commands.map((command) => [command.id, command])),
    [mission.commands],
  );

  const canStart = mission.status === "available";
  const canValidate = mission.status === "started" || mission.status === "completed";

  const handleCheckStep = async (stepId: string) => {
    const result = await onValidateStep(stepId);
    if (!result) return;
    setResultsByStep((current) => ({ ...current, [stepId]: result }));
    if (result.passed) {
      const currentIndex = steps.findIndex((step) => step.id === stepId);
      const nextStep = steps[currentIndex + 1];
      if (nextStep) setActiveStepId(nextStep.id);
    }
  };

  return (
    <div className="space-y-6">
      <MissionBrief mission={mission} />

      <div className="grid gap-6 xl:grid-cols-[18rem_minmax(0,1fr)_22rem]">
        <MissionStepList
          steps={steps}
          activeStepId={activeStep?.id ?? null}
          resultsByStep={resultsByStep}
          onSelect={setActiveStepId}
        />

        <div className="space-y-5">
          {activeStep && (
            <MissionStepCard
              step={activeStep}
              command={commandsById.get(activeStep.commandId)}
              result={resultsByStep[activeStep.id]}
              disabled={actionLoading || !canValidate}
              onCheck={handleCheckStep}
            />
          )}

          {(mission.hints ?? []).length > 0 && (
            <HintPanel
              hints={mission.hints ?? []}
              onUseHint={onUseHint}
              missionStarted={canValidate}
            />
          )}
        </div>

        <div className="space-y-4 xl:sticky xl:top-24 xl:self-start">
          <ResourceProofBoard
            steps={steps}
            resultsByStep={resultsByStep}
            latestMissionResult={validationResult}
          />

          <div className="rounded-lg border border-white/10 bg-[#0b1512]/80 p-5 shadow-2xl shadow-black/20 backdrop-blur">
            <p className="text-xs font-medium uppercase tracking-[0.18em] text-lime-200/75">Coach</p>
            <h2 className="mt-1 text-lg font-semibold text-emerald-50">Mission control</h2>
            <div className="mt-4 space-y-3">
              {canStart && (
                <button
                  onClick={onStart}
                  disabled={actionLoading}
                  className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-lime-300 px-4 py-3 font-semibold text-[#08110f] transition hover:bg-lime-200 disabled:opacity-50"
                >
                  {actionLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle2 className="h-4 w-4" />}
                  Start mission
                </button>
              )}

              {canValidate && (
                <button
                  onClick={onValidateMission}
                  disabled={actionLoading}
                  className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-lime-300 px-4 py-3 font-semibold text-[#08110f] transition hover:bg-lime-200 disabled:opacity-50"
                >
                  {actionLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle2 className="h-4 w-4" />}
                  Complete mission
                </button>
              )}

              <ResetControl missionId={mission.id} onReset={onReset} disabled={actionLoading} />
            </div>

            {mission.progress.attempts > 0 && (
              <div className="mt-4 border-t border-white/10 pt-4 text-sm text-emerald-100/55">
                Attempts: <span className="text-emerald-50">{mission.progress.attempts}</span>
                {mission.progress.xpAwarded > 0 && (
                  <span className="mt-1 block">
                    XP earned: <span className="text-lime-200">{mission.progress.xpAwarded}</span>
                  </span>
                )}
              </div>
            )}
          </div>

          {validationResult && <ValidationPanel result={validationResult} />}
        </div>
      </div>
    </div>
  );
}
