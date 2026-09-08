import { useEffect, useState } from "react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";
import { TrendingUp, TrendingDown } from "lucide-react";
import { api, toParams } from "../lib/api";
import type { Filters } from "../lib/api";
import { ChartCard, EmptyState, Skeleton, formatCurrency } from "../components/UI";
import FilterBar from "../components/FilterBar";

export default function Regions() {
  const [filters, setFilters] = useState<Filters>({});
  const [options, setOptions] = useState({ regions: [], categories: [], segments: [], products: [] });
  const [regions, setRegions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/dashboard/filter-options").then((r) => setOptions(r.data)).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    api.get("/regions", { params: toParams(filters) }).then((r) => setRegions(r.data.regions)).finally(() => setLoading(false));
  }, [filters]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-xl font-semibold text-slate-900 dark:text-white">Regional Analytics</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">Compare performance and growth across regions.</p>
      </div>

      <FilterBar filters={filters} setFilters={setFilters} options={options} />

      {loading ? (
        <Skeleton className="h-96" />
      ) : regions.length === 0 ? (
        <EmptyState title="No regional data" subtitle="Upload sales data to see regional analytics." />
      ) : (
        <>
          <ChartCard title="Revenue by Region">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={regions}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.15} />
                <XAxis dataKey="region" tick={{ fontSize: 11 }} />
                <YAxis tickFormatter={(v) => formatCurrency(v)} tick={{ fontSize: 11 }} width={60} />
                <Tooltip formatter={(v) => formatCurrency(Number(v))} />
                <Bar dataKey="revenue" fill="#6366f1" radius={[6, 6, 0, 0]} />
                <Bar dataKey="profit" fill="#2dd4da" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          <div className="grid gap-4 md:grid-cols-2">
            {regions.map((r) => (
              <ChartCard key={r.region} title={r.region}>
                <div className="mb-3 flex items-center justify-between">
                  <div>
                    <p className="text-xs text-slate-500 dark:text-slate-400">Revenue</p>
                    <p className="font-display text-lg font-semibold text-slate-800 dark:text-white">{formatCurrency(r.revenue)}</p>
                  </div>
                  <div className={`flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium ${
                    r.growth_pct >= 0 ? "bg-positive-500/10 text-positive-500" : "bg-negative-500/10 text-negative-500"
                  }`}>
                    {r.growth_pct >= 0 ? <TrendingUp size={13} /> : <TrendingDown size={13} />}
                    {Math.abs(r.growth_pct).toFixed(1)}%
                  </div>
                </div>
                <p className="mb-2 text-xs font-medium uppercase tracking-wider text-slate-400">Top Products</p>
                <div className="space-y-1.5">
                  {r.top_products?.map((p: any) => (
                    <div key={p.product_id} className="flex justify-between text-sm">
                      <span className="text-slate-600 dark:text-slate-300">{p.product_name}</span>
                      <span className="font-mono text-slate-500 dark:text-slate-400">{formatCurrency(p.revenue)}</span>
                    </div>
                  ))}
                </div>
              </ChartCard>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
