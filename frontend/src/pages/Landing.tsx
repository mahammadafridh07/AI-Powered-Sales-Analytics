import { Link } from "react-router-dom";
import {
  BarChart3, TrendingUp, AlertTriangle, MessageSquareText, Package, Map,
  ArrowRight, CheckCircle2, Sparkles,
} from "lucide-react";

const FEATURES = [
  { icon: BarChart3, title: "Executive Dashboards", text: "Revenue, profit, and order KPIs with real trend indicators — filterable by date, region, category, and segment." },
  { icon: TrendingUp, title: "ML Sales Forecasting", text: "Random Forest and XGBoost models compete on validation data; the best-performing one forecasts 7–90 days ahead." },
  { icon: AlertTriangle, title: "Anomaly Detection", text: "Isolation Forest flags unusual revenue, quantity, and pricing patterns before they become a problem." },
  { icon: MessageSquareText, title: "AI Sales Analyst", text: "Ask plain-English questions. Answers are grounded in real, retrieved analytics — never invented." },
  { icon: Package, title: "Product & Customer Intelligence", text: "Top/worst performers, margin analysis, and data-driven customer segmentation." },
  { icon: Map, title: "Regional Performance", text: "Compare growth, revenue, and profit across every region your business operates in." },
];

const STEPS = [
  { title: "Upload your sales data", text: "Drag in a CSV or Excel export. We validate, clean, and store it automatically." },
  { title: "Explore your analytics", text: "KPIs, trends, and breakdowns update instantly across products, customers, and regions." },
  { title: "Forecast & detect anomalies", text: "ML models trained on your data project future revenue and surface irregularities." },
  { title: "Ask the AI Analyst", text: "Get plain-English answers and recommendations grounded in your actual numbers." },
];

function HeroPulse() {
  // Signature element: an animated revenue "pulse" line that draws itself in,
  // echoing the forecasting/trend theme of the product.
  return (
    <svg viewBox="0 0 480 160" className="w-full max-w-xl" fill="none">
      <defs>
        <linearGradient id="pulseGrad" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#818cf8" />
          <stop offset="100%" stopColor="#2dd4da" />
        </linearGradient>
      </defs>
      <path
        d="M0 120 L40 118 L70 122 L95 90 L120 100 L150 60 L180 78 L210 40 L240 55 L270 20 L300 42 L330 15 L360 30 L390 10 L420 25 L480 5"
        stroke="url(#pulseGrad)"
        strokeWidth="3"
        strokeLinecap="round"
        className="animate-draw"
      />
    </svg>
  );
}

