import { Link, useParams } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { getScan } from "../api/scanApi";
import { T } from "../constants/theme";
import useFetch from "../hooks/useFetch";
import PageHeader from "../components/common/PageHeader";
import { ErrorState, LoadingState } from "../components/common/StateViews";
import ResultView from "../components/results/ResultView";

export default function Results() {
  const { scanId } = useParams();
  const { data: scan, loading, error, reload } = useFetch(() => getScan(scanId), [scanId]);

  return (
    <>
      <Link to="/history" className="inline-flex items-center gap-1.5 text-xs font-medium mb-4 ss-focus rounded" style={{ color: T.textMuted }}>
        <ArrowLeft size={14} aria-hidden="true" /> Back to history
      </Link>
      <PageHeader title="Analysis result" subtitle={scan?.title || `Scan ${scanId}`} />
      {loading && <LoadingState label="Loading result..." />}
      {error && <ErrorState title="Could not load this result" message={error} onRetry={reload} />}
      {scan && <ResultView scan={scan} />}
    </>
  );
}