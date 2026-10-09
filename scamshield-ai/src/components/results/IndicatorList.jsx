import { CircleCheck, TriangleAlert } from "lucide-react";
import { severityColor, T } from "../../constants/theme";

export default function IndicatorList({ indicators, positive }) {
  if (!indicators.length) {
    return <p className="text-sm" style={{ color: T.textMuted }}>The backend did not report any indicators for this scan.</p>;
  }
  return (
    <ul className="flex flex-col gap-2.5">
      {indicators.map((ind, idx) => {
        const color = positive ? T.green : severityColor(ind.severity);
        return (
          <li key={`${ind.code}-${idx}`} className="flex items-start gap-3 rounded-xl p-3.5"
            style={{ background: positive ? T.greenSoft : "rgba(255,255,255,0.03)", border: `1px solid ${positive ? T.greenGlow : T.border}` }}>
            {positive
              ? <CircleCheck size={16} color={color} className="mt-0.5 flex-shrink-0" aria-hidden="true" />
              : <TriangleAlert size={16} color={color} className="mt-0.5 flex-shrink-0" aria-hidden="true" />}
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <p className="text-sm font-medium" style={{ color: T.text }}>{ind.label}</p>
                <span className="text-[10px] px-1.5 py-0.5 rounded font-semibold uppercase" style={{ color: severityColor(ind.severity), background: "rgba(255,255,255,0.05)" }}>{ind.severity}</span>
                {ind.code && <span className="ss-mono text-[10px]" style={{ color: T.textFaint }}>{ind.code}</span>}
              </div>
              {ind.evidence && <p className="text-xs mt-1 break-words" style={{ color: T.textMuted }}>{ind.evidence}</p>}
            </div>
          </li>
        );
      })}
    </ul>
  );
}