import client from "./client";
import { apiError } from "../utils/errors";
import { normalizeScan } from "../utils/normalize";

export async function getReport(scanId) {
  const { data } = await client.get(`/reports/${encodeURIComponent(scanId)}`);
  if (!data || data.success === false) throw apiError(data?.error || "Report not found.");
  return normalizeScan(data.report || data.scan || data);
}