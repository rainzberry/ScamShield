import client from "./client";
import { apiError } from "../utils/errors";
import { normalizeScan, normalizeScanList } from "../utils/normalize";

// Multipart field name the Flask QR endpoint reads: request.files["file"]
export const QR_FIELD_NAME = "file";

function extractScan(data) {
  if (!data || data.success === false) {
    throw apiError(data?.error || data?.message || "Analysis failed.");
  }
  const scan = normalizeScan(data.scan || data);
  if (!scan.id) throw apiError("The backend returned an unexpected response (missing scan id).");
  return scan;
}

export async function analyzeEmail(payload) {
  const { data } = await client.post("/analyze/email", payload);
  return extractScan(data);
}

export async function analyzeText(payload) {
  const { data } = await client.post("/analyze/text", payload);
  return extractScan(data);
}

export async function analyzeUrl(payload) {
  const { data } = await client.post("/analyze/url", payload);
  return extractScan(data);
}

export async function analyzeQr({ file }) {
  const form = new FormData();
  form.append(QR_FIELD_NAME, file);
  const { data } = await client.post("/analyze/qr", form);
  return extractScan(data);
}

/** Dispatches to the right endpoint. type is one of: email | text | url | qr */
export function runAnalysis(type, payload) {
  switch (type) {
    case "email": return analyzeEmail(payload);
    case "text": return analyzeText(payload);
    case "url": return analyzeUrl(payload);
    case "qr": return analyzeQr(payload);
    default: return Promise.reject(apiError("Unknown scan type."));
  }
}

export async function listScans(params = {}) {
  const { data } = await client.get("/scans", { params });
  if (data?.success === false) throw apiError(data.error || "Could not load scans.");
  return normalizeScanList(data);
}

export async function getScan(id) {
  const { data } = await client.get(`/scans/${encodeURIComponent(id)}`);
  if (!data || data.success === false) throw apiError(data?.error || "Scan not found.");
  return normalizeScan(data.scan || data);
}