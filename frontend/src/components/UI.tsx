import { ArrowUpRight, ArrowDownRight, Inbox } from "lucide-react";

export function formatCurrency(value: number): string {
  if (Math.abs(value) >= 10000000) return `₹${(value / 10000000).toFixed(2)}Cr`;
  if (Math.abs(value) >= 100000) return `₹${(value / 100000).toFixed(2)}L`;
  if (Math.abs(value) >= 1000) return `₹${(value / 1000).toFixed(1)}K`;
  return `₹${value.toFixed(0)}`;
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat("en-IN").format(Math.round(value));
}

export function Card({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <div
      className={`rounded-2xl border border-ink-600/40 bg-white dark:bg-ink-800 shadow-sm shadow-black/5 dark:shadow-black/20 ${className}`}
    >
      {children}
    </div>
  );
}

export function KpiCard({
  label,
  value,
  growth,
  isCurrency = true,
  isInteger = false,
  isPercent = false,
}: {
  label: string;
  value: number;
  growth?: number;
  isCurrency?: boolean;
  isInteger?: boolean;
  isPercent?: boolean;
}) {
  const positive = (growth ?? 0) >= 0;
  const display = isPercent
    ? `${value.toFixed(1)}%`
    : isCurrency
    ? formatCurrency(value)
    : isInteger
    ? formatNumber(value)
    : formatCurrency(value);
  return (
    <Card className="p-5 animate-fade-up">
      <p className="text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">{label}</p>
      <p className="mt-2 font-display text-2xl font-semibold text-slate-900 dark:text-white">{display}</p>
      {growth !== undefined && (
        <div
          className={`mt-2 inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${
            positive
              ? "bg-positive-500/10 text-positive-500"
              : "bg-negative-500/10 text-negative-500"
          }`}
        >
          {positive ? <ArrowUpRight size={13} /> : <ArrowDownRight size={13} />}
          {Math.abs(growth).toFixed(1)}%
        </div>
      )}
    </Card>
  );
}

export function ChartCard({
  title,
  action,
  children,
}: {
  title: string;
  action?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <Card className="p-5">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="font-display text-sm font-semibold text-slate-800 dark:text-slate-100">{title}</h3>
        {action}
      </div>
      {children}
    </Card>
  );
}

export function EmptyState({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-ink-500/40 py-16 text-center">
      <div className="rounded-full bg-brand-500/10 p-3 text-brand-500">
        <Inbox size={22} />
      </div>
      <p className="font-display text-sm font-semibold text-slate-700 dark:text-slate-200">{title}</p>
      {subtitle && <p className="max-w-sm text-xs text-slate-500 dark:text-slate-400">{subtitle}</p>}
    </div>
  );
}

export function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded-lg bg-slate-200 dark:bg-ink-700 ${className}`} />;
}

export function SeverityBadge({ severity }: { severity: string }) {
  const styles: Record<string, string> = {
    High: "bg-negative-500/10 text-negative-500",
    Medium: "bg-warning-500/10 text-warning-500",
    Low: "bg-positive-500/10 text-positive-500",
  };
  return (
    <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${styles[severity] || styles.Low}`}>
      {severity}
    </span>
  );
}
