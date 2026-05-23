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
      <div className="rounded-lg border border-slate-700 bg-slate-950 p-4 space-y-3">
        <p className="text-sm text-slate-300 font-medium">Reset Mission?</p>
        <div className="space-y-2">
          <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
            <input
              type="radio"
              name="reset-mode"
              value="practice"
              checked={mode === "practice"}
              onChange={() => setMode("practice")}
              className="text-blue-500"
            />
            Practice reset — keep XP and completion
          </label>
          <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
            <input
              type="radio"
              name="reset-mode"
              value="restart"
              checked={mode === "restart"}
              onChange={() => setMode("restart")}
              className="text-blue-500"
            />
            Restart reset — clear progress
          </label>
        </div>
        <div className="flex gap-2 pt-2">
          <button
            onClick={handleReset}
            disabled={disabled}
            className="flex-1 py-2 px-4 rounded bg-red-700 hover:bg-red-600 disabled:opacity-50 text-white text-sm font-medium"
          >
            Confirm Reset
          </button>
          <button
            onClick={handleCancel}
            className="py-2 px-4 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm"
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
      className="w-full py-2.5 px-4 rounded-lg border border-slate-700 hover:bg-slate-800 disabled:opacity-50 text-slate-300 text-sm font-medium transition-colors"
    >
      Reset Mission
    </button>
  );
}