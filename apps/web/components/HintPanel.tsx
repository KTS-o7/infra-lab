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
    <div className="rounded-lg border border-white/10 bg-[#0b1512]/80 p-6 shadow-xl shadow-black/10 backdrop-blur">
      <h2 className="mb-4 text-lg font-semibold text-emerald-50">Hints</h2>
      <div className="space-y-3">
        {hints.map((hint) => (
          <div key={hint.id} className="rounded-md border border-white/10 bg-black/25 p-4">
            <div className="mb-2 flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-emerald-50">{hint.title}</span>
                {hint.penaltyXp > 0 && (
                  <span className="text-xs text-amber-300">-{hint.penaltyXp} XP</span>
                )}
              </div>
              {!hint.isUsed && hint.text && missionStarted && (
                <button
                  onClick={() => onUseHint(hint.id)}
                  className="rounded-md border border-white/10 bg-white/[0.04] px-3 py-1 text-xs text-emerald-100/65 hover:bg-white/[0.075] hover:text-emerald-50"
                >
                  Reveal Hint
                </button>
              )}
            </div>
            {hint.isUsed && hint.text && (
              <p className="text-sm leading-6 text-emerald-100/62">{hint.text}</p>
            )}
            {!hint.text && !hint.isUsed && (
              <p className="text-sm italic text-emerald-100/42">Use hint to reveal guidance.</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
