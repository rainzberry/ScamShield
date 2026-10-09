export const T = {
  void: "#0a0c10",
  base: "#0d1015",
  panelSolid: "#12151b",
  border: "rgba(255,255,255,0.08)",
  borderBright: "rgba(255,255,255,0.16)",
  text: "#e7e9ee",
  textMuted: "#8b93a3",
  textFaint: "#5b6373",
  red: "#ff3b52",
  redGlow: "rgba(255,59,82,0.45)",
  redSoft: "rgba(255,59,82,0.10)",
  amber: "#f5a524",
  amberGlow: "rgba(245,165,36,0.35)",
  amberSoft: "rgba(245,165,36,0.10)",
  green: "#36d399",
  greenGlow: "rgba(54,211,153,0.30)",
  greenSoft: "rgba(54,211,153,0.10)",
  malicious: "#ff1f3d",
  maliciousGlow: "rgba(255,31,61,0.6)",
};

export const CLASSIFICATIONS = ["safe", "spam", "phishing", "scam", "malicious"];
export const SCAN_TYPES = ["email", "text", "url", "qr"];
export const SCAN_TYPE_LABELS = { email: "Email", text: "Text", url: "URL", qr: "QR" };

export const CLASS_STYLES = {
  safe: { label: "Safe", text: T.green, soft: T.greenSoft, glow: T.greenGlow, ring: "rgba(54,211,153,0.35)" },
  spam: { label: "Spam", text: T.amber, soft: T.amberSoft, glow: T.amberGlow, ring: "rgba(245,165,36,0.4)" },
  phishing: { label: "Phishing", text: T.red, soft: T.redSoft, glow: T.redGlow, ring: "rgba(255,59,82,0.55)" },
  scam: { label: "Scam", text: "#ff6a3d", soft: "rgba(255,106,61,0.12)", glow: "rgba(255,106,61,0.45)", ring: "rgba(255,106,61,0.55)" },
  malicious: { label: "Malicious", text: T.malicious, soft: "rgba(255,31,61,0.13)", glow: T.maliciousGlow, ring: "rgba(255,31,61,0.7)" },
  unknown: { label: "Unknown", text: T.textMuted, soft: "rgba(255,255,255,0.05)", glow: "rgba(255,255,255,0.1)", ring: "rgba(255,255,255,0.2)" },
};

export function getClassStyle(classification) {
  return CLASS_STYLES[String(classification || "").toLowerCase()] || CLASS_STYLES.unknown;
}

export const SEVERITY_COLORS = {
  INFO: T.textMuted,
  LOW: T.green,
  MEDIUM: T.amber,
  HIGH: T.red,
  CRITICAL: T.malicious,
};

export function severityColor(severity) {
  return SEVERITY_COLORS[String(severity || "").toUpperCase()] || T.textMuted;
}