export default function Landing() {
  return (
    <div className="min-h-screen bg-ink-900 text-white">
      {/* Nav */}
      <header className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-brand-500 to-teal-500">
            <BarChart3 size={18} />
          </div>
          <span className="font-display text-lg font-semibold">SalesAI</span>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/login" className="text-sm font-medium text-slate-300 hover:text-white">Sign in</Link>
          <Link to="/register" className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-semibold hover:bg-brand-600">
            Get started
          </Link>
        </div>
      </header>

      {/* Hero */}
      <section className="mx-auto grid max-w-7xl items-center gap-10 px-6 py-16 md:grid-cols-2 md:py-24">
        <div className="animate-fade-up">
          <span className="inline-flex items-center gap-1.5 rounded-full bg-brand-500/10 px-3 py-1 text-xs font-medium text-brand-400">
            <Sparkles size={13} /> Now with an AI Sales Analyst
          </span>
          <h1 className="mt-5 font-display text-4xl font-semibold leading-tight md:text-5xl">
            AI-Powered Sales Analytics <span className="text-brand-400">&amp; Forecasting</span>
          </h1>
          <p className="mt-5 max-w-md text-base text-slate-400">
            Turn sales data into actionable business decisions with analytics, forecasting,
            anomaly detection, and AI-powered insights.
          </p>
          <div className="mt-8 flex items-center gap-4">
            <Link
              to="/register"
              className="flex items-center gap-2 rounded-lg bg-brand-500 px-5 py-3 text-sm font-semibold hover:bg-brand-600"
            >
              Start free <ArrowRight size={16} />
            </Link>
            <Link to="/login" className="text-sm font-medium text-slate-300 hover:text-white">
              I already have an account
            </Link>
          </div>
        </div>
        <div className="flex items-center justify-center rounded-2xl border border-white/5 bg-ink-800 p-8">
          <div className="w-full">
            <div className="mb-4 flex items-baseline justify-between">
              <div>
                <p className="text-xs uppercase tracking-wider text-slate-500">Revenue</p>
                <p className="font-display text-3xl font-semibold">₹24.8Cr</p>
              </div>
              <span className="rounded-full bg-positive-500/10 px-2.5 py-1 text-xs font-medium text-positive-500">
                ↑ 14.8% vs previous period
              </span>
            </div>
            <HeroPulse />
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-7xl px-6 py-16">
        <h2 className="font-display text-2xl font-semibold">Everything a data-driven sales team needs</h2>
        <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map(({ icon: Icon, title, text }) => (
            <div key={title} className="rounded-2xl border border-white/5 bg-ink-800 p-6">
              <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-lg bg-brand-500/10 text-brand-400">
                <Icon size={18} />
              </div>
              <h3 className="font-display text-sm font-semibold">{title}</h3>
              <p className="mt-2 text-sm text-slate-400">{text}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="border-y border-white/5 bg-ink-950/40 py-16">
        <div className="mx-auto max-w-7xl px-6">
          <h2 className="font-display text-2xl font-semibold">How it works</h2>
          <div className="mt-8 grid gap-6 md:grid-cols-4">
            {STEPS.map((s, i) => (
              <div key={s.title} className="relative rounded-2xl border border-white/5 bg-ink-800 p-5">
                <span className="font-display text-xs font-semibold text-teal-400">Step {i + 1}</span>
                <h3 className="mt-2 font-display text-sm font-semibold">{s.title}</h3>
                <p className="mt-2 text-sm text-slate-400">{s.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits */}
      <section className="mx-auto max-w-7xl px-6 py-16">
        <div className="grid gap-8 md:grid-cols-2">
          <div>
            <h2 className="font-display text-2xl font-semibold">Built for real decisions, not vanity metrics</h2>
            <p className="mt-3 text-slate-400">
              Every chart, forecast, and AI answer traces back to your actual uploaded data —
              no fabricated numbers, no black-box magic.
            </p>
          </div>
          <ul className="space-y-3">
            {[
              "Model comparison with real MAE, RMSE, and MAPE — best model auto-selected",
              "Isolation Forest anomaly detection, not arbitrary thresholds",
              "Safe, read-only query layer between the AI and your database",
              "Works immediately with the bundled realistic sample dataset",
            ].map((b) => (
              <li key={b} className="flex items-start gap-3 text-sm text-slate-300">
                <CheckCircle2 size={18} className="mt-0.5 shrink-0 text-teal-400" />
                {b}
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* CTA */}
      <section className="mx-auto max-w-7xl px-6 pb-20">
        <div className="rounded-3xl bg-gradient-to-br from-brand-600 to-teal-500 px-8 py-14 text-center">
          <h2 className="font-display text-2xl font-semibold md:text-3xl">Ready to see your sales data differently?</h2>
          <p className="mx-auto mt-3 max-w-md text-sm text-white/85">
            Sign up and explore the platform instantly with the built-in demo dataset.
          </p>
          <Link
            to="/register"
            className="mt-6 inline-flex items-center gap-2 rounded-lg bg-white px-5 py-3 text-sm font-semibold text-ink-900 hover:bg-slate-100"
          >
            Get started free <ArrowRight size={16} />
          </Link>
        </div>
      </section>

      <footer className="border-t border-white/5 py-8 text-center text-xs text-slate-500">
        © {new Date().getFullYear()} SalesAI. Built as a portfolio analytics platform.
      </footer>
    </div>
  );
}
