import { Shield, ShieldAlert, ShieldCheck, ShieldX, MailWarning, TriangleAlert } from "lucide-react";
import { getClassStyle } from "../../constants/theme";

const ICONS = { safe: ShieldCheck, spam: MailWarning, phishing: ShieldAlert, scam: TriangleAlert, malicious: ShieldX };

export function ClassIcon({ classification, size = 16 }) {
  const Icon = ICONS[classification] || Shield;
  return <Icon size={size} strokeWidth={2} color={getClassStyle(classification).text} aria-hidden="true" />;
}

export default function ClassBadge({ classification, size = "md" }) {
  const c = getClassStyle(classification);
  const pad = size === "sm" ? "px-2 py-0.5 text-[11px]" : "px-2.5 py-1 text-xs";
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-semibold ${pad}`}
      style={{ background: c.soft, color: c.text, border: `1px solid ${c.ring}` }}
    >
      <ClassIcon classification={classification} size={size === "sm" ? 12 : 13} />
      {c.label.toUpperCase()}
    </span>
  );
}
