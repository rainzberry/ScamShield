import client from "./client";
import { apiError } from "../utils/errors";
import { normalizeStats } from "../utils/normalize";

export async function getDashboardStats() {
  const { data } = await client.get("/dashboard/stats");
  if (data?.success === false) throw apiError(data.error || "Could not load dashboard statistics.");
  return normalizeStats(data);
}

export async function getHealth() {
  const { data } = await client.get("/health");
  return data || {};
}