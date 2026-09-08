import type { Filters } from "../lib/api";

interface Options {
  regions: string[];
  categories: string[];
  segments: string[];
  products: { product_id: number; product_name: string }[];
}

export default function FilterBar({
  filters,
  setFilters,
  options,
}: {
  filters: Filters;
  setFilters: (f: Filters) => void;
  options: Options;
}) {
  const inputCls =
    "rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 dark:border-white/10 dark:bg-ink-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500/40";

  return (
    <div className="flex flex-wrap items-center gap-2 rounded-2xl border border-slate-200 bg-white p-3 dark:border-white/5 dark:bg-ink-800/60">
      <input
        type="date"
        className={inputCls}
        value={filters.start_date || ""}
        onChange={(e) => setFilters({ ...filters, start_date: e.target.value })}
      />
      <span className="text-xs text-slate-400">to</span>
      <input
        type="date"
        className={inputCls}
        value={filters.end_date || ""}
        onChange={(e) => setFilters({ ...filters, end_date: e.target.value })}
      />
      <select
        className={inputCls}
        value={filters.region || ""}
        onChange={(e) => setFilters({ ...filters, region: e.target.value || undefined })}
      >
        <option value="">All Regions</option>
        {options.regions.map((r) => (
          <option key={r} value={r}>{r}</option>
        ))}
      </select>
      <select
        className={inputCls}
        value={filters.category || ""}
        onChange={(e) => setFilters({ ...filters, category: e.target.value || undefined })}
      >
        <option value="">All Categories</option>
        {options.categories.map((c) => (
          <option key={c} value={c}>{c}</option>
        ))}
      </select>
      <select
        className={inputCls}
        value={filters.segment || ""}
        onChange={(e) => setFilters({ ...filters, segment: e.target.value || undefined })}
      >
        <option value="">All Segments</option>
        {options.segments.map((s) => (
          <option key={s} value={s}>{s}</option>
        ))}
      </select>
      {(filters.start_date || filters.end_date || filters.region || filters.category || filters.segment) && (
        <button
          onClick={() => setFilters({})}
          className="ml-auto rounded-lg px-3 py-2 text-xs font-medium text-brand-500 hover:bg-brand-500/10"
        >
          Clear filters
        </button>
      )}
    </div>
  );
}
