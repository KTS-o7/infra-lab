"use client";

import { useState } from "react";
import { clsx } from "clsx";
import { Check, Copy, Monitor, Terminal } from "lucide-react";

interface Props {
  id: string;
  label: string;
  command: string;
}

export default function CommandBlock({ id, label, command }: Props) {
  const [copied, setCopied] = useState(false);
  // "host" = localhost:4566 (default), "browser" = floci:4566
  const [target, setTarget] = useState<"host" | "browser">("host");

  const hasBothVariants = command.includes("localhost:4566");
  const displayedCommand =
    hasBothVariants && target === "browser"
      ? command.replaceAll("localhost:4566", "floci:4566")
      : command;

  const handleCopy = () => {
    navigator.clipboard.writeText(displayedCommand).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="rounded-md border border-white/10 bg-black/25 p-4">
      <div className="mb-3 flex items-center justify-between gap-3">
        <span className="text-sm font-medium text-emerald-100/75">{label}</span>
        <div className="flex items-center gap-2">
          {hasBothVariants && (
            <div className="flex rounded-md border border-white/10 text-xs font-medium overflow-hidden">
              <button
                onClick={() => setTarget("host")}
                className={clsx(
                  "flex items-center gap-1.5 px-2.5 py-1.5 transition-colors",
                  target === "host"
                    ? "bg-emerald-900/50 text-emerald-100"
                    : "bg-transparent text-emerald-100/40 hover:text-emerald-100/70"
                )}
                title="Command for your local terminal"
              >
                <Monitor className="h-3 w-3" />
                Host
              </button>
              <button
                onClick={() => setTarget("browser")}
                className={clsx(
                  "flex items-center gap-1.5 px-2.5 py-1.5 transition-colors border-l border-white/10",
                  target === "browser"
                    ? "bg-emerald-900/50 text-emerald-100"
                    : "bg-transparent text-emerald-100/40 hover:text-emerald-100/70"
                )}
                title="Command for the in-browser terminal"
              >
                <Terminal className="h-3 w-3" />
                Browser
              </button>
            </div>
          )}
          <button
            onClick={handleCopy}
            className={clsx(
              "flex min-h-10 shrink-0 items-center gap-1.5 rounded-md border px-3 py-2 text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-lime-300 focus-visible:ring-offset-2 focus-visible:ring-offset-[#08110f]",
              copied
                ? "border-lime-300/20 bg-lime-300/10 text-lime-100"
                : "border-white/10 bg-white/[0.04] text-emerald-100/65 hover:bg-white/[0.075] hover:text-emerald-50"
            )}
          >
            {copied ? (
              <>
                <Check className="h-3.5 w-3.5" />
                Copied
              </>
            ) : (
              <>
                <Copy className="h-3.5 w-3.5" />
                Copy
              </>
            )}
          </button>
        </div>
      </div>
      <p className="sr-only" aria-live="polite">
        {copied ? `${label} copied to clipboard` : ""}
      </p>
      <pre
        tabIndex={0}
        className="overflow-x-auto whitespace-pre rounded-md bg-[#08110f] p-3 font-mono text-sm leading-6 text-emerald-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-lime-300"
      >
        {displayedCommand}
      </pre>
    </div>
  );
}
