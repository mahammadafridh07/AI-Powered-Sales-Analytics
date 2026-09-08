import { useEffect, useState } from "react";
import { Package, Megaphone, Users, Map, Sparkles } from "lucide-react";
import { api } from "../lib/api";
import { ChartCard, EmptyState, Skeleton } from "../components/UI";

const ICONS: Record<string, any> = {
  Inventory: Package,
  Marketing: Megaphone,
  "Customer Retention": Users,
  "Regional Strategy": Map,
};

export default function Recommendations() {
  const [recs, setRecs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/recommendations").then((r) => setRecs(r.data.recommendations)).finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-xl font-semibold text-slate-900 dark:text-white">Recommendations</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Data-driven suggestions across inventory, marketing, retention, and regional strategy.
        </p>
      </div>

      {loading ? (
        <Skeleton className="h-64" />
      ) : recs.length === 0 ? (
        <EmptyState title="No recommendations yet" subtitle="Upload more sales data so trends and patterns can be identified." />
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {recs.map((r, i) => {
            const Icon = ICONS[r.category] || Sparkles;
            return (
              <ChartCard key={i} title={r.category}>
                <div className="flex gap-3">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-brand-500/10 text-brand-500">
                    <Icon size={18} />
                  </div>
                  <div>
                    <p className="font-display text-sm font-semibold text-slate-800 dark:text-slate-100">{r.title}</p>
                    <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{r.detail}</p>
                    <span className="mt-2 inline-block rounded-full bg-teal-500/10 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-teal-500">
                      AI-generated suggestion
                    </span>
                  </div>
                </div>
              </ChartCard>
            );
          })}
        </div>
      )}
    </div>
  );
}
