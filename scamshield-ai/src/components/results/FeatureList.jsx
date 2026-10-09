import { T } from "../../constants/theme";

function describe(item) {
  if (typeof item === "string") return { name: item };
  const name = item.feature ?? item.name ?? item.label ?? item.rule ?? item.code ?? "Feature";
  const raw = item.weight ?? item.importance ?? item.contribution ?? item.score ?? item.value;
  const num = typeof raw === "number" ? raw : Number.isFinite(Number(raw)) && raw !== null && raw !== "" ? Number(raw) : null;
  const detail = item.description ?? item.evidence ?? item.reason ?? item.explanation ?? "";
  return { name: String(name), num, raw, detail: typeof detail === "string" ? detail : JSON.stringify(detail) };
}

/* Generic renderer for backend-provided feature evidence.
   Accepts strings or objects like { feature, weight/importance/contribution/score/value, description }. */
export function FeatureList({ items, emptyText }) {
  if (!items || !items.length) {
    return <p className="text-sm" style={{ color: T.textMuted }}>{emptyText}</p>;
  }
  const rows = items.map(describe);
  const maxAbs = Math.max(0.0001, ...rows.map((r) => (r.num === null ? 0 : Math.abs(r.num))));
  return (
    <ul className="flex flex-col gap-3">
      {rows.map((r, i) => {
        const color = r.num !== null && r.num < 0 ? T.green : T.red;
        return (
          <li key={`${r.name}-${i}`}>
            <div className="flex items-center justify-between gap-3 text-sm">
              <span className="ss-mono text-xs break-all" style={{ color: T.text }}>{r.name}</span>
              {r.num !== null
                ? <span className="ss-mono text-xs flex-shrink-0" style={{ color }}>{Math.round(r.num * 1000) / 1000}</span>
                : r.raw !== undefined && r.raw !== "" && <span className="text-xs flex-shrink-0 break-all" style={{ color: T.textMuted }}>{String(r.raw)}</span>}
            </div>
            {r.num !== null && (
              <div className="h-1.5 rounded-full mt-1.5" style={{ background: "rgba(255,255,255,0.06)" }} aria-hidden="true">
                <div className="h-full rounded-full" style={{ width: `${Math.min(100, (Math.abs(r.num) / maxAbs) * 100)}%`, background: color }} />
              </div>
            )}
            {r.detail && <p className="text-xs mt-1 break-words" style={{ color: T.textMuted }}>{r.detail}</p>}
          </li>
        );
      })}
    </ul>
  );
}

/* Key/value table for URL feature analysis (object) or a list (array). */
export function KeyValueList({ data }) {
  if (!data) return null;
  if (Array.isArray(data)) return <FeatureList items={data} emptyText="No URL features were returned." />;
  const entries = Object.entries(data);
  if (!entries.length) return <p className="text-sm" style={{ color: T.textMuted }}>No URL features were returned.</p>;
  const show = (v) => (typeof v === "boolean" ? (v ? "Yes" : "No") : typeof v === "object" ? JSON.stringify(v) : String(v));
  return (
    <dl className="grid sm:grid-cols-2 gap-x-6 gap-y-2.5">
      {entries.map(([k, v]) => (
        <div key={k} className="flex items-baseline justify-between gap-3 pb-2" style={{ borderBottom: `1px solid ${T.border}` }}>
          <dt className="text-xs" style={{ color: T.textMuted }}>{k.replace(/_/g, " ")}</dt>
          <dd className="ss-mono text-xs text-right break-all" style={{ color: T.text }}>{show(v)}</dd>
        </div>
      ))}
    </dl>
  );
}