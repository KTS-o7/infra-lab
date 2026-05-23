"use client";

import { useEffect, useState, useCallback } from "react";
import { getMission, startMission, validateMission, resetMission, useHint as useHintApi, MissionDetail, ValidationResult } from "@/lib/api";
import CommandBlock from "./CommandBlock";
import ValidationPanel from "./ValidationPanel";
import HintPanel from "./HintPanel";
import ResetControl from "./ResetControl";
import RuntimeBanner from "./RuntimeBanner";
import { clsx } from "clsx";
import Link from "next/link";

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
      <div className="flex items-center justify-center py-24">
        <div className="animate-spin w-10 h-10 border-3 border-blue-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="text-center py-24">
        <p className="text-red-400 mb-4">{error || "Mission not found"}</p>
        <Link href="/" className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm">
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
        <Link href="/" className="text-sm text-slate-400 hover:text-slate-200 flex items-center gap-1 mb-4">
          <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
          </svg>
          Back to mission map
        </Link>

        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-slate-100">{mission.title}</h1>
              {isCompleted && (
                <span className="px-3 py-1 rounded-full text-xs font-medium bg-emerald-900 text-emerald-300 border border-emerald-700">
                  Completed
                </span>
              )}
            </div>
            <p className="text-slate-400 mb-4">{mission.summary}</p>
            <div className="flex items-center gap-4 text-sm text-slate-400">
              <span className="flex items-center gap-1">
                <span className="text-amber-400">⭐</span>
                {mission.xp} XP
              </span>
              <span>⏱ {mission.estimatedMinutes}m</span>
              <span>{mission.services.join(", ")}</span>
              <span className="capitalize">{mission.difficulty}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <div className="rounded-xl border border-slate-700 bg-slate-900 p-6">
            <h2 className="text-lg font-semibold text-slate-100 mb-3">Scenario</h2>
            <p className="text-slate-300 whitespace-pre-line">{mission.story}</p>
          </div>

          <div className="rounded-xl border border-slate-700 bg-slate-900 p-6">
            <h2 className="text-lg font-semibold text-slate-100 mb-3">Learning Objectives</h2>
            <ul className="space-y-2">
              {mission.learningObjectives.map((obj, i) => (
                <li key={i} className="flex items-start gap-2 text-slate-300">
                  <span className="text-blue-400 mt-1">✓</span>
                  {obj}
                </li>
              ))}
            </ul>
          </div>

          <div className="rounded-xl border border-slate-700 bg-slate-900 p-6">
            <h2 className="text-lg font-semibold text-slate-100 mb-4">Commands</h2>
            <div className="space-y-3">
              {mission.commands.map((cmd) => (
                <CommandBlock key={cmd.id} id={cmd.id} label={cmd.label} command={cmd.command} />
              ))}
            </div>
          </div>

          {mission.hints.length > 0 && (
            <HintPanel
              hints={mission.hints}
              onUseHint={handleUseHint}
              missionStarted={mission.status === "started" || mission.status === "completed"}
            />
          )}
        </div>

        <div className="space-y-4">
          <div className="rounded-xl border border-slate-700 bg-slate-900 p-6">
            <h2 className="text-lg font-semibold text-slate-100 mb-4">Actions</h2>
            <div className="space-y-3">
              {canStart && (
                <button
                  onClick={handleStart}
                  disabled={actionLoading}
                  className="w-full py-3 px-4 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-medium transition-colors"
                >
                  {actionLoading ? "Starting..." : "Start Mission"}
                </button>
              )}

              {canValidate && (
                <button
                  onClick={handleValidate}
                  disabled={actionLoading}
                  className="w-full py-3 px-4 rounded-lg bg-emerald-700 hover:bg-emerald-600 disabled:opacity-50 text-white font-medium transition-colors"
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
              <div className="mt-4 pt-4 border-t border-slate-700">
                <p className="text-sm text-slate-400">
                  Attempts: <span className="text-slate-200">{mission.progress.attempts}</span>
                </p>
                {mission.progress.xpAwarded > 0 && (
                  <p className="text-sm text-slate-400 mt-1">
                    XP Earned: <span className="text-amber-400">{mission.progress.xpAwarded}</span>
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