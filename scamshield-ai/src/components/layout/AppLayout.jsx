import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import {
  Activity, History, HelpCircle, Inbox, Info, LayoutDashboard, LogOut, Menu, ScanLine, Settings, User, X,
} from "lucide-react";
import { T } from "../../constants/theme";
import { useAuth } from "../../context/AuthContext";
import useHealth from "../../hooks/useHealth";
import Logo from "../common/Logo";

const NAV = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/scanner", label: "Scanner", icon: ScanLine },
  { to: "/gmail", label: "Gmail (Demo)", icon: Inbox },
  { to: "/history", label: "History", icon: History },
  { to: "/about", label: "About", icon: Info },
  { to: "/faq", label: "FAQ", icon: HelpCircle },
  { to: "/settings", label: "Settings", icon: Settings },
];

function SidebarContent({ onNavigate }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    onNavigate?.();
    navigate("/", { replace: true });
    await logout();
  }

  return (
    <div className="flex flex-col h-full">
      <div className="px-2 py-2 mb-6"><Logo showTagline /></div>
      <nav className="flex flex-col gap-1 flex-1" aria-label="Main">
        {NAV.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            onClick={onNavigate}
            className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors ss-focus hover:bg-white/5"
            style={({ isActive }) => ({
              color: isActive ? T.text : T.textMuted,
              background: isActive ? "rgba(255,59,82,0.08)" : undefined,
              borderLeft: `2px solid ${isActive ? T.red : "transparent"}`,
            })}
          >
            {({ isActive }) => (
              <>
                <Icon size={18} strokeWidth={isActive ? 2.3 : 2} color={isActive ? T.red : undefined} aria-hidden="true" />
                <span>{label}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>
      <div className="pt-4 mt-4" style={{ borderTop: `1px solid ${T.border}` }}>
        <div className="flex items-center gap-2.5 px-3 py-2 rounded-xl mb-1" style={{ background: "rgba(255,255,255,0.03)" }}>
          <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0" style={{ background: T.panelSolid, border: `1px solid ${T.border}` }}>
            <User size={14} color={T.textMuted} aria-hidden="true" />
          </div>
          <div className="min-w-0">
            <p className="text-xs font-medium truncate" style={{ color: T.text }}>{user?.name || "Account"}</p>
            <p className="text-[10px] truncate" style={{ color: T.textFaint }}>{user?.email || ""}</p>
          </div>
        </div>
        <button onClick={handleLogout} className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-medium ss-focus hover:text-white" style={{ color: T.textMuted }}>
          <LogOut size={15} aria-hidden="true" /> Log out
        </button>
      </div>
    </div>
  );
}

function ApiStatus() {
  const { status } = useHealth(60000);
  const map = {
    checking: { text: "Checking API", color: T.textFaint },
    online: { text: "API online", color: T.green },
    degraded: { text: "Model unavailable", color: T.amber },
    offline: { text: "Backend unavailable", color: T.red },
  };
  const s = map[status];
  return (
    <span className="inline-flex items-center gap-2 text-xs rounded-full px-3 py-1.5" role="status"
      style={{ background: T.panelSolid, border: `1px solid ${T.border}`, color: T.textMuted }}>
      <Activity size={12} color={s.color} aria-hidden="true" />
      <span className="w-1.5 h-1.5 rounded-full" style={{ background: s.color }} aria-hidden="true" />
      {s.text}
    </span>
  );
}

export default function AppLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { user } = useAuth();
  const location = useLocation();

  useEffect(() => { setMobileOpen(false); }, [location.pathname]);

  useEffect(() => {
    if (!mobileOpen) return undefined;
    const onKey = (e) => { if (e.key === "Escape") setMobileOpen(false); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [mobileOpen]);

  return (
    <div className="flex min-h-screen ss-bg ss-grid">
      <aside className="hidden lg:flex flex-col w-64 flex-shrink-0 p-4 h-screen sticky top-0 no-print" style={{ borderRight: `1px solid ${T.border}` }}>
        <SidebarContent />
      </aside>

      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden no-print" role="dialog" aria-modal="true" aria-label="Navigation menu">
          <div className="absolute inset-0 bg-black/60" onClick={() => setMobileOpen(false)} aria-hidden="true" />
          <aside className="absolute left-0 top-0 h-full w-72 p-4 ss-bg ss-fade-up" style={{ borderRight: `1px solid ${T.border}` }}>
            <button onClick={() => setMobileOpen(false)} className="absolute top-4 right-4 p-1.5 rounded-lg ss-focus" style={{ color: T.textMuted }} aria-label="Close menu">
              <X size={18} />
            </button>
            <SidebarContent onNavigate={() => setMobileOpen(false)} />
          </aside>
        </div>
      )}

      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-3 px-5 lg:px-8 py-3 sticky top-0 z-30 no-print"
          style={{ background: "rgba(13,16,21,0.85)", backdropFilter: "blur(10px)", borderBottom: `1px solid ${T.border}` }}>
          <button onClick={() => setMobileOpen(true)} className="lg:hidden p-2 rounded-lg ss-focus"
            style={{ color: T.textMuted, background: T.panelSolid, border: `1px solid ${T.border}` }} aria-label="Open menu">
            <Menu size={18} />
          </button>
          <div className="hidden lg:block" />
          <div className="flex items-center gap-3">
            <ApiStatus />
            <span className="hidden sm:inline text-xs font-medium" style={{ color: T.text }}>{user?.name || user?.email}</span>
          </div>
        </div>
        <main className="px-5 lg:px-8 py-6 lg:py-8 max-w-[1400px]">
          <Outlet />
        </main>
      </div>
    </div>
  );
}