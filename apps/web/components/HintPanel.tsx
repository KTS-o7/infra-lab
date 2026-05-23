"use client";

interface Hint {
  id: string;
  title: string;
  text?: string;
  isUsed: boolean;
  penaltyXp: number;
}

interface Props {
  hints: Hint[];
  onUseHint: (hintId: string) => void;
  missionStarted: boolean;
}

export default function HintPanel({ hints, onUseHint, missionStarted }: Props) {
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-900 p-6">
      <h2 className="text-lg font-semibold text-slate-100 mb-4">Hints</h2>
      <div className="space-y-3">
        {hints.map((hint) => (
          <div key={hint.id} className="rounded-lg border border-slate-700 bg-slate-950 p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-slate-200">{hint.title}</span>
                {hint.penaltyXp > 0 && (
                  <span className="text-xs text-amber-500">-{hint.penaltyXp} XP</span>
                )}
              </div>
              {!hint.isUsed && hint.text && missionStarted && (
                <button
                  onClick={() => onUseHint(hint.id)}
                  className="text-xs px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
                >
                  Reveal Hint
                </button>
              )}
            </div>
            {hint.isUsed && hint.text && (
              <p className="text-sm text-slate-400">{hint.text}</p>
            )}
            {!hint.text && !hint.isUsed && (
              <p className="text-sm text-slate-500 italic">Use hint to reveal guidance.</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}