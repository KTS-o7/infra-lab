"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { CheckCircle2, Loader2, ArrowRight, BookOpen, Lock } from "lucide-react";
import type { MissionDetail, MissionHint, StepProgress, ValidationResult } from "@/lib/api";
import MissionBrief from "./MissionBrief";
import MissionStepList from "./MissionStepList";
import MissionStepCard from "./MissionStepCard";
import ResourceProofBoard from "./ResourceProofBoard";
import HintPanel from "./HintPanel";
import ResetControl from "./ResetControl";
import ValidationPanel from "./ValidationPanel";
import CapstoneScorePanel from "./CapstoneScorePanel";
import CourseContinuityPanel from "./CourseContinuityPanel";

const SERVICE_DESCRIPTIONS: Record<string, string> = {
  sns: "push-based messaging for pub/sub and mobile notifications",
  sqs: "pull-based message queuing for decoupled processing",
  lambda: "serverless functions for event-driven compute",
  apigateway: "managed API endpoint service with routing and throttling",
  dynamodb: "NoSQL database with on-demand scaling",
  s3: "object storage for static assets and data lakes",
  ecs: "container orchestration for Docker workloads",
  eks: "managed Kubernetes for production container deployments",
};

interface MissionDebriefProps {
  mission: MissionDetail["mission"];
  nextMissionId?: string;
}

