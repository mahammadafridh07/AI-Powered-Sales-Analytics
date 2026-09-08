import { useEffect, useState } from "react";
import { api, toParams } from "../lib/api";
import type { Filters } from "../lib/api";
import { ChartCard, EmptyState, Skeleton, formatCurrency, formatNumber } from "../components/UI";
import FilterBar from "../components/FilterBar";
import { ArrowUpDown } from "lucide-react";

type SortKey = "revenue" | "profit" | "units_sold" | "margin_pct";

export default function Products() {
  const [filters, setFilters] = useState<Filters>({});
  const [options, setOptions] = useState({ regions: [], categories: [], segments: [], products: [] });
  const [products, setProducts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortKey, setSortKey] = useState<SortKey>("revenue");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  useEffect(() => {
    api.get("/dashboard/filter-options").then((r) => setOptions(r.data)).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    api.get("/products", { params: toParams(filters) }).then((r) => setProducts(r.data.products)).finally(() => setLoading(false));
  }, [filters]);

  function toggleSort(key: SortKey) {
    if (sortKey === key) setSortDir(sortDir === "desc" ? "asc" : "desc");
    else { setSortKey(key); setSortDir("desc"); }
  }

  const sorted = [...products].sort((a, b) => (sortDir === "desc" ? b[sortKey] - a[sortKey] : a[sortKey] - b[sortKey]));

  const headers: { key: SortKey; label: string }[] = [
    { key: "revenue", label: "Revenue" },
    { key: "profit", label: "Profit" },
    { key: "units_sold", label: "Units Sold" },
    { key: "margin_pct", label: "Margin %" },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-xl font-semibold text-slate-900 dark:text-white">Product Analytics</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">Revenue, profit, and demand by product.</p>
      </div>

      <FilterBar filters={filters} setFilters={setFilters} options={options} />

      {loading ? (
        <Skeleton className="h-96" />
      ) : products.length === 0 ? (
        <EmptyState title="No product data" subtitle="Upload sales data to see product analytics." />
      ) : (
        <ChartCard title={`All Products (${products.length})`}>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-left text-xs uppercase tracking-wider text-slate-400 dark:border-white/10">
                  <th className="py-2 pr-4">Product</th>
                  <th className="py-2 pr-4">Category</th>
                  {headers.map((h) => (
                    <th key={h.key} className="cursor-pointer select-none py-2 pr-4" onClick={() => toggleSort(h.key)}>
                      <span className="inline-flex items-center gap-1">
                        {h.label} <ArrowUpDown size={12} />
                      </span>
                    </th>
                  ))}
                  <th className="py-2 pr-4">Orders</th>
                </tr>
              </thead>
              <tbody>
                {sorted.map((p) => (
                  <tr key={p.product_id} className="border-b border-slate-100 hover:bg-slate-50 dark:border-white/5 dark:hover:bg-white/5">
                    <td className="py-2.5 pr-4 font-medium text-slate-700 dark:text-slate-200">{p.product_name}</td>
                    <td className="py-2.5 pr-4 text-slate-500 dark:text-slate-400">{p.category}</td>
                    <td className="py-2.5 pr-4 font-mono">{formatCurrency(p.revenue)}</td>
                    <td className="py-2.5 pr-4 font-mono">{formatCurrency(p.profit)}</td>
                    <td className="py-2.5 pr-4 font-mono">{formatNumber(p.units_sold)}</td>
                    <td className="py-2.5 pr-4 font-mono">{p.margin_pct}%</td>
                    <td className="py-2.5 pr-4 font-mono">{p.orders}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </ChartCard>
      )}
    </div>
  );
}
