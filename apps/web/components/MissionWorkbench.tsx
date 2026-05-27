"use client";

import { useMemo, useState } from "react";
import { CheckCircle2, Loader2, ArrowRight, Map as MapIcon } from "lucide-react";
import Link from "next/link";
import type { MissionDetail, ResetMode, ValidationResult } from "@/lib/api";
import MissionBrief from "./MissionBrief";
import MissionStepList from "./MissionStepList";
import MissionStepCard from "./MissionStepCard";
import ResourceProofBoard from "./ResourceProofBoard";
import HintPanel from "./HintPanel";
import ResetControl from "./ResetControl";
import ValidationPanel from "./ValidationPanel";
import MissionWebTerminal from "./MissionWebTerminal";
import LearnMorePanel from "./LearnMorePanel";
import MissionChatPanel from "./MissionChatPanel";

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
  const serviceDesc =
    SERVICE_DESCRIPTIONS[primaryService.toLowerCase()] ??
    "distributed system patterns";

  return (
    <div className="rounded-lg border border-lime-500/30 bg-[#0b1512]/95 p-5 shadow-2xl shadow-black/20 backdrop-blur">
      <p className="text-xs font-medium uppercase tracking-[0.18em] text-lime-200/75">
        Mission complete
      </p>
      <h2 className="mt-1 text-lg font-semibold text-lime-300">
        Platform online: {primaryService.toUpperCase()}
      </h2>

      <div className="mt-4 space-y-4">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.1em] text-emerald-100/55">
            What was built
          </p>
          <p className="mt-1 text-sm text-emerald-50/80 leading-relaxed">
            {mission.summary}
          </p>
        </div>

        <div>
          <p className="text-xs font-medium uppercase tracking-[0.1em] text-emerald-100/55">
            Real systems
          </p>
          <p className="mt-1 text-sm text-emerald-50/80 leading-relaxed">
            In production AWS,{" "}
            <span className="text-lime-200">
              {primaryService.toUpperCase()}
            </span>{" "}
            provides {serviceDesc}.
          </p>
        </div>

        {nextMissionId ? (
          <div>
            <p className="text-xs font-medium uppercase tracking-[0.1em] text-emerald-100/55">
              What&apos;s next
            </p>
            <Link
              href={`/missions/${nextMissionId}`}
              className="mt-2 flex w-full items-center justify-between gap-3 rounded-md border border-lime-300/25 bg-lime-300/10 px-4 py-3 text-sm font-semibold text-lime-100 transition hover:border-lime-300/50 hover:bg-lime-300/20 hover:text-lime-200"
            >
              <span>Start next mission</span>
              <ArrowRight className="h-4 w-4 shrink-0" />
            </Link>
          </div>
        ) : (
          <div>
            <p className="text-xs font-medium uppercase tracking-[0.1em] text-emerald-100/55">
              What&apos;s next
            </p>
            <Link
              href="/"
              className="mt-2 flex w-full items-center justify-between gap-3 rounded-md border border-white/15 bg-white/[0.06] px-4 py-3 text-sm font-medium text-emerald-100 transition hover:border-lime-300/30 hover:bg-white/[0.10] hover:text-lime-200"
            >
              <span>Back to mission map</span>
              <MapIcon className="h-4 w-4 shrink-0" />
            </Link>
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
  onReset: (mode: ResetMode) => void;
  onUseHint: (hintId: string) => void;
  onUseLearnMore: (itemId: string) => Promise<void>;
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
  onUseLearnMore,
}: Props) {
  const mission = data.mission;
  const steps = mission.steps ?? [];
  const [activeStepId, setActiveStepId] = useState(steps[0]?.id ?? null);
  const [resultsByStep, setResultsByStep] = useState<
    Record<string, ValidationResult>
  >({});
  const [checkingStepId, setCheckingStepId] = useState<string | null>(null);

  const activeStep = useMemo(
    () => steps.find((step) => step.id === activeStepId) ?? steps[0],
    [activeStepId, steps],
  );
  const commandsById = useMemo(
    () => new Map(mission.commands.map((command) => [command.id, command])),
    [mission.commands],
  );

  const canStart = mission.status === "available";
  const canValidate =
    mission.status === "started" || mission.status === "completed";

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
            <p className="text-xs font-medium uppercase tracking-[0.18em] text-lime-200/75">
              Lab console
            </p>
            <h2 className="text-lg font-semibold text-emerald-50">
              Rebuild workspace
            </h2>
          </div>
          <div className="flex flex-wrap items-center gap-2 text-xs font-medium uppercase tracking-[0.14em] text-emerald-100/45">
            <span className="rounded-md border border-white/10 bg-black/20 px-2.5 py-1">
              Endpoint floci:4566
            </span>
            <span className="rounded-md border border-lime-300/20 bg-lime-300/10 px-2.5 py-1 text-lime-100">
              No real AWS
            </span>
          </div>
        </div>

        <div className="grid gap-0 xl:grid-cols-[18rem_minmax(0,1fr)_22rem]">
          <aside className="border-b border-white/10 p-4 xl:border-b-0 xl:border-r">
            <MissionStepList
              steps={steps}
              activeStepId={activeStep?.id ?? null}
              resultsByStep={resultsByStep}
              onSelect={setActiveStepId}
            />
          </aside>

          <main className="min-w-0 border-b border-white/10 p-4 sm:p-5 xl:border-b-0 xl:border-r">
            {activeStep && (
              <MissionStepCard
                step={activeStep}
                command={commandsById.get(activeStep.commandId)}
                result={resultsByStep[activeStep.id]}
                canCheck={canValidate}
                checking={checkingStepId === activeStep.id}
                onCheck={handleCheckStep}
              />
            )}

            <div className="mt-6">
              <MissionWebTerminal />
            </div>

            {(mission.hints ?? []).length > 0 && (
              <div className="mt-5">
                <HintPanel
                  hints={mission.hints ?? []}
                  onUseHint={onUseHint}
                  missionStarted={canValidate}
                />
              </div>
            )}

            {(mission.learnMore ?? []).length > 0 && (
              <div className="mt-5">
                <LearnMorePanel
                  items={mission.learnMore ?? []}
                  onUse={onUseLearnMore}
                />
              </div>
            )}

            <div className="mt-8">
              <MissionChatPanel missionId={mission.id} />
            </div>
          </main>

          <aside className="space-y-4 p-4 xl:sticky xl:top-24 xl:self-start">
            <ResourceProofBoard
              steps={steps}
              resultsByStep={resultsByStep}
              latestMissionResult={validationResult}
            />

            <div className="rounded-lg border border-white/10 bg-[#0b1512]/80 p-5 shadow-2xl shadow-black/20 backdrop-blur">
              <p className="text-xs font-medium uppercase tracking-[0.18em] text-lime-200/75">
                Coach
              </p>
              <h2 className="mt-1 text-lg font-semibold text-emerald-50">
                Mission control
              </h2>
              <div className="mt-4 space-y-3">
                {canStart && (
                  <button
                    onClick={onStart}
                    disabled={actionLoading}
                    className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-lime-300 px-4 py-3 font-semibold text-[#08110f] transition hover:bg-lime-200 disabled:opacity-50"
                  >
                    {actionLoading ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <CheckCircle2 className="h-4 w-4" />
                    )}
                    Start mission
                  </button>
                )}

                {canValidate && (
                  <button
                    onClick={onValidateMission}
                    disabled={actionLoading}
                    className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-lime-300 px-4 py-3 font-semibold text-[#08110f] transition hover:bg-lime-200 disabled:opacity-50"
                  >
                    {actionLoading ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <CheckCircle2 className="h-4 w-4" />
                    )}
                    Complete mission
                  </button>
                )}

                <ResetControl
                  missionId={mission.id}
                  onReset={onReset}
                  disabled={actionLoading}
                />
              </div>

              {mission.progress.attempts > 0 && (
                <div className="mt-4 border-t border-white/10 pt-4 text-sm text-emerald-100/55">
                  Attempts:{" "}
                  <span className="text-emerald-50">
                    {mission.progress.attempts}
                  </span>
                  {mission.progress.xpAwarded > 0 && (
                    <span className="mt-1 block">
                      XP earned:{" "}
                      <span className="text-lime-200">
                        {mission.progress.xpAwarded}
                      </span>
                    </span>
                  )}
                </div>
              )}
            </div>

            {validationResult && <ValidationPanel result={validationResult} />}

            {validationResult?.passed && mission.status === "completed" && (
              <MissionDebrief
                mission={mission}
                nextMissionId={validationResult.unlockedMissionIds?.[0]}
              />
            )}
          </aside>
        </div>
      </div>
    </div>
  );
}
