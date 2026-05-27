"use client";

import { useState } from "react";
import {
  Check,
  ClipboardCheck,
  Copy,
  Loader2,
  Lock,
  Terminal,
} from "lucide-react";
import { clsx } from "clsx";

interface Props {
  command?: { id: string; label: string; command: string };
  canCheck: boolean;
  checking: boolean;
  disabledReason?: string;
  onCheck: () => void;
}

export default function MissionTerminalPanel({
  command,
  canCheck,
  checking,
  disabledReason,
  onCheck,
}: Props) {
  const [copied, setCopied] = useState(false);
  const commandText =
    command?.command ?? "# No CLI command is attached to this step yet.";

  const handleCopy = () => {
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
            <p className="text-xs font-medium uppercase tracking-[0.18em] text-lime-200/75">
              Local terminal
            </p>
            <p className="truncate text-sm text-emerald-100/60">
              {command?.label ?? "Guided command"}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            className={clsx(
              "inline-flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-xs font-medium transition",
              copied
                ? "border-lime-300/25 bg-lime-300/10 text-lime-100"
                : "border-white/10 bg-white/[0.04] text-emerald-100/70 hover:bg-white/[0.08] hover:text-emerald-50",
            )}
          >
            {copied ? (
              <Check className="h-3.5 w-3.5" />
            ) : (
              <Copy className="h-3.5 w-3.5" />
            )}
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
              <span className="ml-2 font-mono">floci:4566</span>
            </div>
            <pre className="overflow-x-auto whitespace-pre-wrap break-words font-mono text-sm leading-6 text-lime-100">
              <span className="select-none text-emerald-100/35">$ </span>
              {commandText}
            </pre>
          </div>
        </div>

        <div className="border-t border-white/10 p-4 lg:border-l lg:border-t-0">
          <p className="text-xs font-medium uppercase tracking-[0.16em] text-emerald-100/38">
            Execution model
          </p>
          <p className="mt-2 text-sm leading-6 text-emerald-100/60">
            Run this in your machine terminal. Infra Quest checks the local
            sandbox state after the command changes resources.
          </p>
          <button
            onClick={onCheck}
            disabled={!canCheck || checking}
            className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-md bg-lime-300 px-4 py-3 font-semibold text-[#08110f] transition hover:bg-lime-200 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {checking ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Checking step
              </>
            ) : !canCheck ? (
              <>
                <Lock className="h-4 w-4" />
                Start mission first
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
