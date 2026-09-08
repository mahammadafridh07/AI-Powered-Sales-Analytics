import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { ChartCard, EmptyState, Skeleton, SeverityBadge, formatCurrency } from "../components/UI";

const SEVERITIES = ["High", "Medium", "Low"];

export default function Anomalies() {
  const [severity, setSeverity] = useState<string | null>(null);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api
      .get("/anomalies", { params: severity ? { severity } : {} })
      .then((r) => setData(r.data))
      .finally(() => setLoading(false));
  }, [severity]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-xl font-semibold text-slate-900 dark:text-white">Anomaly Detection</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Detected using Isolation Forest over revenue, quantity, price, and discount patterns.
        </p>
      </div>

      {loading && !data ? (
        <Skeleton className="h-96" />
      ) : (
        <>
          <div className="grid grid-cols-3 gap-4">
            {SEVERITIES.map((s) => (
              <button
                key={s}
                onClick={() => setSeverity(severity === s ? null : s)}
                className={`rounded-2xl border p-4 text-left transition ${
                  severity === s
                    ? "border-brand-500 bg-brand-500/5"
                    : "border-slate-200 bg-white dark:border-white/10 dark:bg-ink-800"
                }`}
              >
                <SeverityBadge severity={s} />
                <p className="mt-2 font-display text-2xl font-semibold text-slate-800 dark:text-white">
                  {data?.counts?.[s] ?? 0}
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400">anomalies detected</p>
              </button>
            ))}
          </div>

          {!data || data.anomalies.length === 0 ? (
            <EmptyState title="No anomalies found" subtitle="Either your data looks consistent, or there isn't enough data yet." />
          ) : (
            <ChartCard title={`Detected Anomalies (${data.total})`}>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-200 text-left text-xs uppercase tracking-wider text-slate-400 dark:border-white/10">
                      <th className="py-2 pr-4">Date</th>
                      <th className="py-2 pr-4">Product</th>
                      <th className="py-2 pr-4">Region</th>
                      <th className="py-2 pr-4">Actual</th>
                      <th className="py-2 pr-4">Expected</th>
                      <th className="py-2 pr-4">Score</th>
                      <th className="py-2 pr-4">Severity</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.anomalies.map((a: any, i: number) => (
                      <tr key={i} className="border-b border-slate-100 hover:bg-slate-50 dark:border-white/5 dark:hover:bg-white/5">
                        <td className="py-2.5 pr-4 text-slate-500 dark:text-slate-400">{a.date}</td>
                        <td className="py-2.5 pr-4 font-medium text-slate-700 dark:text-slate-200">{a.product_name}</td>
                        <td className="py-2.5 pr-4">{a.region}</td>
                        <td className="py-2.5 pr-4 font-mono">{formatCurrency(a.actual_value)}</td>
                        <td className="py-2.5 pr-4 font-mono text-slate-500">{formatCurrency(a.expected_revenue)}</td>
                        <td className="py-2.5 pr-4 font-mono">{a.anomaly_score}</td>
                        <td className="py-2.5 pr-4"><SeverityBadge severity={a.severity} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </ChartCard>
          )}
        </>
      )}
    </div>
  );
}
