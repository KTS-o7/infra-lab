"use client";

import { useEffect, useState, useCallback } from "react";
import {
  getMission,
  startMission,
  validateMission,
  resetMission,
  useHint as useHintApi,
  useLearnMore,
  type MissionDetail,
  type ResetMode,
  type ValidationResult,
} from "@/lib/api";
import RuntimeBanner from "./RuntimeBanner";
import MissionWorkbench from "./MissionWorkbench";
import Link from "next/link";
import { ArrowLeft, Loader2 } from "lucide-react";

interface Props {
  missionId: string;
}

export default function MissionDetail({ missionId }: Props) {
  const [data, setData] = useState<MissionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [validationResult, setValidationResult] =
    useState<ValidationResult | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    getMission(missionId)
      .then(setData)
      .catch(() => setError("Failed to load mission"))
      .finally(() => setLoading(false));
  }, [missionId]);

  useEffect(() => {
    load();
  }, [load]);

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

  const handleValidateStep = async (stepId: string) => {
    setActionLoading(true);
    try {
      const result = await validateMission(missionId, stepId);
      await load();
      return result;
    } catch {
      setError("Failed to validate step");
      return null;
    } finally {
      setActionLoading(false);
    }
  };

  const handleReset = async (mode: ResetMode) => {
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

  const handleUseLearnMore = async (itemId: string) => {
    try {
      await useLearnMore(missionId, itemId);
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
        <Link
          href="/"
          className="inline-flex items-center gap-2 rounded-md border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-emerald-50 hover:bg-white/[0.075]"
        >
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
        <Link
          href="/"
          className="inline-flex items-center gap-2 rounded-md border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-emerald-50 hover:bg-white/[0.075]"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to missions
        </Link>
      </div>
    );
  }

  return (
    <div>
      <RuntimeBanner />

      <div className="mb-6">
        <Link
          href="/"
          className="mb-4 inline-flex items-center gap-2 text-sm text-emerald-100/55 hover:text-lime-200"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to mission map
        </Link>
      </div>
      <MissionWorkbench
        data={data}
        actionLoading={actionLoading}
        validationResult={validationResult}
        onStart={handleStart}
        onValidateMission={handleValidate}
        onValidateStep={handleValidateStep}
        onReset={handleReset}
        onUseHint={handleUseHint}
        onUseLearnMore={handleUseLearnMore}
      />
    </div>
  );
}
