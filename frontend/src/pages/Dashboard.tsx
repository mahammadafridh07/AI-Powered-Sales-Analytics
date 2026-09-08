import { useEffect, useState } from "react";
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid,
  BarChart, Bar, PieChart, Pie, Cell, Legend,
} from "recharts";
import { TrendingUp, TrendingDown, Lightbulb, ShieldAlert, MapPin } from "lucide-react";
import { api, toParams } from "../lib/api";
import type { Filters } from "../lib/api";
import { KpiCard, ChartCard, EmptyState, Skeleton, formatCurrency } from "../components/UI";
import FilterBar from "../components/FilterBar";

const COLORS = ["#6366f1", "#2dd4da", "#22c55e", "#f5a623", "#f0475a", "#818cf8"];

interface Insight { type: string; icon: string; title: string; text: string; }

export default function Dashboard() {
  const [filters, setFilters] = useState<Filters>({});
  const [options, setOptions] = useState({ regions: [], categories: [], segments: [], products: [] });
  const [summary, setSummary] = useState<any>(null);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/dashboard/filter-options").then((r) => setOptions(r.data)).catch(() => {});
    api.get("/dashboard/insights").then((r) => setInsights(r.data.insights || [])).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    api
      .get("/dashboard/summary", { params: toParams(filters) })
      .then((r) => setSummary(r.data))
      .finally(() => setLoading(false));
  }, [filters]);

  const insightIcon = (icon: string) => {
    if (icon === "trending-up") return <TrendingUp size={16} className="text-positive-500" />;
    if (icon === "trending-down") return <TrendingDown size={16} className="text-negative-500" />;
    if (icon === "alert-triangle") return <ShieldAlert size={16} className="text-warning-500" />;
    if (icon === "map-pin") return <MapPin size={16} className="text-brand-500" />;
    return <Lightbulb size={16} className="text-brand-500" />;
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-xl font-semibold text-slate-900 dark:text-white">Executive Dashboard</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">A real-time snapshot of revenue, profit, and growth.</p>
      </div>

      <FilterBar filters={filters} setFilters={setFilters} options={options} />

      {loading ? (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
          {Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-24" />)}
        </div>
      ) : !summary?.has_data ? (
        <EmptyState title="No sales data yet" subtitle="Upload a CSV or load the sample dataset from the Upload page to see your dashboard come to life." />
      ) : (
        <>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
            <KpiCard label="Revenue" value={summary.kpis.revenue.value} growth={summary.kpis.revenue.growth_pct} />
            <KpiCard label="Profit" value={summary.kpis.profit.value} growth={summary.kpis.profit.growth_pct} />
            <KpiCard label="Orders" value={summary.kpis.orders.value} growth={summary.kpis.orders.growth_pct} isInteger isCurrency={false} />
            <KpiCard label="Avg Order Value" value={summary.kpis.avg_order_value.value} growth={summary.kpis.avg_order_value.growth_pct} />
            <KpiCard label="Customers" value={summary.kpis.customers.value} growth={summary.kpis.customers.growth_pct} isInteger isCurrency={false} />
          </div>

          {insights.length > 0 && (
            <ChartCard title="AI Business Insights">
              <div className="grid gap-3 sm:grid-cols-2">
                {insights.map((ins, i) => (
                  <div key={i} className="flex gap-3 rounded-xl bg-slate-50 p-3 dark:bg-ink-700/40">
                    <div className="mt-0.5">{insightIcon(ins.icon)}</div>
                    <div>
                      <p className="text-sm font-medium text-slate-800 dark:text-slate-100">{ins.title}</p>
                      <p className="text-xs text-slate-500 dark:text-slate-400">{ins.text}</p>
                    </div>
                  </div>
                ))}
              </div>
            </ChartCard>
          )}

          <div className="grid gap-4 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <ChartCard title="Revenue & Profit Over Time">
                <ResponsiveContainer width="100%" height={280}>
                  <AreaChart data={summary.revenue_over_time}>
                    <defs>
                      <linearGradient id="rev" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#6366f1" stopOpacity={0.35} />
                        <stop offset="100%" stopColor="#6366f1" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="profit" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#22c55e" stopOpacity={0.3} />
                        <stop offset="100%" stopColor="#22c55e" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.15} />
                    <XAxis dataKey="order_date" tick={{ fontSize: 11 }} minTickGap={30} />
                    <YAxis tickFormatter={(v) => formatCurrency(v)} tick={{ fontSize: 11 }} width={60} />
                    <Tooltip formatter={(v) => formatCurrency(Number(v))} />
                    <Area type="monotone" dataKey="revenue" stroke="#6366f1" fill="url(#rev)" strokeWidth={2} name="Revenue" />
                    <Area type="monotone" dataKey="profit" stroke="#22c55e" fill="url(#profit)" strokeWidth={2} name="Profit" />
                  </AreaChart>
                </ResponsiveContainer>
              </ChartCard>
            </div>
            <ChartCard title="Revenue by Category">
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={summary.revenue_by_category}
                    dataKey="revenue"
                    nameKey="category"
                    innerRadius={55}
                    outerRadius={90}
                    paddingAngle={2}
                  >
                    {summary.revenue_by_category.map((_: any, i: number) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(v) => formatCurrency(Number(v))} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                </PieChart>
              </ResponsiveContainer>
            </ChartCard>
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <ChartCard title="Revenue by Region">
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={summary.revenue_by_region}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.15} />
                  <XAxis dataKey="region" tick={{ fontSize: 11 }} />
                  <YAxis tickFormatter={(v) => formatCurrency(v)} tick={{ fontSize: 11 }} width={60} />
                  <Tooltip formatter={(v) => formatCurrency(Number(v))} />
                  <Bar dataKey="revenue" fill="#6366f1" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>
            <ChartCard title="Top Products">
              <div className="space-y-2">
                {summary.top_products.slice(0, 6).map((p: any) => (
                  <div key={p.product_id} className="flex items-center justify-between text-sm">
                    <div>
                      <p className="font-medium text-slate-700 dark:text-slate-200">{p.product_name}</p>
                      <p className="text-xs text-slate-500 dark:text-slate-400">{p.category}</p>
                    </div>
                    <span className="font-mono text-sm font-semibold text-slate-700 dark:text-slate-200">
                      {formatCurrency(p.revenue)}
                    </span>
                  </div>
                ))}
              </div>
            </ChartCard>
          </div>
        </>
      )}
    </div>
  );
}
