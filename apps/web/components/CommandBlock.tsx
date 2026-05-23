"use client";

import { useState } from "react";
import { clsx } from "clsx";

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
    <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-slate-300">{label}</span>
        <button
          onClick={handleCopy}
          className={clsx(
            "flex items-center gap-1.5 px-3 py-1 rounded text-xs font-medium transition-colors",
            copied
              ? "bg-emerald-900 text-emerald-300 border border-emerald-700"
              : "bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
          )}
        >
          {copied ? (
            <>
              <svg width="12" height="12" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Copied
            </>
          ) : (
            <>
              <svg width="12" height="12" fill="currentColor" viewBox="0 0 20 20">
                <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" />
                <path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z" />
              </svg>
              Copy
            </>
          )}
        </button>
      </div>
      <pre className="text-sm font-mono text-slate-200 overflow-x-auto whitespace-pre-wrap break-all">{command}</pre>
    </div>
  );
}