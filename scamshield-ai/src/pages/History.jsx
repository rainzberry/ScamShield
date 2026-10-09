import { useState } from "react";
import { ArrowUpDown } from "lucide-react";
import { listScans } from "../api/scanApi";
import { CLASSIFICATIONS, getClassStyle, SCAN_TYPES, SCAN_TYPE_LABELS, T } from "../constants/theme";
import useFetch from "../hooks/useFetch";
import PageHeader from "../components/common/PageHeader";
import Panel from "../components/common/Panel";
import { ErrorState, LoadingState } from "../components/common/StateViews";
import Pagination from "../components/history/Pagination";
import ScanTable from "../components/history/ScanTable";

const PER_PAGE = 10;
const SORTS = {
  newest: { sort_by: "created_at", order: "desc", label: "Newest first" },
  oldest: { sort_by: "created_at", order: "asc", label: "Oldest first" },
  risk: { sort_by: "risk_score", order: "desc", label: "Highest risk" },
};

export default function History() {
  const [page, setPage] = useState(1);
  const [classification, setClassification] = useState("all");
  const [scanType, setScanType] = useState("all");
  const [sort, setSort] = useState("newest");

  const { data, loading, error, reload } = useFetch(() => {
    const params = { page, per_page: PER_PAGE, sort_by: SORTS[sort].sort_by, order: SORTS[sort].order };
    if (classification !== "all") params.classification = classification;
    if (scanType !== "all") params.scan_type = scanType;
    return listScans(params);
  }, [page, classification, scanType, sort]);

  const update = (setter) => (value) => { setter(value); setPage(1); };
  const filtered = classification !== "all" || scanType !== "all";

  return (
    <>
      <PageHeader title="Scan history" subtitle={data ? `${data.total} stored ${data.total === 1 ? "scan" : "scans"}` : "Your stored scans"} />

      <Panel className="p-4 mb-5">
        <div className="flex flex-col md:flex-row gap-3 md:items-center md:justify-between">
          <div className="flex flex-wrap gap-2" role="group" aria-label="Filter by classification">
            {["all", ...CLASSIFICATIONS].map((id) => {
              const active = classification === id;
              const s = getClassStyle(id);
              return (
                <button key={id} onClick={() => update(setClassification)(id)} aria-pressed={active}
                  className="text-xs font-medium px-3 py-1.5 rounded-full transition-all ss-focus"
                  style={active
                    ? { background: id === "all" ? T.panelSolid : s.soft, color: id === "all" ? T.text : s.text, border: `1px solid ${id === "all" ? T.borderBright : s.ring}` }
                    : { color: T.textMuted, border: `1px solid ${T.border}` }}>
                  {id === "all" ? "All" : s.label}
                </button>
              );
            })}
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <select aria-label="Filter by scan type" value={scanType} onChange={(e) => update(setScanType)(e.target.value)} className="ss-input !w-auto text-xs">
              <option value="all">All types</option>
              {SCAN_TYPES.map((t) => <option key={t} value={t}>{SCAN_TYPE_LABELS[t]}</option>)}
            </select>
            <ArrowUpDown size={14} color={T.textFaint} aria-hidden="true" />
            <select aria-label="Sort scans" value={sort} onChange={(e) => update(setSort)(e.target.value)} className="ss-input !w-auto text-xs">
              {Object.entries(SORTS).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
            </select>
          </div>
        </div>
      </Panel>

      <Panel className="p-5">
        {loading && <LoadingState label="Loading scans..." />}
        {error && <ErrorState title="Could not load history" message={error} onRetry={reload} />}
        {data && !loading && (
          <>
            <ScanTable
              scans={data.scans}
              emptyTitle={filtered ? "No scans match these filters" : "No scans yet"}
              emptyDescription={filtered ? "Try changing or clearing the filters." : "Run an analysis from the Scanner page and it will appear here."}
            />
            <Pagination page={data.page} pages={data.pages} total={data.total} onChange={setPage} />
          </>
        )}
      </Panel>
    </>
  );
}