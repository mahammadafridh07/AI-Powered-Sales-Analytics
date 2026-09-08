import { useEffect, useState } from "react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";
import { api, toParams } from "../lib/api";
import type { Filters } from "../lib/api";
import { KpiCard, ChartCard, EmptyState, Skeleton, formatCurrency, formatNumber } from "../components/UI";
import FilterBar from "../components/FilterBar";

const SEGMENT_COLORS: Record<string, string> = {
  "High Value": "#22c55e",
  "Loyal": "#6366f1",
  "Potential": "#2dd4da",
  "At Risk": "#f5a623",
  "Inactive": "#f0475a",
};

export default function Customers() {
  const [filters, setFilters] = useState<Filters>({});
  const [options, setOptions] = useState({ regions: [], categories: [], segments: [], products: [] });
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/dashboard/filter-options").then((r) => setOptions(r.data)).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    api.get("/customers", { params: toParams(filters) }).then((r) => setData(r.data)).finally(() => setLoading(false));
  }, [filters]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-xl font-semibold text-slate-900 dark:text-white">Customer Analytics</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">Segments, loyalty, and top customers.</p>
      </div>

      <FilterBar filters={filters} setFilters={setFilters} options={options} />

      {loading ? (
        <Skeleton className="h-96" />
      ) : !data || data.summary.total_customers === 0 ? (
        <EmptyState title="No customer data" subtitle="Upload sales data to see customer analytics." />
      ) : (
        <>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            <KpiCard label="Total Customers" value={data.summary.total_customers} isCurrency={false} isInteger />
            <KpiCard label="New Customers" value={data.summary.new_customers} isCurrency={false} isInteger />
            <KpiCard label="Returning Customers" value={data.summary.returning_customers} isCurrency={false} isInteger />
            <KpiCard label="Avg Order Value" value={data.summary.avg_order_value} />
          </div>

          <div className="grid gap-4 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <ChartCard title="Top Customers by Revenue">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={data.top_customers.slice(0, 10)} layout="vertical" margin={{ left: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.15} />
                    <XAxis type="number" tickFormatter={(v) => formatCurrency(v)} tick={{ fontSize: 11 }} />
                    <YAxis type="category" dataKey="customer_name" tick={{ fontSize: 11 }} width={110} />
                    <Tooltip formatter={(v) => formatCurrency(Number(v))} />
                    <Bar dataKey="revenue" fill="#6366f1" radius={[0, 6, 6, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </ChartCard>
            </div>
            <ChartCard title="Customer Segments">
              <div className="space-y-3">
                {data.segments.map((s: any) => (
                  <div key={s.segment}>
                    <div className="flex justify-between text-xs">
                      <span className="flex items-center gap-1.5 font-medium text-slate-600 dark:text-slate-300">
                        <span className="h-2 w-2 rounded-full" style={{ background: SEGMENT_COLORS[s.segment] || "#818cf8" }} />
                        {s.segment}
                      </span>
                      <span className="text-slate-500 dark:text-slate-400">{formatNumber(s.customers)} customers</span>
                    </div>
                    <div className="mt-1 h-1.5 w-full rounded-full bg-slate-100 dark:bg-ink-700">
                      <div
                        className="h-1.5 rounded-full"
                        style={{
                          width: `${Math.min(100, (s.revenue / data.segments[0].revenue) * 100)}%`,
                          background: SEGMENT_COLORS[s.segment] || "#818cf8",
                        }}
                      />
                    </div>
                    <p className="mt-0.5 text-xs text-slate-400">{formatCurrency(s.revenue)} revenue</p>
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
