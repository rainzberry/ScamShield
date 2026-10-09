import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Inbox, ScanLine } from "lucide-react";
import { listInbox } from "../api/gmailApi";
import { T } from "../constants/theme";
import useLocalStorage from "../hooks/useLocalStorage";
import Button from "../components/common/Button";
import PageHeader from "../components/common/PageHeader";
import Panel from "../components/common/Panel";
import { ErrorState, InlineAlert, LoadingState } from "../components/common/StateViews";

export const GMAIL_DEMO_KEY = "scamshield_gmail_demo_connected";

export default function Gmail() {
  const navigate = useNavigate();
  const [connected, setConnected] = useLocalStorage(GMAIL_DEMO_KEY, false);
  const [messages, setMessages] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadInbox() {
    setLoading(true);
    setError("");
    try {
      const res = await listInbox();
      setMessages(res.messages);
      setConnected(true);
    } catch (err) {
      setError(err.userMessage || err.message || "Could not load the inbox.");
    } finally {
      setLoading(false);
    }
  }

  function disconnect() {
    setConnected(false);
    setMessages(null);
  }

  // Sends the sample message text to the REAL backend. The result is genuine, the inbox is not.
  function analyze(m) {
    navigate("/analysis", { state: { request: { type: "email", payload: { sender: m.from, subject: m.subject, body: m.body, ...(m.url ? { url: m.url } : {}) } } } });
  }

  // Restore the demo list if the user was already "connected" in a previous visit
  if (connected && !messages && !loading && !error) loadInbox();

  return (
    <>
      <PageHeader title="Gmail" subtitle="Scan messages from an inbox" />

      <InlineAlert tone="warning" className="mb-5">
        <strong>Demo Gmail Mode</strong> — Demo Mode — sample messages only. No real Google account is accessed.
      </InlineAlert>

      {loading && <LoadingState label="Loading demo inbox..." />}
      {error && <ErrorState title="Inbox unavailable" message={error} onRetry={loadInbox} />}

      {!connected && !loading && !error && (
        <Panel className="p-8 lg:p-10 max-w-xl">
          <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-5" style={{ background: T.redSoft, border: `1px solid ${T.redGlow}` }}>
            <Inbox size={22} color={T.red} aria-hidden="true" />
          </div>
          <h2 className="ss-display font-bold text-lg mb-2" style={{ color: T.text }}>Demo inbox</h2>
          <p className="text-sm leading-relaxed mb-6" style={{ color: T.textMuted }}>
            Real Gmail OAuth is not available yet. You can load a set of built-in sample messages and send any of them to the real detection backend to see how analysis works.
          </p>
          <Button icon={Inbox} onClick={loadInbox}>Load demo inbox</Button>
        </Panel>
      )}

      {messages && !loading && (
        <Panel className="overflow-hidden">
          <div className="px-5 py-4 flex items-center justify-between" style={{ borderBottom: `1px solid ${T.border}` }}>
            <h2 className="font-semibold text-sm" style={{ color: T.text }}>Sample messages (demo)</h2>
            <button onClick={disconnect} className="text-xs font-semibold ss-focus rounded" style={{ color: T.textMuted }}>Reset demo</button>
          </div>
          <ul>
            {messages.map((m) => (
              <li key={m.id} className="px-5 py-4 flex items-center gap-4" style={{ borderTop: `1px solid ${T.border}` }}>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium truncate" style={{ color: T.text }}>{m.from}</p>
                  <p className="text-sm truncate" style={{ color: T.textMuted }}>{m.subject}</p>
                  <p className="text-xs truncate mt-0.5" style={{ color: T.textFaint }}>{m.snippet}</p>
                </div>
                <Button size="sm" icon={ScanLine} onClick={() => analyze(m)} aria-label={`Analyze message: ${m.subject}`}>Analyze</Button>
              </li>
            ))}
          </ul>
        </Panel>
      )}
    </>
  );
}