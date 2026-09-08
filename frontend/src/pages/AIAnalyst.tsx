import { useEffect, useRef, useState } from "react";
import { Send, Bot, User, AlertCircle } from "lucide-react";
import { api } from "../lib/api";

interface Message {
  role: "user" | "assistant";
  text: string;
}

const SUGGESTIONS = [
  "Which region generated the highest revenue?",
  "Which products are underperforming?",
  "Which customers are at risk?",
  "Give me a summary of this quarter.",
  "Which region is growing fastest?",
];

export default function AIAnalyst() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", text: "Ask me anything about your sales data — I'll answer using your real, retrieved analytics." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [aiConfigured, setAiConfigured] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.get("/ai/status").then((r) => setAiConfigured(r.data.ai_configured)).catch(() => {});
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send(question?: string) {
    const q = question || input;
    if (!q.trim()) return;
    setMessages((m) => [...m, { role: "user", text: q }]);
    setInput("");
    setLoading(true);
    try {
      const res = await api.post("/ai/chat", { question: q });
      setMessages((m) => [...m, { role: "assistant", text: res.data.answer }]);
    } catch (e: any) {
      setMessages((m) => [...m, { role: "assistant", text: "Sorry, I couldn't process that question. Please try again." }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col">
      <div className="mb-4">
        <h1 className="font-display text-xl font-semibold text-slate-900 dark:text-white">AI Sales Analyst</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">Data-grounded answers, never invented.</p>
      </div>

      {!aiConfigured && (
        <div className="mb-4 flex items-start gap-2 rounded-xl bg-warning-500/10 px-4 py-3 text-sm text-warning-500">
          <AlertCircle size={16} className="mt-0.5 shrink-0" />
          <span>
            No LLM_API_KEY is configured. You'll still get accurate, data-grounded answers — just without
            natural-language polish from an LLM. Add a key in your <span className="font-mono">.env</span> file to enable full AI explanations.
          </span>
        </div>
      )}

      <div className="flex-1 space-y-4 overflow-y-auto rounded-2xl border border-slate-200 bg-white p-4 dark:border-white/5 dark:bg-ink-800">
        {messages.map((m, i) => (
          <div key={i} className={`flex gap-3 ${m.role === "user" ? "flex-row-reverse" : ""}`}>
            <div
              className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
                m.role === "user" ? "bg-brand-500 text-white" : "bg-teal-500/15 text-teal-500"
              }`}
            >
              {m.role === "user" ? <User size={15} /> : <Bot size={15} />}
            </div>
            <div
              className={`max-w-[75%] whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-sm ${
                m.role === "user"
                  ? "bg-brand-500 text-white"
                  : "bg-slate-100 text-slate-700 dark:bg-ink-700 dark:text-slate-200"
              }`}
            >
              {m.text}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <span className="h-2 w-2 animate-bounce rounded-full bg-brand-500 [animation-delay:-0.2s]" />
            <span className="h-2 w-2 animate-bounce rounded-full bg-brand-500 [animation-delay:-0.1s]" />
            <span className="h-2 w-2 animate-bounce rounded-full bg-brand-500" />
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            onClick={() => send(s)}
            className="rounded-full border border-slate-200 px-3 py-1.5 text-xs text-slate-600 hover:border-brand-500 hover:text-brand-500 dark:border-white/10 dark:text-slate-300"
          >
            {s}
          </button>
        ))}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          send();
        }}
        className="mt-3 flex gap-2"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about your sales data..."
          className="flex-1 rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/40 dark:border-white/10 dark:bg-ink-800 dark:text-white"
        />
        <button
          type="submit"
          disabled={loading}
          className="flex items-center justify-center rounded-xl bg-brand-500 px-4 py-3 text-white hover:bg-brand-600 disabled:opacity-60"
        >
          <Send size={17} />
        </button>
      </form>
    </div>
  );
}
