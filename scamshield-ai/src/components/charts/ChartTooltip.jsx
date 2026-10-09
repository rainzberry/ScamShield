import { T } from "../../constants/theme";

export default function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="ss-panel rounded-lg px-3 py-2 text-xs" style={{ background: "rgba(18,21,27,0.95)" }}>
      {label !== undefined && <p className="font-semibold mb-1" style={{ color: T.text }}>{label}</p>}
      {payload.map((p) => (
        <p key={p.dataKey || p.name} style={{ color: p.color || p.payload?.color || T.text }}>
          {p.name}: <span className="ss-mono">{p.value}</span>
        </p>
      ))}
    </div>
  );
}