import { useEffect, useState } from "react";
import { ResponsiveContainer, ComposedChart, Line, Area, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from "recharts";
import { api } from "../lib/api";
import { ChartCard, KpiCard, EmptyState, Skeleton, formatCurrency } from "../components/UI";

const HORIZONS = [7, 30, 90];

export default function Forecast() {
  const [horizon, setHorizon] = useState(30);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    setError("");
    api
      .get("/forecast", { params: { horizon } })
      .then((r) => setData(r.data))
      .catch((e) => setError(e?.response?.data?.detail || "Could not generate forecast."))
      .finally(() => setLoading(false));
  }, [horizon]);

  const chartData = data
    ? [
        ...data.history.map((h: any) => ({ date: h.date, actual: h.revenue })),
        ...data.forecast.map((f: any) => ({ date: f.date, forecast: f.revenue, lower: f.lower, upper: f.upper })),
      ]
    : [];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="font-display text-xl font-semibold text-slate-900 dark:text-white">Sales Forecasting</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Trained on your historical data — the best-validated model is selected automatically.
          </p>
        </div>
        <div className="flex rounded-lg border border-slate-200 bg-white p-1 dark:border-white/10 dark:bg-ink-800">
          {HORIZONS.map((h) => (
            <button
              key={h}
              onClick={() => setHorizon(h)}
              className={`rounded-md px-3 py-1.5 text-sm font-medium transition ${
                horizon === h ? "bg-brand-500 text-white" : "text-slate-500 dark:text-slate-400"
              }`}
            >
              {h} days
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <Skeleton className="h-96" />
      ) : error ? (
        <EmptyState title="Forecast unavailable" subtitle={error} />
      ) : data ? (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="rounded-2xl border border-ink-600/40 bg-white p-5 dark:bg-ink-800">
              <p className="text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">Model Used</p>
              <p className="mt-2 font-display text-2xl font-semibold text-brand-500">{data.model_used}</p>
            </div>
            <KpiCard label={`Expected Revenue (${horizon}d)`} value={data.expected_revenue_total} />
            <KpiCard label="Validation MAPE" value={data.metrics[data.model_used].mape} isPercent isCurrency={false} />
          </div>

          <ChartCard title="Historical Sales vs. Forecast">
            <ResponsiveContainer width="100%" height={320}>
              <ComposedChart data={chartData}>
                <defs>
                  <linearGradient id="band" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#2dd4da" stopOpacity={0.25} />
                    <stop offset="100%" stopColor="#2dd4da" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.15} />
                <XAxis dataKey="date" tick={{ fontSize: 10 }} minTickGap={40} />
                <YAxis tickFormatter={(v) => formatCurrency(v)} tick={{ fontSize: 11 }} width={60} />
                <Tooltip formatter={(v) => formatCurrency(Number(v))} />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Area type="monotone" dataKey="upper" stroke="none" fill="url(#band)" name="Confidence band" />
                <Line type="monotone" dataKey="actual" stroke="#818cf8" dot={false} strokeWidth={2} name="Historical" />
                <Line type="monotone" dataKey="forecast" stroke="#2dd4da" dot={false} strokeWidth={2} strokeDasharray="5 3" name="Forecast" />
              </ComposedChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Model Comparison (Validation Metrics)">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-200 text-left text-xs uppercase tracking-wider text-slate-400 dark:border-white/10">
                    <th className="py-2 pr-4">Model</th>
                    <th className="py-2 pr-4">MAE</th>
                    <th className="py-2 pr-4">RMSE</th>
                    <th className="py-2 pr-4">MAPE</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(data.metrics).map(([name, m]: [string, any]) => (
                    <tr
                      key={name}
                      className={`border-b border-slate-100 dark:border-white/5 ${
                        name === data.model_used ? "bg-brand-500/5 font-medium" : ""
                      }`}
                    >
                      <td className="py-2.5 pr-4 text-slate-700 dark:text-slate-200">
                        {name} {name === data.model_used && <span className="ml-1 text-xs text-brand-500">(selected)</span>}
                      </td>
                      <td className="py-2.5 pr-4 font-mono">{formatCurrency(m.mae)}</td>
                      <td className="py-2.5 pr-4 font-mono">{formatCurrency(m.rmse)}</td>
                      <td className="py-2.5 pr-4 font-mono">{m.mape}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </ChartCard>
        </>
      ) : null}
    </div>
  );
}
