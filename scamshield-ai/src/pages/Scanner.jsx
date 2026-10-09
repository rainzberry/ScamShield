import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { CircleCheck, FileText, Info, Link2, Mail, QrCode } from "lucide-react";
import { T } from "../constants/theme";
import PageHeader from "../components/common/PageHeader";
import Panel from "../components/common/Panel";
import EmailForm from "../components/scanners/EmailForm";
import QrForm from "../components/scanners/QrForm";
import TextForm from "../components/scanners/TextForm";
import UrlForm from "../components/scanners/UrlForm";

const TABS = [
  { id: "email", label: "Email", icon: Mail, Form: EmailForm },
  { id: "url", label: "URL", icon: Link2, Form: UrlForm },
  { id: "text", label: "Text", icon: FileText, Form: TextForm },
  { id: "qr", label: "QR code", icon: QrCode, Form: QrForm },
];

const CHECKS = [
  "Sender and domain signals",
  "URL structure and destination features",
  "Urgency and pressure language",
  "Credential or payment requests",
  "Hidden links inside QR codes",
];

export default function Scanner() {
  const [tab, setTab] = useState("email");
  const navigate = useNavigate();
  const active = TABS.find((t) => t.id === tab);
  const Form = active.Form;

  // The Analysis page performs the real API call; nothing is analysed here.
  function handleSubmit(type, payload) {
    navigate("/analysis", { state: { request: { type, payload } } });
  }

  return (
    <>
      <PageHeader title="Scanner" subtitle="Submit content to the detection backend" />

      <div role="tablist" aria-label="Scan type" className="flex flex-wrap gap-2 mb-6 p-1 rounded-xl w-fit max-w-full" style={{ background: T.panelSolid, border: `1px solid ${T.border}` }}>
        {TABS.map((t) => (
          <button
            key={t.id} role="tab" id={`tab-${t.id}`} aria-selected={tab === t.id} aria-controls={`panel-${t.id}`}
            onClick={() => setTab(t.id)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ss-focus"
            style={tab === t.id ? { background: T.red, color: "#fff", boxShadow: `0 2px 14px -2px ${T.redGlow}` } : { color: T.textMuted }}
          >
            <t.icon size={15} aria-hidden="true" /> {t.label}
          </button>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-5">
        <Panel className="lg:col-span-2 p-6" role="tabpanel" id={`panel-${tab}`} aria-labelledby={`tab-${tab}`}>
          <h2 className="font-semibold text-sm mb-5" style={{ color: T.text }}>{active.label} analysis</h2>
          <Form key={tab} onSubmit={handleSubmit} disabled={false} />
        </Panel>

        <Panel className="p-6 h-fit">
          <h2 className="font-semibold text-sm mb-3 flex items-center gap-2" style={{ color: T.text }}><Info size={15} color={T.textMuted} aria-hidden="true" /> What the engine looks at</h2>
          <ul className="flex flex-col gap-3 text-xs" style={{ color: T.textMuted }}>
            {CHECKS.map((it) => (
              <li key={it} className="flex items-start gap-2"><CircleCheck size={14} className="mt-0.5 flex-shrink-0" color={T.green} aria-hidden="true" />{it}</li>
            ))}
          </ul>
          <p className="mt-5 pt-4 text-[11px] leading-relaxed" style={{ borderTop: `1px solid ${T.border}`, color: T.textFaint }}>
            Content is sent to the ScamShield backend for analysis. Links and decoded QR payloads are never opened. Results are guidance, not a guarantee.
          </p>
        </Panel>
      </div>
    </>
  );
}