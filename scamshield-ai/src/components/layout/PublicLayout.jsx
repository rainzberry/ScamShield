import { useState } from "react";
import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { Menu, X } from "lucide-react";
import { T } from "../../constants/theme";
import { useAuth } from "../../context/AuthContext";
import Button from "../common/Button";
import Logo from "../common/Logo";

const LINKS = [{ to: "/about", label: "About" }, { to: "/faq", label: "FAQ" }];

export default function PublicLayout({ contained = false }) {
  const [open, setOpen] = useState(false);
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="ss-bg ss-grid min-h-screen flex flex-col">
      <header
        className="sticky top-0 z-40 px-5 lg:px-10 py-4"
        style={{ background: "rgba(13,16,21,0.85)", backdropFilter: "blur(10px)", borderBottom: `1px solid ${T.border}` }}
      >
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <Link to="/" className="ss-focus rounded-lg" aria-label="ScamShield AI home"><Logo size={32} /></Link>
          <nav className="hidden md:flex items-center gap-7" aria-label="Primary">
            {LINKS.map((l) => (
              <NavLink key={l.to} to={l.to} className="text-sm font-medium ss-focus rounded"
                style={({ isActive }) => ({ color: isActive ? T.text : T.textMuted })}>{l.label}</NavLink>
            ))}
          </nav>
          <div className="hidden md:flex items-center gap-3">
            {isAuthenticated ? (
              <Button size="sm" onClick={() => navigate("/dashboard")}>Open dashboard</Button>
            ) : (
              <>
                <Button variant="ghost" size="sm" onClick={() => navigate("/login")}>Log in</Button>
                <Button size="sm" onClick={() => navigate("/register")}>Get started</Button>
              </>
            )}
          </div>
          <button className="md:hidden p-2 rounded-lg ss-focus" style={{ color: T.textMuted }}
            onClick={() => setOpen((o) => !o)} aria-label={open ? "Close menu" : "Open menu"} aria-expanded={open}>
            {open ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
        {open && (
          <div className="md:hidden mt-4 flex flex-col gap-3 pb-2">
            {LINKS.map((l) => (
              <Link key={l.to} to={l.to} onClick={() => setOpen(false)} className="text-sm font-medium" style={{ color: T.textMuted }}>{l.label}</Link>
            ))}
            {isAuthenticated ? (
              <Button onClick={() => navigate("/dashboard")}>Open dashboard</Button>
            ) : (
              <>
                <Button variant="outline" onClick={() => navigate("/login")}>Log in</Button>
                <Button onClick={() => navigate("/register")}>Get started</Button>
              </>
            )}
          </div>
        )}
      </header>

      <main className="flex-1">
        {contained ? <div className="max-w-5xl mx-auto px-5 lg:px-10 py-12"><Outlet /></div> : <Outlet />}
      </main>

      <footer className="px-5 lg:px-10 py-8 mt-10" style={{ borderTop: `1px solid ${T.border}` }}>
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-xs" style={{ color: T.textFaint }}>
          <p>© 2026 ScamShield AI — a Software Engineering project. Detection results are guidance, not a guarantee.</p>
          <div className="flex gap-5">
            <Link to="/about" className="hover:underline">About</Link>
            <Link to="/faq" className="hover:underline">FAQ</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}