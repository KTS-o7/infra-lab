"use client";

import { useEffect, useRef, useState } from "react";
import { Send, Bot, User, Loader2, MessageSquare } from "lucide-react";
import { getChatHistory, sendChatMessage, type ChatMessage } from "@/lib/api";
import { clsx } from "clsx";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Props {
  missionId: string;
}

export default function MissionChatPanel({ missionId }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  // REVIEW FIX (Sarang): Add error state for initial load failure
  const [loadError, setLoadError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getChatHistory(missionId)
      .then((data) => setMessages(data.messages))
      // REVIEW FIX (Sarang): Replace bare console.error with UI error state
      .catch(() => { setLoadError("Failed to load chat history"); })
      .finally(() => setInitialLoading(false));
  }, [missionId]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg: ChatMessage = {
      role: "user",
      content: input,
      createdAt: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const aiMsg = await sendChatMessage(missionId, input);
      setMessages((prev) => [...prev, aiMsg]);
    } catch {
      // REVIEW FIX (Sarang): Remove console.error; UI feedback via error message is sufficient
      setMessages((prev) => [
        ...prev,
        {
          role: "ai",
          content: "Sorry, I'm having trouble connecting to the AI agent.",
          createdAt: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="flex h-[600px] flex-col rounded-lg border border-white/10 bg-[#0b1512]/80 shadow-2xl shadow-black/20 backdrop-blur">
      <div className="flex items-center gap-2 border-b border-white/5 bg-white/[0.02] px-4 py-3">
        <MessageSquare className="h-4 w-4 text-lime-300" />
        <h2 className="text-sm font-semibold text-emerald-50">
          Ask me anything
        </h2>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
        {initialLoading ? (
          <div className="flex items-center justify-center h-full">
            <Loader2 className="h-6 w-6 animate-spin text-lime-300/50" />
          </div>
        ) : messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center p-6">
            <Bot className="h-10 w-10 text-lime-300/20 mb-3" />
            {/* REVIEW FIX (Sarang): Render load error in empty state if set */}
            {loadError ? (
              <p className="text-sm text-red-400/70">{loadError}</p>
            ) : (
              <p className="text-sm text-emerald-100/40">
                Need help with this mission? Ask a question about the services,
                commands, or concepts.
              </p>
            )}
          </div>
        ) : (
          messages.map((msg, i) => (
            <div
              // REVIEW FIX (Sarang): Use stable key (createdAt + role) instead of array index
              key={msg.createdAt + msg.role}
              className={clsx(
                "flex gap-3",
                msg.role === "user"
                  ? "ml-auto flex-row-reverse max-w-[85%]"
                  : "mr-auto max-w-[95%]",
              )}
            >
              <div
                className={clsx(
                  "flex h-8 w-8 shrink-0 items-center justify-center rounded-full border",
                  msg.role === "user"
                    ? "border-lime-300/20 bg-lime-300/10"
                    : "border-white/10 bg-white/5",
                )}
              >
                {msg.role === "user" ? (
                  <User className="h-4 w-4 text-lime-300" />
                ) : (
                  <Bot className="h-4 w-4 text-emerald-100/60" />
                )}
              </div>
              <div
                className={clsx(
                  "rounded-2xl px-4 py-2.5 text-sm",
                  msg.role === "user"
                    ? "bg-lime-300 text-[#08110f] rounded-tr-none whitespace-pre-wrap"
                    : "bg-white/5 text-emerald-50 border border-white/5 rounded-tl-none prose prose-invert prose-sm max-w-none prose-p:leading-relaxed prose-headings:text-lime-300 prose-headings:mt-4 prose-headings:mb-2 prose-ul:list-disc prose-li:my-1",
                )}
              >
                {msg.role === "user" ? (
                  msg.content
                ) : (
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {msg.content}
                  </ReactMarkdown>
                )}
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="flex gap-3 mr-auto animate-pulse">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-white/10 bg-white/5">
              <Bot className="h-4 w-4 text-emerald-100/30" />
            </div>
            <div className="bg-white/5 border border-white/5 rounded-2xl rounded-tl-none px-4 py-2.5">
              <div className="flex gap-1">
                <span
                  className="h-1.5 w-1.5 rounded-full bg-emerald-100/20 animate-bounce"
                  style={{ animationDelay: "0ms" }}
                />
                <span
                  className="h-1.5 w-1.5 rounded-full bg-emerald-100/20 animate-bounce"
                  style={{ animationDelay: "150ms" }}
                />
                <span
                  className="h-1.5 w-1.5 rounded-full bg-emerald-100/20 animate-bounce"
                  style={{ animationDelay: "300ms" }}
                />
              </div>
            </div>
          </div>
        )}
      </div>

      <form
        onSubmit={handleSend}
        className="p-4 border-t border-white/5 bg-white/[0.01]"
      >
        <div className="relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            disabled={loading}
            className="w-full rounded-full border border-white/10 bg-black/40 py-2.5 pl-4 pr-12 text-sm text-emerald-50 placeholder:text-emerald-100/30 focus:border-lime-300/50 focus:outline-none focus:ring-1 focus:ring-lime-300/50 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="absolute right-1.5 top-1.5 flex h-7 w-7 items-center justify-center rounded-full bg-lime-300 text-[#08110f] transition hover:bg-lime-200 disabled:opacity-30"
          >
            <Send className="h-3.5 w-3.5" />
          </button>
        </div>
      </form>
    </section>
  );
}
