"use client";

import { useEffect, useRef, useState } from "react";
import { Terminal } from "@xterm/xterm";
import { FitAddon } from "@xterm/addon-fit";
import "@xterm/xterm/css/xterm.css";

export default function MissionWebTerminal() {
  const terminalRef = useRef<HTMLDivElement>(null);
  const xtermRef = useRef<Terminal | null>(null);
  const socketRef = useRef<WebSocket | null>(null);

  // REVIEW FIX (Sarang): Track connection state so we can show a reconnect button
  // when the socket closes, rather than leaving the user with a dead terminal.
  const [connected, setConnected] = useState(true);

  // REVIEW FIX (Sarang): Incrementing this key re-triggers the useEffect, which
  // tears down the old terminal/socket and boots a fresh one — clean reconnect.
  const [reconnectKey, setReconnectKey] = useState(0);

  useEffect(() => {
    if (!terminalRef.current) return;

    const term = new Terminal({
      cursorBlink: true,
      theme: {
        background: "#050a08",
        foreground: "#bef264", // lime-300
        cursor: "#bef264",
        selectionBackground: "rgba(190, 242, 100, 0.3)",
      },
      fontFamily:
        'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
      fontSize: 14,
    });

    const fitAddon = new FitAddon();
    term.loadAddon(fitAddon);

    term.open(terminalRef.current);
    fitAddon.fit();

    xtermRef.current = term;

    // REVIEW FIX (Sarang): Changed fallback port from 8001 to 8000 to match lib/api.ts
    // and the actual server port. The old value caused WebSocket connections to fail
    // when NEXT_PUBLIC_API_URL was not set.
    let apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    // If we're accessing the UI remotely, localhost:8000 in the browser will fail.
    // We attempt to infer the API host from the current window location if the configured URL is localhost.
    if (
      typeof window !== "undefined" &&
      (apiBaseUrl.includes("localhost") || apiBaseUrl.includes("127.0.0.1"))
    ) {
      const currentHost = window.location.hostname;
      if (currentHost !== "localhost" && currentHost !== "127.0.0.1") {
        apiBaseUrl = apiBaseUrl.replace(/localhost|127\.0\.0\.1/, currentHost);
      }
    }

    const wsBaseUrl = apiBaseUrl.replace(/^http/, "ws");
    const wsUrl = `${wsBaseUrl}/terminal/ws`;

    const socket = new WebSocket(wsUrl);
    socketRef.current = socket;

    socket.onopen = () => {
      setConnected(true);
      term.write("\r\n\x1b[32mCONNECTED TO INFRA-LAB SHELL\x1b[0m\r\n");
      const { cols, rows } = term;
      socket.send(JSON.stringify({ type: "resize", cols, rows }));
    };

    socket.onmessage = async (event) => {
      if (event.data instanceof Blob) {
        const text = await event.data.text();
        term.write(text);
      } else {
        term.write(event.data);
      }
    };

    // REVIEW FIX (Sarang): On close, flip `connected` to false so the reconnect
    // button overlay renders. Previously only a text message was written to the
    // terminal, leaving no actionable way for the user to recover the session.
    socket.onclose = () => {
      term.write("\r\n\x1b[31mDISCONNECTED FROM SHELL\x1b[0m\r\n");
      setConnected(false);
    };

    term.onData((data) => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: "input", data }));
      }
    });

    const handleResize = () => {
      fitAddon.fit();
      const { cols, rows } = term;
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: "resize", cols, rows }));
      }
    };

    window.addEventListener("resize", handleResize);

    // REVIEW FIX (Sarang): Also observe container size changes via ResizeObserver.
    // window resize alone misses cases where the terminal container resizes due to
    // panel toggles or sidebar collapse — the observer fires for those too.
    const resizeObserver = new ResizeObserver(() => {
      handleResize();
    });
    if (terminalRef.current) {
      resizeObserver.observe(terminalRef.current);
    }

    return () => {
      window.removeEventListener("resize", handleResize);
      resizeObserver.disconnect();
      if (
        socket.readyState === WebSocket.OPEN ||
        socket.readyState === WebSocket.CONNECTING
      ) {
        socket.close();
      }
      term.dispose();
    };
  }, [reconnectKey]);

  return (
    <div className="flex h-[450px] flex-col overflow-hidden rounded-lg border border-lime-300/20 bg-[#050a08] shadow-2xl">
      <div className="flex items-center gap-2 border-b border-white/5 bg-white/[0.02] px-4 py-2">
        <div className="flex gap-1.5">
          <div className="h-2.5 w-2.5 rounded-full bg-red-500/50" />
          <div className="h-2.5 w-2.5 rounded-full bg-amber-500/50" />
          <div className="h-2.5 w-2.5 rounded-full bg-emerald-500/50" />
        </div>
        <span className="text-[10px] font-medium uppercase tracking-widest text-emerald-100/40">
          Interactive Terminal
        </span>
      </div>
      <div className="relative flex-1 p-2">
        <div ref={terminalRef} className="h-full w-full overflow-hidden" />
        {/* REVIEW FIX (Sarang): Reconnect button overlay — shown only when the
            WebSocket has closed. Incrementing reconnectKey re-runs the useEffect
            which tears down the dead socket/terminal and creates a fresh pair. */}
        {!connected && (
          <div className="absolute inset-0 flex items-center justify-center bg-[#050a08]/80">
            <button
              onClick={() => setReconnectKey((k) => k + 1)}
              className="rounded border border-lime-300/40 bg-lime-300/10 px-4 py-2 text-sm font-medium text-lime-300 transition hover:bg-lime-300/20"
            >
              Reconnect
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
