"use client";

import { useState } from "react";
import { clsx } from "clsx";
import { Check, Copy } from "lucide-react";

interface Props {
  id: string;
  label: string;
  command: string;
}

export default function CommandBlock({ id, label, command }: Props) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(command).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="rounded-md border border-white/10 bg-black/25 p-4">
      <div className="mb-3 flex items-center justify-between gap-3">
        <span className="text-sm font-medium text-emerald-100/75">{label}</span>
        <button
          onClick={handleCopy}
          className={clsx(
            "flex shrink-0 items-center gap-1.5 rounded-md border px-3 py-1 text-xs font-medium transition-colors",
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
      <pre className="overflow-x-auto whitespace-pre-wrap break-all rounded-md bg-[#08110f] p-3 font-mono text-sm leading-6 text-emerald-50">{command}</pre>
    </div>
  );
}
