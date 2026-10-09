import { useCallback, useEffect, useState } from "react";
import { getHealth } from "../api/dashboardApi";

export default function useHealth(intervalMs = 60000) {
  const [state, setState] = useState({ status: "checking", data: null, error: null, checkedAt: null });

  const refresh = useCallback(async () => {
    try {
      const data = await getHealth();
      const degraded = data?.model_loaded === false;
      setState({ status: degraded ? "degraded" : "online", data, error: null, checkedAt: new Date() });
    } catch (err) {
      setState({ status: "offline", data: null, error: err.userMessage || "Backend unavailable.", checkedAt: new Date() });
    }
  }, []);

  useEffect(() => {
    refresh();
    if (!intervalMs) return undefined;
    const id = setInterval(refresh, intervalMs);
    return () => clearInterval(id);
  }, [refresh, intervalMs]);

  return { ...state, refresh };
}