import { Link, useNavigate } from "react-router-dom";
import { ChevronRight, Search } from "lucide-react";
import { getClassStyle, SCAN_TYPE_LABELS, T } from "../../constants/theme";
import { formatDate } from "../../utils/format";
import ClassBadge from "../common/ClassBadge";
import { EmptyState } from "../common/StateViews";

export default function ScanTable({ scans, emptyTitle = "No scans found", emptyDescription = "Run a new analysis to see results here." }) {
  const navigate = useNavigate();
  if (!scans.length) return <EmptyState icon={Search} title={emptyTitle} description={emptyDescription} />;

  const open = (id) => navigate(`/results/${id}`);

  return (
    <>
      <div className="hidden md:block overflow-x-auto ss-scroll">
        <table className="w-full text-sm min-w-[680px]">
          <caption className="sr-only">Scan history</caption>
          <thead>
            <tr className="text-left" style={{ color: T.textFaint }}>
              {["Date", "Type", "Content", "Classification", "Risk", ""].map((h) => (
                <th key={h || "action"} scope="col" className="font-medium text-xs pb-3 px-1">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {scans.map((s) => (
              <tr key={s.id} onClick={() => open(s.id)} className="cursor-pointer hover:bg-white/[0.02]" style={{ borderTop: `1px solid ${T.border}` }}>
                <td className="py-3 px-1 text-xs whitespace-nowrap" style={{ color: T.textMuted }}>{formatDate(s.createdAt)}</td>
                <td className="py-3 px-1 text-xs" style={{ color: T.textMuted }}>{SCAN_TYPE_LABELS[s.scanType] || s.scanType || "—"}</td>
                <td className="py-3 px-1 text-xs max-w-[280px] truncate">
                  <Link to={`/results/${s.id}`} onClick={(e) => e.stopPropagation()} className="ss-focus rounded" style={{ color: T.text }}>{s.title}</Link>
                </td>
                <td className="py-3 px-1"><ClassBadge classification={s.classification} size="sm" /></td>
                <td className="py-3 px-1">
                  <span className="ss-mono text-xs font-semibold" style={{ color: getClassStyle(s.classification).text }}>{s.riskScore ?? "—"}</span>
                </td>
                <td className="py-3 px-1 text-right"><ChevronRight size={14} color={T.textFaint} aria-hidden="true" /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <ul className="md:hidden flex flex-col gap-2.5">
        {scans.map((s) => (
          <li key={s.id}>
            <Link to={`/results/${s.id}`} className="block rounded-xl p-3.5 ss-focus" style={{ background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}` }}>
              <div className="flex items-center justify-between mb-2">
                <ClassBadge classification={s.classification} size="sm" />
                <span className="ss-mono text-xs font-semibold" style={{ color: getClassStyle(s.classification).text }}>{s.riskScore ?? "—"}/100</span>
              </div>
              <p className="text-sm font-medium truncate mb-0.5" style={{ color: T.text }}>{s.title}</p>
              <div className="flex items-center justify-between text-[11px]" style={{ color: T.textFaint }}>
                <span>{SCAN_TYPE_LABELS[s.scanType] || s.scanType}</span>
                <span>{formatDate(s.createdAt)}</span>
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </>
  );
}