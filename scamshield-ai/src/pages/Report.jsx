import { Link, useParams } from "react-router-dom";
import { ArrowLeft, Printer } from "lucide-react";
import { getReport } from "../api/reportApi";
import { SCAN_TYPE_LABELS, T } from "../constants/theme";
import useFetch from "../hooks/useFetch";
import { formatDateTime } from "../utils/format";
import Button from "../components/common/Button";
import PageHeader from "../components/common/PageHeader";
import Panel from "../components/common/Panel";
import { ErrorState, LoadingState } from "../components/common/StateViews";
import ResultView from "../components/results/ResultView";

export default function Report() {
  const { scanId } = useParams();
  const { data: report, loading, error, reload } = useFetch(() => getReport(scanId), [scanId]);

  return (
    <>
      <Link to={`/results/${scanId}`} className="inline-flex items-center gap-1.5 text-xs font-medium mb-4 ss-focus rounded no-print" style={{ color: T.textMuted }}>
        <ArrowLeft size={14} aria-hidden="true" /> Back to result
      </Link>
      <PageHeader
        title="Security report"
        subtitle={`Scan ID: ${scanId}`}
        actions={report && <Button variant="outline" icon={Printer} onClick={() => window.print()}>Print / Save as PDF</Button>}
      />
      {loading && <LoadingState label="Loading report..." />}
      {error && <ErrorState title="Could not load this report" message={error} onRetry={reload} />}
      {report && (
        <div className="ss-report">
          <Panel className="p-5 mb-5 max-w-4xl">
            <h2 className="sr-only">Report metadata</h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
              {[
                ["SCAN ID", report.id],
                ["SCAN TYPE", SCAN_TYPE_LABELS[report.scanType] || report.scanType],
                ["SCAN DATE", formatDateTime(report.createdAt)],
                ["REPORT GENERATED", report.generatedAt ? formatDateTime(report.generatedAt) : "—"],
              ].map(([k, v]) => (
                <div key={k} className="min-w-0">
                  <p style={{ color: T.textFaint }}>{k}</p>
                  <p className="ss-mono font-medium mt-0.5 break-all" style={{ color: T.text }}>{v || "—"}</p>
                </div>
              ))}
            </div>
          </Panel>
          <ResultView scan={report} isReport />
        </div>
      )}
    </>
  );
}