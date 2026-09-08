import { useEffect, useState } from "react";
import { Moon, Sun, KeyRound, Database, Info } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";
import { api } from "../lib/api";
import { ChartCard } from "../components/UI";

export default function Settings() {
  const { user } = useAuth();
  const { theme, toggle } = useTheme();
  const [aiStatus, setAiStatus] = useState<{ ai_configured: boolean; provider: string; model: string } | null>(null);

  useEffect(() => {
    api.get("/ai/status").then((r) => setAiStatus(r.data)).catch(() => {});
  }, []);

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="font-display text-xl font-semibold text-slate-900 dark:text-white">Settings</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">Manage your profile and application preferences.</p>
      </div>

      <ChartCard title="Profile">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-brand-500/15 text-lg font-semibold text-brand-500">
            {user?.name?.[0]?.toUpperCase()}
          </div>
          <div>
            <p className="font-medium text-slate-800 dark:text-slate-100">{user?.name}</p>
            <p className="text-sm text-slate-500 dark:text-slate-400">{user?.email}</p>
          </div>
        </div>
      </ChartCard>

      <ChartCard title="Appearance">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
            {theme === "dark" ? <Moon size={16} /> : <Sun size={16} />}
            {theme === "dark" ? "Dark mode" : "Light mode"}
          </div>
          <button
            onClick={toggle}
            className="rounded-lg bg-brand-500 px-3 py-1.5 text-xs font-semibold text-white hover:bg-brand-600"
          >
            Switch to {theme === "dark" ? "Light" : "Dark"}
          </button>
        </div>
      </ChartCard>

      <ChartCard title="AI Configuration Status">
        <div className="flex items-center gap-3">
          <div className={`flex h-9 w-9 items-center justify-center rounded-lg ${aiStatus?.ai_configured ? "bg-positive-500/10 text-positive-500" : "bg-warning-500/10 text-warning-500"}`}>
            <KeyRound size={16} />
          </div>
          <div>
            <p className="text-sm font-medium text-slate-700 dark:text-slate-200">
              {aiStatus?.ai_configured ? "LLM API key configured" : "No LLM API key configured"}
            </p>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              {aiStatus?.ai_configured
                ? `Provider: ${aiStatus.provider} · Model: ${aiStatus.model}`
                : "Set LLM_API_KEY in your backend .env to enable full LLM-generated explanations."}
            </p>
          </div>
        </div>
      </ChartCard>

      <ChartCard title="Data Management">
        <div className="flex items-center gap-3 text-sm text-slate-600 dark:text-slate-300">
          <Database size={16} />
          Use the <a href="/app/upload" className="font-medium text-brand-500 hover:underline">Upload Data</a> page to add or refresh your sales dataset.
        </div>
      </ChartCard>

      <ChartCard title="Application Information">
        <div className="flex items-start gap-2 text-sm text-slate-500 dark:text-slate-400">
          <Info size={16} className="mt-0.5 shrink-0" />
          <span>AI-Powered Sales Analytics &amp; Forecasting Platform — v1.0.0. Built with FastAPI, React, and scikit-learn/XGBoost.</span>
        </div>
      </ChartCard>
    </div>
  );
}
