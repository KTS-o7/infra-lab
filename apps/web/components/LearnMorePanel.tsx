"use client";

import { useState } from "react";
import {
  ChevronDown,
  ExternalLink,
  GraduationCap,
  Sparkles,
} from "lucide-react";
import { clsx } from "clsx";

interface LearnMoreItem {
  id: string;
  question: string;
  answer: string;
  docsUrl?: string;
  xp: number;
  isUsed: boolean;
}

interface Props {
  items: LearnMoreItem[];
  onUse: (itemId: string) => Promise<void>;
}

export default function LearnMorePanel({ items, onUse }: Props) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const handleToggle = async (id: string) => {
    if (expandedId === id) {
      setExpandedId(null);
    } else {
      setExpandedId(id);
      const item = items.find((i) => i.id === id);
      if (item && !item.isUsed) {
        await onUse(id);
      }
    }
  };

  if (items.length === 0) return null;

  return (
    <section className="rounded-lg border border-white/10 bg-[#0b1512]/80 p-5 shadow-2xl shadow-black/20 backdrop-blur">
      <div className="mb-4 flex items-center gap-2">
        <GraduationCap className="h-4 w-4 text-lime-300" />
        <h2 className="text-lg font-semibold text-emerald-50">Learn more</h2>
      </div>

      <div className="space-y-3">
        {items.map((item) => (
          <div
            key={item.id}
            className={clsx(
              "overflow-hidden rounded-md border transition-all duration-200",
              expandedId === item.id
                ? "border-lime-300/30 bg-lime-300/[0.03]"
                : "border-white/5 bg-white/[0.02] hover:border-white/10 hover:bg-white/[0.04]",
            )}
          >
            <button
              onClick={() => handleToggle(item.id)}
              className="flex w-full items-center justify-between px-4 py-3 text-left"
            >
              <div className="flex items-center gap-3">
                <span
                  className={clsx(
                    "flex h-6 w-6 items-center justify-center rounded-full text-[10px] font-bold",
                    item.isUsed
                      ? "bg-lime-300/20 text-lime-100"
                      : "bg-white/10 text-emerald-100/40",
                  )}
                >
                  {item.isUsed ? "✓" : "?"}
                </span>
                <span className="text-sm font-medium text-emerald-50">
                  {item.question}
                </span>
              </div>
              <div className="flex items-center gap-3">
                {!item.isUsed && (
                  <span className="flex items-center gap-1 rounded-full bg-lime-300/10 px-2 py-0.5 text-[10px] font-bold text-lime-300">
                    <Sparkles className="h-3 w-3" />+{item.xp} XP
                  </span>
                )}
                <ChevronDown
                  className={clsx(
                    "h-4 w-4 text-emerald-100/40 transition-transform duration-200",
                    expandedId === item.id && "rotate-180",
                  )}
                />
              </div>
            </button>

            {expandedId === item.id && (
              <div className="border-t border-white/5 px-4 pb-4 pt-3">
                <p className="text-sm leading-relaxed text-emerald-100/75">
                  {item.answer}
                </p>
                {item.docsUrl && (
                  <a
                    href={item.docsUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-4 inline-flex items-center gap-1.5 text-xs font-medium text-lime-300 hover:text-lime-200"
                  >
                    Read detailed documentation
                    <ExternalLink className="h-3 w-3" />
                  </a>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}