function MissionDebrief({ mission, nextMissionId }: MissionDebriefProps) {
  const primaryService = mission.services?.[0] ?? "";
  const serviceDesc = SERVICE_DESCRIPTIONS[primaryService.toLowerCase()] ?? "distributed system patterns";

  return (
    <div className="rounded-lg border border-lime-500/30 bg-[#0b1512]/95 p-5 shadow-2xl shadow-black/20 backdrop-blur">
      <p className="text-xs font-medium uppercase tracking-[0.18em] text-lime-200/75">Mission complete</p>
      <h2 className="mt-1 text-lg font-semibold text-lime-300">
        Platform online: {primaryService.toUpperCase()}
      </h2>

      <div className="mt-4 space-y-4">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.1em] text-emerald-100/55">What was built</p>
          <p className="mt-1 text-sm text-emerald-50/80 leading-relaxed">
            {mission.debrief || mission.summary}
          </p>
        </div>

        <div>
          <p className="text-xs font-medium uppercase tracking-[0.1em] text-emerald-100/55">Real systems</p>
          <p className="mt-1 text-sm text-emerald-50/80 leading-relaxed">
            In production AWS, <span className="text-lime-200">{primaryService.toUpperCase()}</span> provides {serviceDesc}.
          </p>
        </div>

        {nextMissionId && (
          <div>
            <p className="text-xs font-medium uppercase tracking-[0.1em] text-emerald-100/55">What&apos;s next</p>
            <div className="mt-2 flex items-center gap-2 rounded border border-white/10 bg-white/5 p-3">
              <ArrowRight className="h-4 w-4 flex-shrink-0 text-lime-300" />
              <span className="text-sm text-emerald-50/80">Mission unlock: {nextMissionId}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

interface Props {
  data: MissionDetail;
  actionLoading: boolean;
  validationResult: ValidationResult | null;
  onStart: () => void;
  onValidateMission: () => void;
  onValidateStep: (stepId: string) => Promise<ValidationResult | null>;
  onReset: (mode: string) => void;
  onUseHint: (hintId: string) => void;
  runtimeReady?: boolean;
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
  runtimeReady = true,
}: Props) {
  const mission = data.mission;
  const steps = mission.steps ?? [];
  const progressByStep = useMemo(() => buildProgressByStep(mission.stepProgress ?? []), [mission.stepProgress]);
  const initialActiveStepId = useMemo(
    () => firstIncompleteStepId(steps, progressByStep),
    [steps, progressByStep],
  );
  const [activeStepId, setActiveStepId] = useState(initialActiveStepId);
  const initialResultsByStep = useMemo(() => buildResultsFromProgress(mission.id, mission.stepProgress ?? []), [mission.id, mission.stepProgress]);
  const [resultsByStep, setResultsByStep] = useState<Record<string, ValidationResult>>(initialResultsByStep);
  const [checkingStepId, setCheckingStepId] = useState<string | null>(null);

  useEffect(() => {
    setResultsByStep(initialResultsByStep);
  }, [initialResultsByStep]);

  useEffect(() => {
    setActiveStepId(initialActiveStepId);
  }, [initialActiveStepId, mission.id]);

  const activeStep = useMemo(
    () => steps.find((step) => step.id === activeStepId) ?? steps[0],
    [activeStepId, steps],
  );
  const commandsById = useMemo(
    () => new Map(mission.commands.map((command) => [command.id, command])),
    [mission.commands],
  );

  const revealedHintIds = useMemo(() => new Set((mission.helpUsage ?? []).map((usage) => usage.hintId)), [mission.helpUsage]);
  const hints = useMemo(
    () => (mission.hints ?? []).map((hint): MissionHint => ({ ...hint, revealed: hint.revealed ?? hint.isUsed ?? revealedHintIds.has(hint.id) })),
    [mission.hints, revealedHintIds],
  );

  const canStart = mission.status === "available" && runtimeReady;
  const canShowStart = mission.status === "available";
  const canValidateMission = (mission.status === "started" || mission.status === "completed") && runtimeReady;
  const isLocked = mission.status === "locked";
  const isCapstone = mission.missionType === "module_capstone" || mission.missionType === "final_capstone";
  const activeStepProgress = activeStep ? progressByStep[activeStep.id] : undefined;
  const activeStepBlocked = activeStepProgress?.status === "blocked";
  const canValidateActiveStep = canValidateMission && !activeStepBlocked;
  const checkDisabledReason = !runtimeReady ? "Runtime offline" : isLocked ? "Mission locked" : activeStepBlocked ? "Step blocked" : "Start mission first";

  const handleCheckStep = async (stepId: string) => {
    setCheckingStepId(stepId);
    const result = await onValidateStep(stepId);
    setCheckingStepId(null);
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

      <div className="overflow-hidden rounded-lg border border-white/10 bg-[#07100d]/90 shadow-2xl shadow-black/30">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 bg-white/[0.03] px-5 py-3">
          <div>
            <p className="text-xs font-medium uppercase tracking-[0.18em] text-lime-200/75">Lab console</p>
            <h2 className="text-lg font-semibold text-emerald-50">Rebuild workspace</h2>
          </div>
          <div className="flex flex-wrap items-center gap-2 text-xs font-medium uppercase tracking-[0.14em] text-emerald-100/45">
            <span className="rounded-md border border-white/10 bg-black/20 px-2.5 py-1">Endpoint localhost:4566</span>
            <span className="rounded-md border border-lime-300/20 bg-lime-300/10 px-2.5 py-1 text-lime-100">No real AWS</span>
          </div>
        </div>

        <div className="grid gap-0 xl:grid-cols-[18rem_minmax(0,1fr)_22rem]">
          <main className="min-w-0 border-b border-white/10 p-4 sm:p-5 xl:order-2 xl:border-b-0 xl:border-r">
            {isLocked ? (
              <div className="rounded-lg border border-amber-300/20 bg-amber-300/10 p-5">
                <div className="flex items-start gap-3">
                  <Lock className="mt-0.5 h-5 w-5 shrink-0 text-amber-200" />
                  <div>
                    <h3 className="font-semibold text-amber-50">Mission locked</h3>
                    <p className="mt-2 text-sm leading-6 text-amber-100/75">
                      Complete the prerequisite mission{(mission.prerequisites ?? []).length === 1 ? "" : "s"} before starting this workbench.
                    </p>
                    {(mission.prerequisites ?? []).length > 0 ? (
                      <div className="mt-3 flex flex-wrap gap-2">
                        {(mission.prerequisites ?? []).map((prerequisite) => (
                          <Link key={prerequisite} href={`/missions/${prerequisite}`} className="rounded-md border border-white/10 bg-black/15 px-2 py-1 text-xs text-amber-100 transition hover:border-amber-200/30 hover:bg-amber-200/10">
                            {prerequisite}
                          </Link>
                        ))}
                      </div>
                    ) : null}
                  </div>
                </div>
              </div>
            ) : activeStep ? (
              <MissionStepCard
                step={activeStep}
                command={commandsById.get(activeStep.commandId)}
                result={resultsByStep[activeStep.id]}
                progress={activeStepProgress}
                canCheck={canValidateActiveStep}
                checking={checkingStepId === activeStep.id}
                disabledReason={checkDisabledReason}
                onCheck={handleCheckStep}
              />
            ) : null}

            {!isLocked && hints.length > 0 && (
              <div className="mt-5">
                <HintPanel
                  hints={hints}
                  onUseHint={onUseHint}
                  missionStarted={canValidateMission}
                />
              </div>
            )}
          </main>

          <aside className="border-b border-white/10 p-4 xl:order-1 xl:border-b-0 xl:border-r">
            <MissionStepList
              steps={steps}
              activeStepId={activeStep?.id ?? null}
              resultsByStep={resultsByStep}
              progressByStep={progressByStep}
              onSelect={setActiveStepId}
            />
          </aside>

          <aside className="space-y-4 p-4 xl:order-3 xl:sticky xl:top-24 xl:self-start">
            <ResourceProofBoard
              steps={steps}
              resultsByStep={resultsByStep}
              progressByStep={progressByStep}
              latestMissionResult={validationResult}
            />

            {isLocked && (
              <div className="rounded-lg border border-amber-300/20 bg-amber-300/10 p-4 text-sm text-amber-100">
                <div className="flex items-start gap-2">
                  <Lock className="mt-0.5 h-4 w-4 shrink-0" />
                  <p>This mission is locked until its prerequisites are complete.</p>
                </div>
              </div>
            )}

            <div className="rounded-lg border border-white/10 bg-[#0b1512]/80 p-5 shadow-2xl shadow-black/20 backdrop-blur">
            <p className="text-xs font-medium uppercase tracking-[0.18em] text-lime-200/75">Coach</p>
            <h2 className="mt-1 text-lg font-semibold text-emerald-50">Mission control</h2>
            <div className="mt-4 space-y-3">
              {canShowStart && (
                <button
                  onClick={onStart}
                  disabled={actionLoading || !canStart}
                  className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-lime-300 px-4 py-3 font-semibold text-[#08110f] transition hover:bg-lime-200 disabled:opacity-50"
                >
                  {actionLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle2 className="h-4 w-4" />}
                  {runtimeReady ? "Start mission" : "Runtime offline"}
                </button>
              )}

              {(mission.status === "started" || mission.status === "completed") && (
                <button
                  onClick={onValidateMission}
                  disabled={actionLoading || !runtimeReady}
                  className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-lime-300 px-4 py-3 font-semibold text-[#08110f] transition hover:bg-lime-200 disabled:opacity-50"
                >
                  {actionLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle2 className="h-4 w-4" />}
                  {runtimeReady ? "Complete mission" : "Runtime offline"}
                </button>
              )}

              <ResetControl missionId={mission.id} onReset={onReset} disabled={actionLoading || !runtimeReady} />
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
            {(mission.stepProgress ?? []).length > 0 && (
              <div className="mt-4 border-t border-white/10 pt-4 text-sm text-emerald-100/55">
                Step progress:{" "}
                <span className="text-emerald-50">
                  {(mission.stepProgress ?? []).filter((step) => step.status === "passed").length}/{steps.length}
                </span>
              </div>
            )}
          </div>

          {validationResult && <ValidationPanel result={validationResult} />}

          {isCapstone && !validationResult?.capstoneScore ? (
            <CapstoneScorePanel score={mission.progress.capstoneScore} />
          ) : null}

          {mission.status === "completed" && (
            <MissionDebrief
              mission={mission}
              nextMissionId={validationResult?.unlockedMissionIds?.[0]}
            />
          )}

          {mission.status !== "completed" && (
            <div className="rounded-lg border border-white/10 bg-[#0b1512]/80 p-4 text-sm text-emerald-100/55">
              <div className="flex items-start gap-2">
                <BookOpen className="mt-0.5 h-4 w-4 shrink-0 text-lime-300" />
                <p>Debrief unlocks after the full mission validation passes.</p>
              </div>
            </div>
          )}

          <CourseContinuityPanel currentMissionId={mission.id} currentCapability={mission.capability} />
          </aside>
        </div>
      </div>
    </div>
  );
}

function buildProgressByStep(stepProgress: StepProgress[]) {
  const progressByStep: Record<string, StepProgress> = {};
  for (const progress of stepProgress) progressByStep[progress.stepId] = progress;
  return progressByStep;
}

function buildResultsFromProgress(missionId: string, stepProgress: StepProgress[]) {
  const resultsByStep: Record<string, ValidationResult> = {};
  for (const progress of stepProgress) {
    if (!progress.latestChecks?.length) continue;
    resultsByStep[progress.stepId] = {
      missionId,
      passed: progress.latestChecks.every((check) => check.passed),
      status: progress.status,
      xpAwarded: 0,
      attemptNumber: progress.attempts,
      checks: progress.latestChecks,
      unlockedMissionIds: [],
      scope: "step",
      stepId: progress.stepId,
    };
  }
  return resultsByStep;
}

function firstIncompleteStepId(steps: MissionDetail["mission"]["steps"], progressByStep: Record<string, StepProgress>) {
  const firstIncomplete = steps.find((step) => progressByStep[step.id]?.status !== "passed");
  return firstIncomplete?.id ?? steps[0]?.id ?? null;
}
