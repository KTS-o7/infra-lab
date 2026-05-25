"use client";

import { useState } from "react";

interface Props {
  missionId: string;
  onReset: (mode: string) => void;
  disabled: boolean;
}

export default function ResetControl({ missionId, onReset, disabled }: Props) {
  const [confirming, setConfirming] = useState(false);
  const [mode, setMode] = useState<"practice" | "restart">("practice");

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
        <p className="text-sm font-medium text-emerald-50">Reset mission?</p>
        <div className="space-y-2">
          <label className="flex cursor-pointer items-center gap-2 text-sm text-emerald-100/65">
            <input
              type="radio"
              name="reset-mode"
              value="practice"
              checked={mode === "practice"}
              onChange={() => setMode("practice")}
              className="accent-lime-300"
            />
            Practice reset — keep XP and completion
          </label>
          <label className="flex cursor-pointer items-center gap-2 text-sm text-emerald-100/65">
            <input
              type="radio"
              name="reset-mode"
              value="restart"
              checked={mode === "restart"}
              onChange={() => setMode("restart")}
              className="accent-lime-300"
            />
            Restart reset — clear progress
          </label>
        </div>
        <div className="flex gap-2 pt-2">
          <button
            onClick={handleReset}
            disabled={disabled}
            className="flex-1 rounded-md bg-red-700 px-4 py-2 text-sm font-medium text-white hover:bg-red-600 disabled:opacity-50"
          >
            Confirm Reset
          </button>
          <button
            onClick={handleCancel}
            className="rounded-md border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-emerald-100/65 hover:bg-white/[0.075] hover:text-emerald-50"
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
      className="w-full rounded-md border border-white/10 bg-white/[0.04] px-4 py-2.5 text-sm font-medium text-emerald-100/65 transition-colors hover:bg-white/[0.075] hover:text-emerald-50 disabled:opacity-50"
    >
      Reset Mission
    </button>
  );
}
