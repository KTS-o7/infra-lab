"use client";

import { useState } from "react";
import type { ResetMode } from "@/lib/api";

interface Props {
  missionId: string;
  onReset: (mode: ResetMode) => void;
  disabled: boolean;
}

export default function ResetControl({ missionId, onReset, disabled }: Props) {
  const [confirming, setConfirming] = useState(false);
  const [mode, setMode] = useState<ResetMode>("resources");

  const handleReset = () => {
    if (!confirming) {
      setConfirming(true);
      return;
    }
    onReset(mode);
    setConfirming(false);
  };

  const handleCancel = () => {
    setConfirming(false);
  };

  if (confirming) {
    return (
      <div className="space-y-3 rounded-md border border-white/10 bg-black/25 p-4">
        <p className="text-sm font-medium text-emerald-50">Reset {missionId}?</p>
        <div className="space-y-2">
          <label className="flex cursor-pointer items-center gap-2 text-sm text-emerald-100/65">
            <input
              type="radio"
              name="reset-mode"
              value="resources"
              checked={mode === "resources"}
              onChange={() => setMode("resources")}
              className="accent-lime-300"
            />
            Resources only - keep progress and XP
          </label>
          <label className="flex cursor-pointer items-center gap-2 text-sm text-emerald-100/65">
            <input
              type="radio"
              name="reset-mode"
              value="progress"
              checked={mode === "progress"}
              onChange={() => setMode("progress")}
              className="accent-lime-300"
            />
            Practice history - clear steps and hints
          </label>
          <label className="flex cursor-pointer items-center gap-2 text-sm text-emerald-100/65">
            <input
              type="radio"
              name="reset-mode"
              value="resources_and_progress"
              checked={mode === "resources_and_progress"}
              onChange={() => setMode("resources_and_progress")}
              className="accent-lime-300"
            />
            Resources and history
          </label>
        </div>
        <p className="text-xs leading-5 text-emerald-100/45">Completed mission credit, XP, and best capstone score are preserved by the backend.</p>
        <div className="flex gap-2 pt-2">
          <button
            onClick={handleReset}
            disabled={disabled}
            className="min-h-10 flex-1 rounded-md bg-red-700 px-4 py-2 text-sm font-medium text-white hover:bg-red-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-300 focus-visible:ring-offset-2 focus-visible:ring-offset-[#07100d] disabled:opacity-50"
          >
            Confirm reset
          </button>
          <button
            onClick={handleCancel}
            className="min-h-10 rounded-md border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-emerald-100/65 hover:bg-white/[0.075] hover:text-emerald-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-lime-300 focus-visible:ring-offset-2 focus-visible:ring-offset-[#07100d]"
          >
            Cancel
          </button>
        </div>
      </div>
    );
  }

  return (
    <button
      onClick={handleReset}
      disabled={disabled}
      className="min-h-10 w-full rounded-md border border-white/10 bg-white/[0.04] px-4 py-2.5 text-sm font-medium text-emerald-100/65 transition-colors hover:bg-white/[0.075] hover:text-emerald-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-lime-300 focus-visible:ring-offset-2 focus-visible:ring-offset-[#07100d] disabled:opacity-50"
    >
      Reset mission
    </button>
  );
}
