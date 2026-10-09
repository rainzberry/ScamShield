import { useEffect, useState } from "react";

/**
 * Runs an async fetcher and exposes { data, loading, error, reload }.
 * Re-runs when any value in `deps` changes (the fetcher itself is intentionally not a dependency).
 */
export default function useFetch(fetcher, deps = []) {
  const [state, setState] = useState({ data: null, loading: true, error: null });
  const [tick, setTick] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setState((s) => ({ ...s, loading: true, error: null }));
    fetcher()
      .then((data) => { if (!cancelled) setState({ data, loading: false, error: null }); })
      .catch((err) => {
        if (!cancelled) setState({ data: null, loading: false, error: err.userMessage || err.message || "Request failed." });
      });
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, tick]);

  return { ...state, reload: () => setTick((t) => t + 1) };
}