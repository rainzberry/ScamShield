import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { AlertTriangle, ScanLine } from "lucide-react";
import { runAnalysis } from "../api/scanApi";
import { T } from "../constants/theme";
import Button from "../components/common/Button";
import PageHeader from "../components/common/PageHeader";
import Panel from "../components/common/Panel";
import { EmptyState, ErrorState } from "../components/common/StateViews";

/* The animation here is PRESENTATIONAL ONLY. It does not represent individual ML stages.
   The elapsed timer is real. Navigation to Results happens only after the backend responds. */
export default function Analysis() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const request = state?.request ?? null;

  const [attempt, setAttempt] = useState(0);
  const [error, setError] = useState(null);
  const [elapsed, setElapsed] = useState(0);
  const mounted = useRef(false);
  const startedAttempt = useRef(-1);

  useEffect(() => {
    mounted.current = true;
    return () => { mounted.current = false; };
  }, []);

  useEffect(() => {
    if (!request || startedAttempt.current === attempt) return;
    startedAttempt.current = attempt; // guards against React StrictMode double-invoking effects
    setError(null);
    setElapsed(0);
    runAnalysis(request.type, request.payload)
      .then((scan) => { if (mounted.current) navigate(`/results/${scan.id}`, { replace: true }); })
      .catch((err) => { if (mounted.current) setError(err.userMessage || "Analysis failed. Please try again."); });
  }, [attempt, request, navigate]);

  useEffect(() => {
    if (!request || error) return undefined;
    const id = setInterval(() => setElapsed((s) => s + 1), 1000);
    return () => clearInterval(id);
  }, [request, error, attempt]);

  if (!request) {
    return (
      <>
        <PageHeader title="Analysis" />
        <Panel><EmptyState icon={AlertTriangle} title="Nothing to analyse" description="Start a new analysis from the Scanner page." action={<Button onClick={() => navigate("/scanner")}>Go to scanner</Button>} /></Panel>
      </>
    );
  }

  if (error) {
    return (
      <>
        <PageHeader title="Analysis failed" />
        <div className="max-w-2xl">
          <ErrorState title="Analysis failed" message={error} onRetry={() => setAttempt((a) => a + 1)} />
          <div className="mt-4"><Button variant="ghost" onClick={() => navigate("/scanner")}>Back to scanner</Button></div>
        </div>
      </>
    );
  }

  return (
    <>
      <PageHeader title="Analyzing" subtitle="Waiting for the detection backend" />
      <Panel className="max-w-2xl mx-auto p-8 lg:p-10 text-center">
        <div className="relative w-20 h-20 mx-auto mb-6 rounded-2xl flex items-center justify-center ss-sweep" style={{ background: T.redSoft, border: `1px solid ${T.redGlow}` }}>
          <ScanLine size={30} color={T.red} className="ss-pulse" aria-hidden="true" />
        </div>
        <h2 className="ss-display font-bold text-lg mb-1" style={{ color: T.text }}>Running analysis</h2>
        <p className="text-sm mb-6" style={{ color: T.textMuted }} role="status" aria-live="polite">
          Your {request.type === "qr" ? "QR image" : request.type} submission has been sent to the backend.
        </p>
        <div className="h-1.5 rounded-full overflow-hidden max-w-sm mx-auto mb-3" style={{ background: "rgba(255,255,255,0.06)" }} aria-hidden="true">
          <div className="h-full w-1/3 rounded-full ss-indeterminate" style={{ background: T.red, boxShadow: `0 0 10px ${T.redGlow}` }} />
        </div>
        <p className="ss-mono text-xs" style={{ color: T.textFaint }}>{elapsed}s elapsed</p>
        <p className="text-[11px] mt-6" style={{ color: T.textFaint }}>The animation is decorative. You will be taken to the result as soon as the backend responds.</p>
      </Panel>
    </>
  );
}