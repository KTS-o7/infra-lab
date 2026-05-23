"use client";

import { useEffect, useState, useCallback } from "react";
import { getMission, startMission, validateMission, resetMission, useHint as useHintApi, type MissionDetail, type ValidationResult } from "@/lib/api";
import CommandBlock from "./CommandBlock";
import ValidationPanel from "./ValidationPanel";
import HintPanel from "./HintPanel";
import ResetControl from "./ResetControl";
import RuntimeBanner from "./RuntimeBanner";
import Link from "next/link";
import { ArrowLeft, CheckCircle2, Clock3, Loader2, Server, Sparkles, Star, Target } from "lucide-react";

interface Props {
  missionId: string;
}

export default function MissionDetail({ missionId }: Props) {
  const [data, setData] = useState<MissionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    getMission(missionId)
      .then(setData)
      .catch(() => setError("Failed to load mission"))
      .finally(() => setLoading(false));
  }, [missionId]);

  useEffect(() => { load(); }, [load]);

  const handleStart = async () => {
    setActionLoading(true);
    try {
      await startMission(missionId);
      await load();
    } catch {
      setError("Failed to start mission");
    } finally {
      setActionLoading(false);
    }
  };

  const handleValidate = async () => {
    setActionLoading(true);
    setValidationResult(null);
    try {
      const result = await validateMission(missionId);
      setValidationResult(result);
      await load();
    } catch {
      setError("Failed to validate mission");
    } finally {
      setActionLoading(false);
    }
  };

  const handleReset = async (mode: string) => {
    setActionLoading(true);
    try {
      await resetMission(missionId, mode);
      setValidationResult(null);
      await load();
    } catch {
      setError("Failed to reset mission");
    } finally {
      setActionLoading(false);
    }
  };

  const handleUseHint = async (hintId: string) => {
    try {
      await useHintApi(missionId, hintId);
      await load();
    } catch {
      // ignore
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center rounded-lg border border-white/10 bg-white/[0.035] py-24">
        <Loader2 className="h-8 w-8 animate-spin text-lime-300" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="rounded-lg border border-red-400/20 bg-red-950/45 py-24 text-center">
        <p className="mb-4 text-red-200">{error || "Mission not found"}</p>
        <Link href="/" className="inline-flex items-center gap-2 rounded-md border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-emerald-50 hover:bg-white/[0.075]">
          <ArrowLeft className="h-4 w-4" />
          Back to missions
        </Link>
      </div>
    );
  }

  if (data.mission.status === "locked") {
    return (
      <div className="rounded-lg border border-red-400/20 bg-red-950/45 py-24 text-center">
        <p className="mb-4 text-red-200">This mission is locked.</p>
        <Link href="/" className="inline-flex items-center gap-2 rounded-md border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-emerald-50 hover:bg-white/[0.075]">
          <ArrowLeft className="h-4 w-4" />
          Back to missions
        </Link>
      </div>
    );
  }

  const mission = data.mission;
  const canStart = mission.status === "available";
  const canValidate = mission.status === "started" || mission.status === "completed";
  const isCompleted = mission.status === "completed";

  return (
    <div>
      <RuntimeBanner />

      <div className="mb-6">
        <Link href="/" className="mb-4 inline-flex items-center gap-2 text-sm text-emerald-100/55 hover:text-lime-200">
          <ArrowLeft className="h-4 w-4" />
          Back to mission map
        </Link>

        <div className="rounded-lg border border-white/10 bg-white/[0.045] p-5 shadow-2xl shadow-black/20 backdrop-blur sm:p-6">
          <div>
            <div className="mb-3 flex flex-wrap items-center gap-3">
              <h1 className="text-3xl font-semibold leading-tight text-emerald-50">{mission.title}</h1>
              {isCompleted && (
                <span className="inline-flex items-center gap-1.5 rounded-md border border-lime-300/20 bg-lime-300/10 px-3 py-1 text-xs font-medium text-lime-100">
                  <CheckCircle2 className="h-3.5 w-3.5" />
                  Completed
                </span>
              )}
            </div>
            <p className="mb-5 max-w-3xl text-sm leading-6 text-emerald-100/62 sm:text-base">{mission.summary}</p>
            <div className="flex flex-wrap items-center gap-2 text-sm">
              <span className="inline-flex items-center gap-1.5 rounded-md border border-lime-300/20 bg-lime-300/10 px-2.5 py-1 text-lime-100">
                <Star className="h-4 w-4 fill-lime-300 text-lime-300" />
                {mission.xp} XP
              </span>
              <span className="inline-flex items-center gap-1.5 rounded-md border border-white/10 bg-black/20 px-2.5 py-1 text-emerald-100/60">
                <Clock3 className="h-4 w-4" />
                {mission.estimatedMinutes}m
              </span>
              <span className="inline-flex items-center gap-1.5 rounded-md border border-white/10 bg-black/20 px-2.5 py-1 text-emerald-100/60">
                <Server className="h-4 w-4" />
                {mission.services.join(" / ")}
              </span>
              <span className="rounded-md border border-white/10 bg-black/20 px-2.5 py-1 text-emerald-100/60 capitalize">
                {mission.difficulty}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <div className="rounded-lg border border-white/10 bg-[#0b1512]/80 p-6 shadow-xl shadow-black/10 backdrop-blur">
            <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold text-emerald-50">
              <Sparkles className="h-5 w-5 text-lime-300" />
              Scenario
            </h2>
            <p className="whitespace-pre-line leading-7 text-emerald-100/68">{mission.story}</p>
          </div>

          <div className="rounded-lg border border-white/10 bg-[#0b1512]/80 p-6 shadow-xl shadow-black/10 backdrop-blur">
            <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-emerald-50">
              <Target className="h-5 w-5 text-lime-300" />
              Learning objectives
            </h2>
            <ul className="space-y-2">
              {mission.learningObjectives.map((obj, i) => (
                <li key={i} className="flex items-start gap-3 rounded-md border border-white/10 bg-white/[0.035] p-3 text-sm leading-6 text-emerald-100/68">
                  <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-lime-300" />
                  {obj}
                </li>
              ))}
            </ul>
          </div>

          <div className="rounded-lg border border-white/10 bg-[#0b1512]/80 p-6 shadow-xl shadow-black/10 backdrop-blur">
            <h2 className="mb-4 text-lg font-semibold text-emerald-50">Commands</h2>
            <div className="space-y-3">
              {mission.commands.map((cmd) => (
                <CommandBlock key={cmd.id} id={cmd.id} label={cmd.label} command={cmd.command} />
              ))}
            </div>
          </div>

          {(mission.hints ?? []).length > 0 && (
            <HintPanel
              hints={mission.hints ?? []}
              onUseHint={handleUseHint}
              missionStarted={mission.status === "started" || mission.status === "completed"}
            />
          )}
        </div>

        <div className="space-y-4">
          <div className="rounded-lg border border-white/10 bg-[#0b1512]/80 p-6 shadow-2xl shadow-black/20 backdrop-blur lg:sticky lg:top-24">
            <h2 className="mb-4 text-lg font-semibold text-emerald-50">Actions</h2>
            <div className="space-y-3">
              {canStart && (
                <button
                  onClick={handleStart}
                  disabled={actionLoading}
                  className="w-full rounded-md bg-lime-300 px-4 py-3 font-semibold text-[#08110f] transition hover:bg-lime-200 disabled:opacity-50"
                >
                  {actionLoading ? "Starting..." : "Start Mission"}
                </button>
              )}

              {canValidate && (
                <button
                  onClick={handleValidate}
                  disabled={actionLoading}
                  className="w-full rounded-md bg-lime-300 px-4 py-3 font-semibold text-[#08110f] transition hover:bg-lime-200 disabled:opacity-50"
                >
                  {actionLoading ? "Validating..." : "Validate"}
                </button>
              )}

              <ResetControl
                missionId={missionId}
                onReset={handleReset}
                disabled={actionLoading}
              />
            </div>

            {mission.progress.attempts > 0 && (
              <div className="mt-4 border-t border-white/10 pt-4">
                <p className="text-sm text-emerald-100/55">
                  Attempts: <span className="text-emerald-50">{mission.progress.attempts}</span>
                </p>
                {mission.progress.xpAwarded > 0 && (
                  <p className="mt-1 text-sm text-emerald-100/55">
                    XP earned: <span className="text-lime-200">{mission.progress.xpAwarded}</span>
                  </p>
                )}
              </div>
            )}
          </div>

          {validationResult && (
            <ValidationPanel result={validationResult} />
          )}
        </div>
      </div>
    </div>
  );
}
