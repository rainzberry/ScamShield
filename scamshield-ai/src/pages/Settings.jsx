import { useNavigate } from "react-router-dom";
import { Activity, Inbox, Info, LogOut, RefreshCw, User } from "lucide-react";
import { API_BASE_URL } from "../api/client";
import { T } from "../constants/theme";
import { useAuth } from "../context/AuthContext";
import useHealth from "../hooks/useHealth";
import useLocalStorage from "../hooks/useLocalStorage";
import Button from "../components/common/Button";
import PageHeader from "../components/common/PageHeader";
import Panel from "../components/common/Panel";
import { InlineAlert } from "../components/common/StateViews";
import { GMAIL_DEMO_KEY } from "./Gmail";

function Row({ label, children }) {
  return (
    <div className="flex items-center justify-between gap-4 py-3" style={{ borderBottom: `1px solid ${T.border}` }}>
      <span className="text-xs" style={{ color: T.textMuted }}>{label}</span>
      <span className="text-sm text-right break-all" style={{ color: T.text }}>{children}</span>
    </div>
  );
}

function Section({ icon: Icon, title, children }) {
  return (
    <Panel className="p-5 lg:p-6">
      <h2 className="font-semibold text-sm mb-2 flex items-center gap-2" style={{ color: T.text }}><Icon size={15} color={T.textMuted} aria-hidden="true" /> {title}</h2>
      {children}
    </Panel>
  );
}

export default function Settings() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const health = useHealth(0);
  const [gmailConnected, setGmailConnected] = useLocalStorage(GMAIL_DEMO_KEY, false);

  async function handleLogout() {
    navigate("/", { replace: true });
    await logout();
  }

  const statusText = { checking: "Checking...", online: "Online", degraded: "Online, model unavailable", offline: "Backend unavailable" }[health.status];
  const statusColor = { checking: T.textFaint, online: T.green, degraded: T.amber, offline: T.red }[health.status];
  const d = health.data || {};

  return (
    <>
      <PageHeader title="Settings" subtitle="Account, backend status and application information" />
      <div className="grid lg:grid-cols-2 gap-5 max-w-5xl">
        <Section icon={User} title="Account">
          <Row label="Name">{user?.name || "—"}</Row>
          <Row label="Email">{user?.email || "—"}</Row>
          <div className="pt-4"><Button variant="outline" icon={LogOut} onClick={handleLogout}>Log out</Button></div>
        </Section>

        <Section icon={Activity} title="Backend status">
          <Row label="API"><span style={{ color: statusColor }}>{statusText}</span></Row>
          <Row label="API host">{(() => { try { return new URL(API_BASE_URL).host; } catch { return "—"; } })()}</Row>
          {d.version && <Row label="API version">{String(d.version)}</Row>}
          {(d.model_version || d.model) && <Row label="Model">{String(d.model_version || d.model)}</Row>}
          {d.model_loaded !== undefined && <Row label="Model loaded">{d.model_loaded ? "Yes" : "No"}</Row>}
          {health.status === "offline" && <InlineAlert tone="error" className="mt-3">{health.error}</InlineAlert>}
          <div className="pt-4"><Button variant="outline" size="sm" icon={RefreshCw} onClick={health.refresh}>Check again</Button></div>
        </Section>

        <Section icon={Inbox} title="Gmail connection">
          <Row label="Mode">Demo (sample messages only)</Row>
          <Row label="State">{gmailConnected ? "Demo inbox loaded" : "Not loaded"}</Row>
          <p className="text-[11px] mt-3" style={{ color: T.textFaint }}>Demo Mode — sample messages only. No real Google account is accessed.</p>
          {gmailConnected && <div className="pt-3"><Button variant="outline" size="sm" onClick={() => setGmailConnected(false)}>Reset demo inbox</Button></div>}
        </Section>

        <Section icon={Info} title="Application">
          <Row label="Application">ScamShield AI</Row>
          <Row label="Frontend version">1.0.0</Row>
          <Row label="Theme">Dark (fixed)</Row>
          <p className="text-[11px] mt-3" style={{ color: T.textFaint }}>Detection results are guidance and not a guarantee of safety.</p>
        </Section>
      </div>
    </>
  );
}