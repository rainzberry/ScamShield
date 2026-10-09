import { CLASSIFICATIONS } from "../constants/theme";
import { truncate } from "./format";

const toNumber = (v) => {
  if (v === null || v === undefined || v === "") return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
};
const asArray = (v) => (Array.isArray(v) ? v : []);

/** Confidence may arrive as 0-1 or 0-100. Returns a 0-100 percentage (or null). */
function toPercent(v) {
  const n = toNumber(v);
  if (n === null) return null;
  return Math.round((n <= 1 ? n * 100 : n) * 10) / 10;
}

function normalizeIndicator(i) {
  if (typeof i === "string") return { code: i, label: i, severity: "INFO", evidence: "" };
  return {
    code: i?.code || i?.id || "",
    label: i?.label || i?.name || i?.code || "Indicator",
    severity: String(i?.severity || "INFO").toUpperCase(),
    evidence: i?.evidence || i?.description || "",
  };
}

/** Converts any backend scan object into one safe, predictable shape. Missing optional fields stay empty. */
export function normalizeScan(raw) {
  const r = raw || {};
  const input = r.input && typeof r.input === "object" ? r.input : {};
  const pick = (...keys) => {
    for (const k of keys) {
      if (r[k] !== undefined && r[k] !== null && r[k] !== "") return r[k];
      if (input[k] !== undefined && input[k] !== null && input[k] !== "") return input[k];
    }
    return "";
  };

  const exp = r.explanation;
  const explanation =
    typeof exp === "string"
      ? { summary: exp, modelFeatures: [], ruleFeatures: [], urlFeatures: null }
      : {
          summary: exp?.summary || "",
          modelFeatures: asArray(exp?.model_features),
          ruleFeatures: asArray(exp?.rule_features),
          urlFeatures: exp?.url_features ?? null,
        };

  const sender = pick("sender");
  const subject = pick("subject");
  const url = pick("url");
  const content = pick("body", "content", "text");
  const preview = pick("input_preview", "content_preview");
  const title = subject || url || truncate(content || preview, 80) || `${r.scan_type || "Content"} scan`;

  return {
    id: r.id ?? r.scan_id ?? null,
    scanType: String(r.scan_type || "").toLowerCase(),
    classification: String(r.classification || "").toLowerCase(),
    riskScore: toNumber(r.risk_score),
    confidence: toPercent(r.confidence),
    severity: r.severity ? String(r.severity).toUpperCase() : null,
    indicators: asArray(r.indicators).map(normalizeIndicator),
    explanation,
    recommendation: r.recommendation || "",
    createdAt: r.created_at || r.timestamp || null,
    modelVersion: r.model_version || "",
    title,
    input: { sender, subject, url, content, preview },
    decodedPayload: r.decoded_payload ?? r.qr_payload ?? input.decoded_payload ?? "",
    payloadType: r.payload_type ?? r.qr_payload_type ?? "",
    generatedAt: r.generated_at || null,
  };
}

export function normalizeScanList(raw) {
  const items = asArray(raw?.scans || raw?.items || raw?.results);
  const p = raw?.pagination || raw || {};
  const total = toNumber(p.total ?? p.total_items) ?? items.length;
  const perPage = (toNumber(p.per_page ?? p.page_size) ?? items.length) || 10;
  const page = toNumber(p.page) ?? 1;
  const pages = toNumber(p.pages ?? p.total_pages) ?? Math.max(1, Math.ceil(total / perPage));
  return { scans: items.map(normalizeScan), total, page, pages, perPage };
}

const SEVERITY_ORDER = ["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"];

export function normalizeStats(raw) {
  const s = raw?.stats || raw || {};
  const by = s.by_classification || s.classification_counts || s.classifications || {};
  const counts = {};
  CLASSIFICATIONS.forEach((k) => {
    counts[k] = toNumber(by[k] ?? s[`${k}_count`] ?? s[k]) ?? 0;
  });
  const total = toNumber(s.total_scans ?? s.total) ?? Object.values(counts).reduce((a, b) => a + b, 0);

  const sev = s.severity_distribution || s.by_severity || null;
  const severity = sev
    ? Object.entries(sev)
        .map(([k, v]) => ({ key: k.toUpperCase(), value: toNumber(v) || 0 }))
        .sort((a, b) => SEVERITY_ORDER.indexOf(a.key) - SEVERITY_ORDER.indexOf(b.key))
    : [];

  const activityRaw = s.activity || s.scans_over_time;
  const activity = Array.isArray(activityRaw)
    ? activityRaw.map((a) => ({
        date: a.date || a.day || "",
        scans: toNumber(a.scans ?? a.count) ?? 0,
        threats: toNumber(a.threats) ?? 0,
      }))
    : [];

  return {
    total,
    counts,
    averageRisk: toNumber(s.average_risk ?? s.avg_risk_score ?? s.average_risk_score),
    severity,
    activity,
    recent: asArray(s.recent_scans).map(normalizeScan),
  };
}