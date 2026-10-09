import { AlertTriangle, CircleCheck, Info, Inbox, Loader2, TriangleAlert } from "lucide-react";
import { T } from "../../constants/theme";
import Button from "./Button";
import Panel from "./Panel";

export function LoadingState({ label = "Loading..." }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-3" role="status" aria-live="polite">
      <Loader2 size={26} className="animate-spin" color={T.red} aria-hidden="true" />
      <p className="text-sm" style={{ color: T.textMuted }}>{label}</p>
    </div>
  );
}

export function ErrorState({ title = "Something went wrong", message, onRetry }) {
  return (
    <Panel className="flex flex-col items-center text-center py-14 px-6" role="alert">
      <div className="rounded-2xl p-4 mb-4" style={{ background: T.redSoft, border: `1px solid ${T.redGlow}` }}>
        <AlertTriangle size={26} color={T.red} aria-hidden="true" />
      </div>
      <p className="ss-display font-semibold text-base mb-1" style={{ color: T.text }}>{title}</p>
      <p className="text-sm max-w-md mb-5" style={{ color: T.textMuted }}>{message}</p>
      {onRetry && <Button variant="outline" onClick={onRetry}>Try again</Button>}
    </Panel>
  );
}

export function EmptyState({ icon: Icon = Inbox, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-16 px-6">
      <div className="rounded-2xl p-4 mb-4" style={{ background: T.panelSolid, border: `1px solid ${T.border}` }}>
        <Icon size={28} color={T.textFaint} aria-hidden="true" />
      </div>
      <p className="ss-display font-semibold text-base mb-1" style={{ color: T.text }}>{title}</p>
      <p className="text-sm max-w-sm mb-5" style={{ color: T.textMuted }}>{description}</p>
      {action}
    </div>
  );
}

const TONES = {
  error: { icon: TriangleAlert, color: T.red, bg: T.redSoft, border: T.redGlow },
  warning: { icon: Info, color: T.amber, bg: T.amberSoft, border: T.amberGlow },
  success: { icon: CircleCheck, color: T.green, bg: T.greenSoft, border: T.greenGlow },
  info: { icon: Info, color: T.textMuted, bg: "rgba(255,255,255,0.03)", border: T.border },
};

export function InlineAlert({ tone = "info", children, className = "" }) {
  const t = TONES[tone];
  const Icon = t.icon;
  return (
    <div
      role={tone === "error" ? "alert" : "status"}
      className={`flex items-start gap-2 rounded-lg px-3 py-2.5 text-xs leading-relaxed ${className}`}
      style={{ background: t.bg, border: `1px solid ${t.border}`, color: t.color }}
    >
      <Icon size={14} className="mt-0.5 flex-shrink-0" aria-hidden="true" />
      <span>{children}</span>
    </div>
  );
}