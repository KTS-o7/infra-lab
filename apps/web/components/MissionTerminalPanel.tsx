"use client";

import { useState } from "react";
import { Check, ClipboardCheck, Copy, Loader2, Lock, Terminal } from "lucide-react";
import { clsx } from "clsx";

interface Props {
  command?: { id: string; label: string; command: string };
  canCheck: boolean;
  checking: boolean;
  disabledReason?: string;
  onCheck: () => void;
}

export default function MissionTerminalPanel({ command, canCheck, checking, disabledReason, onCheck }: Props) {
  const [copied, setCopied] = useState(false);
  const [revealed, setRevealed] = useState(false);
  const commandText = command?.command ?? "# No CLI command is attached to this step yet.";

  const handleCopy = () => {
    if (!revealed) return;
    navigator.clipboard.writeText(commandText).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <section className="overflow-hidden rounded-lg border border-lime-300/20 bg-[#050a08] shadow-2xl shadow-black/30">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-lime-300/10 bg-lime-300/[0.035] px-4 py-3">
        <div className="flex min-w-0 items-center gap-2">
          <Terminal className="h-4 w-4 shrink-0 text-lime-300" />
          <div className="min-w-0">
            <p className="text-xs font-medium uppercase tracking-[0.18em] text-lime-200/75">Local terminal</p>
            <p className="truncate text-sm text-emerald-100/60">{command?.label ?? "Guided command"}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setRevealed((current) => !current)}
            className="inline-flex min-h-10 items-center gap-1.5 rounded-md border border-lime-300/20 bg-lime-300/10 px-3 py-2 text-xs font-medium text-lime-100 transition hover:bg-lime-300/15 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-lime-300 focus-visible:ring-offset-2 focus-visible:ring-offset-[#050a08]"
          >
            <Terminal className="h-3.5 w-3.5" />
            {revealed ? "Hide command" : "Reveal command"}
          </button>
          <button
            onClick={handleCopy}
            disabled={!revealed}
            className={clsx(
              "inline-flex min-h-10 items-center gap-1.5 rounded-md border px-3 py-2 text-xs font-medium transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-lime-300 focus-visible:ring-offset-2 focus-visible:ring-offset-[#050a08]",
              !revealed
                ? "cursor-not-allowed border-white/10 bg-white/[0.02] text-emerald-100/30"
                : copied
                ? "border-lime-300/25 bg-lime-300/10 text-lime-100"
                : "border-white/10 bg-white/[0.04] text-emerald-100/70 hover:bg-white/[0.08] hover:text-emerald-50",
            )}
          >
            {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
            {copied ? "Copied" : "Copy"}
          </button>
        </div>
      </div>

      <div className="grid gap-0 lg:grid-cols-[minmax(0,1fr)_16rem]">
        <div className="min-w-0 p-4">
          <div className="rounded-md border border-white/10 bg-black/50 p-4">
            <div className="mb-3 flex items-center gap-2 text-xs text-emerald-100/45">
              <span className="h-2.5 w-2.5 rounded-full bg-red-400/80" />
              <span className="h-2.5 w-2.5 rounded-full bg-amber-300/80" />
              <span className="h-2.5 w-2.5 rounded-full bg-lime-300/80" />
              <span className="ml-2 font-mono">localhost:4566</span>
            </div>
            {revealed ? (
              <pre tabIndex={0} className="overflow-x-auto whitespace-pre font-mono text-sm leading-6 text-lime-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-lime-300">
                <span className="select-none text-emerald-100/35">$ </span>
                {commandText}
              </pre>
            ) : (
              <div className="rounded-md border border-dashed border-white/10 bg-white/[0.025] p-4 text-sm leading-6 text-emerald-100/60">
                Read the goal and target state first, then reveal the local CLI command when you are ready to make the change.
              </div>
            )}
          </div>
        </div>

        <div className="border-t border-white/10 p-4 lg:border-l lg:border-t-0">
          <p className="text-xs font-medium uppercase tracking-[0.16em] text-emerald-100/38">Execution model</p>
          <p className="mt-2 text-sm leading-6 text-emerald-100/60">
            Run this in your machine terminal. Infra Quest checks the local sandbox state after the command changes resources.
          </p>
          <p className="sr-only" aria-live="polite">{copied ? "Command copied to clipboard" : ""}</p>
          <button
            onClick={onCheck}
            disabled={!canCheck || checking}
            aria-disabled={!canCheck || checking}
            className="mt-4 inline-flex min-h-10 w-full items-center justify-center gap-2 rounded-md bg-lime-300 px-4 py-3 font-semibold text-[#08110f] transition hover:bg-lime-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-lime-300 focus-visible:ring-offset-2 focus-visible:ring-offset-[#050a08] disabled:cursor-not-allowed disabled:opacity-50"
          >
            {checking ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Checking step
              </>
            ) : !canCheck ? (
              <>
                <Lock className="h-4 w-4" />
                {disabledReason ?? "Start mission first"}
              </>
            ) : (
              <>
                <ClipboardCheck className="h-4 w-4" />
                Check step
              </>
            )}
          </button>
        </div>
      </div>
    </section>
  );
}
