import { T } from "../../constants/theme";

/* value: number 0-100 or null (renders an empty ring and an em dash) */
export default function RadialMeter({ value, label, sub, color, glow, unit = "/ 100", size = 148 }) {
  const r = 52;
  const c = 2 * Math.PI * r;
  const safeValue = typeof value === "number" ? Math.max(0, Math.min(100, value)) : 0;
  const offset = c - (safeValue / 100) * c;
  return (
    <div className="flex flex-col items-center" role="img" aria-label={`${label}: ${typeof value === "number" ? `${value} ${unit}` : "not available"}`}>
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} viewBox="0 0 120 120" className="-rotate-90" aria-hidden="true">
          <circle cx="60" cy="60" r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="9" />
          <circle
            cx="60" cy="60" r={r} fill="none" stroke={color} strokeWidth="9" strokeLinecap="round"
            strokeDasharray={c} strokeDashoffset={offset} className="ss-ring"
            style={{ filter: `drop-shadow(0 0 8px ${glow})`, transition: "stroke-dashoffset 1s cubic-bezier(.22,.9,.3,1)" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="ss-mono ss-display font-bold" style={{ fontSize: size / 4.6, color: T.text }}>
            {typeof value === "number" ? value : "—"}
          </span>
          <span className="text-[10px] tracking-wide" style={{ color: T.textFaint }}>{unit}</span>
        </div>
      </div>
      <p className="text-xs font-semibold mt-3 tracking-wide" style={{ color: T.textMuted }}>{label}</p>
      {sub && <p className="text-[11px] mt-0.5" style={{ color: T.textFaint }}>{sub}</p>}
    </div>
  );
}