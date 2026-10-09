import { Link } from "react-router-dom";
import { FileText, HelpCircle, History, ScanLine, ShieldAlert, ShieldCheck } from "lucide-react";
import { getClassStyle, SCAN_TYPE_LABELS, T } from "../../constants/theme";
import { formatDateTime } from "../../utils/format";
import ClassBadge from "../common/ClassBadge";
import Button from "../common/Button";
import Panel from "../common/Panel";
import { InlineAlert } from "../common/StateViews";
import RadialMeter from "../charts/RadialMeter";
import IndicatorList from "./IndicatorList";
import { FeatureList, KeyValueList } from "./FeatureList";

function Section({ title, children }) {
  return (
    <Panel className="p-5 lg:p-6">
      <h2 className="font-semibold text-sm mb-3" style={{ color: T.text }}>{title}</h2>
      {children}
    </Panel>
  );
}

function Meta({ label, value }) {
  return (
    <div className="min-w-0">
      <p className="text-[10px] tracking-wide" style={{ color: T.textFaint }}>{label}</p>
      <p className="text-xs font-medium mt-0.5 break-words" style={{ color: T.text }}>{value || "—"}</p>
    </div>
  );
}

export default function ResultView({ scan, isReport = false }) {
  const c = getClassStyle(scan.classification);
  const positive = scan.classification === "safe";
  const { explanation, input } = scan;
  const hasInput = input.sender || input.subject || input.url || input.content;

  return (
    <div className="max-w-4xl ss-fade-up flex flex-col gap-5">
      {/* Headline card */}
      <Panel className="p-6 lg:p-8" glow={c.glow}>
        <div className="flex flex-wrap items-start justify-between gap-4 mb-6">
          <div>
            <p className="text-xs mb-2" style={{ color: T.textFaint }}>CLASSIFICATION</p>
            <ClassBadge classification={scan.classification} />
          </div>
          {!isReport && scan.id && (
            <Link to={`/reports/${scan.id}`} className="no-print">
              <Button variant="outline" size="sm" icon={FileText}>View full report</Button>
            </Link>
          )}
        </div>

        <div className="grid sm:grid-cols-2 gap-6 py-6" style={{ borderTop: `1px solid ${T.border}`, borderBottom: `1px solid ${T.border}` }}>
          <RadialMeter value={scan.riskScore} label="RISK SCORE" sub={scan.severity ? `${scan.severity} SEVERITY` : "Severity not reported"} color={c.text} glow={c.glow} />
          <RadialMeter value={scan.confidence === null ? null : Math.round(scan.confidence)} label="CONFIDENCE" sub="Model certainty" unit="%" color={T.text} glow="rgba(255,255,255,0.15)" />
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6">
          <Meta label="SCAN TYPE" value={SCAN_TYPE_LABELS[scan.scanType] || scan.scanType} />
          <Meta label="SEVERITY" value={scan.severity} />
          <Meta label="MODEL VERSION" value={scan.modelVersion} />
          <Meta label="ANALYSED" value={formatDateTime(scan.createdAt)} />
        </div>

        <div className="flex items-start gap-2 text-[11px] leading-relaxed mt-6 rounded-lg px-3.5 py-3" style={{ background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}`, color: T.textMuted }}>
          <HelpCircle size={14} className="flex-shrink-0 mt-0.5" color={T.textFaint} aria-hidden="true" />
          <span><strong style={{ color: T.text }}>Risk</strong> is how dangerous the content is if acted on. <strong style={{ color: T.text }}>Confidence</strong> is how certain the model is about its classification. Read both. This is guidance, not a guarantee.</span>
        </div>
      </Panel>

      {/* Why flagged */}
      <Section title={positive ? "Why was this considered safe?" : "Why was this flagged?"}>
        {explanation.summary
          ? <p className="text-sm leading-relaxed" style={{ color: T.textMuted }}>{explanation.summary}</p>
          : <p className="text-sm" style={{ color: T.textMuted }}>No explanation summary was returned by the backend for this scan.</p>}
      </Section>

      <Section title={positive ? "What was checked" : "Threat indicators"}>
        <IndicatorList indicators={scan.indicators} positive={positive} />
      </Section>

      <Section title="Model evidence">
        <p className="text-xs mb-3" style={{ color: T.textFaint }}>Features that influenced the machine-learning prediction. Red pushes toward higher risk, green toward lower risk.</p>
        <FeatureList items={explanation.modelFeatures} emptyText="The backend did not return model feature evidence for this scan." />
      </Section>

      <Section title="Rule-based evidence">
        <FeatureList items={explanation.ruleFeatures} emptyText="The backend did not return rule-based evidence for this scan." />
      </Section>

      {explanation.urlFeatures && (
        <Section title="URL feature analysis">
          <KeyValueList data={explanation.urlFeatures} />
        </Section>
      )}

      {scan.scanType === "qr" && (scan.decodedPayload || scan.payloadType) && (
        <Section title="Decoded QR content">
          {scan.payloadType && <p className="text-xs mb-2" style={{ color: T.textMuted }}>Payload type: <span className="ss-mono" style={{ color: T.text }}>{scan.payloadType}</span></p>}
          {scan.decodedPayload && (
            <pre className="ss-mono text-xs p-3 rounded-lg whitespace-pre-wrap break-all" style={{ background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}`, color: T.textMuted }}>{String(scan.decodedPayload)}</pre>
          )}
          <InlineAlert tone="warning" className="mt-3">Shown as plain text only. ScamShield never opens or executes decoded QR content. Do not open it unless you trust the source.</InlineAlert>
        </Section>
      )}

      {/* Recommendation */}
      <div className="rounded-2xl p-5 flex items-start gap-3" style={{ background: c.soft, border: `1px solid ${c.ring}` }}>
        {positive ? <ShieldCheck size={20} color={c.text} className="flex-shrink-0" aria-hidden="true" /> : <ShieldAlert size={20} color={c.text} className="flex-shrink-0" aria-hidden="true" />}
        <div>
          <h2 className="text-xs font-semibold mb-0.5" style={{ color: c.text }}>RECOMMENDED ACTION</h2>
          <p className="text-sm" style={{ color: T.text }}>{scan.recommendation || "No recommendation was returned by the backend for this scan."}</p>
        </div>
      </div>

      {/* Submitted content (plain text only, nothing is opened or linked) */}
      {hasInput && (
        <details>
          <summary className="cursor-pointer text-xs font-semibold ss-focus rounded w-fit" style={{ color: T.textMuted }}>View submitted content</summary>
          <Panel className="p-4 mt-2 ss-mono text-xs leading-relaxed break-words" style={{ color: T.textMuted }}>
            {input.sender && <p className="mb-1"><span style={{ color: T.textFaint }}>From:</span> {input.sender}</p>}
            {input.subject && <p className="mb-1"><span style={{ color: T.textFaint }}>Subject:</span> {input.subject}</p>}
            {input.url && <p className="mb-1 break-all"><span style={{ color: T.textFaint }}>URL (not clickable):</span> {input.url}</p>}
            {input.content && <p className="whitespace-pre-wrap pt-2 mt-2" style={{ borderTop: `1px solid ${T.border}` }}>{input.content}</p>}
          </Panel>
        </details>
      )}

      {!isReport && (
        <div className="flex flex-wrap gap-3 no-print">
          <Link to="/scanner"><Button icon={ScanLine}>Scan something else</Button></Link>
          <Link to="/history"><Button variant="outline" icon={History}>Scan history</Button></Link>
        </div>
      )}
    </div>
  );
}