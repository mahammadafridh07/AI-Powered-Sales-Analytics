import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import {
  LayoutDashboard, Package, Users, Map, TrendingUp, AlertTriangle,
  MessageSquareText, Lightbulb, Settings as SettingsIcon, Menu, X,
  Sun, Moon, LogOut, BarChart3, UploadCloud,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";

const NAV = [
  { to: "/app/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/app/products", label: "Products", icon: Package },
  { to: "/app/customers", label: "Customers", icon: Users },
  { to: "/app/regions", label: "Regions", icon: Map },
  { to: "/app/forecast", label: "Forecast", icon: TrendingUp },
  { to: "/app/anomalies", label: "Anomalies", icon: AlertTriangle },
  { to: "/app/ai-analyst", label: "AI Analyst", icon: MessageSquareText },
  { to: "/app/recommendations", label: "Recommendations", icon: Lightbulb },
  { to: "/app/upload", label: "Upload Data", icon: UploadCloud },
];

export default function AppShell({ children }: { children: React.ReactNode }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const { user, logout } = useAuth();
  const { theme, toggle } = useTheme();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  const SidebarContent = (
    <>
      <div className={`flex items-center gap-2 px-4 py-5 ${collapsed ? "justify-center" : ""}`}>
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-brand-500 to-teal-500 text-white">
          <BarChart3 size={18} />
        </div>
        {!collapsed && <span className="font-display text-lg font-semibold text-white">SalesAI</span>}
      </div>
      <nav className="flex-1 space-y-1 px-3">
        {NAV.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            onClick={() => setMobileOpen(false)}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors ${
                isActive
                  ? "bg-brand-500/15 text-brand-400"
                  : "text-slate-400 hover:bg-white/5 hover:text-white"
              } ${collapsed ? "justify-center" : ""}`
            }
          >
            <Icon size={18} />
            {!collapsed && label}
          </NavLink>
        ))}
      </nav>
      <div className="px-3 pb-4">
        <NavLink
          to="/app/settings"
          onClick={() => setMobileOpen(false)}
          className={({ isActive }) =>
            `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors ${
              isActive ? "bg-brand-500/15 text-brand-400" : "text-slate-400 hover:bg-white/5 hover:text-white"
            } ${collapsed ? "justify-center" : ""}`
          }
        >
          <SettingsIcon size={18} />
          {!collapsed && "Settings"}
        </NavLink>
      </div>
    </>
  );

  return (
    <div className="flex h-screen overflow-hidden bg-mist-100 dark:bg-ink-900">
      {/* Desktop sidebar */}
      <aside
        className={`hidden md:flex md:flex-col border-r border-white/5 bg-ink-950 transition-all ${
          collapsed ? "md:w-[76px]" : "md:w-64"
        }`}
      >
        {SidebarContent}
      </aside>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-40 md:hidden">
          <div className="absolute inset-0 bg-black/50" onClick={() => setMobileOpen(false)} />
          <aside className="absolute left-0 top-0 flex h-full w-64 flex-col bg-ink-950">
            <button
              className="absolute right-3 top-4 text-slate-400"
              onClick={() => setMobileOpen(false)}
              aria-label="Close menu"
            >
              <X size={20} />
            </button>
            {SidebarContent}
          </aside>
        </div>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-slate-200 bg-white/80 px-4 py-3 backdrop-blur dark:border-white/5 dark:bg-ink-900/80 md:px-6">
          <div className="flex items-center gap-3">
            <button
              className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-white/5 md:hidden"
              onClick={() => setMobileOpen(true)}
              aria-label="Open menu"
            >
              <Menu size={20} />
            </button>
            <button
              className="hidden rounded-lg p-2 text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-white/5 md:block"
              onClick={() => setCollapsed((c) => !c)}
              aria-label="Toggle sidebar"
            >
              <Menu size={18} />
            </button>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={toggle}
              className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-white/5"
              aria-label="Toggle theme"
            >
              {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
            </button>
            <div className="mx-1 hidden h-6 w-px bg-slate-200 dark:bg-white/10 sm:block" />
            <div className="hidden items-center gap-2 sm:flex">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-500/15 text-sm font-semibold text-brand-500">
                {user?.name?.[0]?.toUpperCase() || "U"}
              </div>
              <span className="text-sm font-medium text-slate-700 dark:text-slate-200">{user?.name}</span>
            </div>
            <button
              onClick={handleLogout}
              className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-negative-500 dark:text-slate-400 dark:hover:bg-white/5"
              aria-label="Log out"
              title="Log out"
            >
              <LogOut size={18} />
            </button>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-4 md:p-6">{children}</main>
      </div>
    </div>
  );
}
