import React, { useState, useEffect, useMemo, useRef, createContext, useContext } from "react";
import {
  Home, Mail, History as HistoryIcon, Info, Settings as SettingsIcon, User, LogOut,
  Shield, ShieldAlert, ShieldCheck, TriangleAlert, MailWarning, Search, ChevronDown,
  ChevronRight, X, Menu, ArrowRight, CheckCircle2, Circle, Loader2, ExternalLink, Lock,
  Eye, EyeOff, RefreshCw, Download, HelpCircle, ChevronUp, Sparkles, ScanLine, Inbox,
  FileText, ArrowLeft, AlertTriangle, Link2, Clock, Filter, ArrowUpDown, CircleCheck,
  ShieldX, Fingerprint, Gauge, BadgeCheck, Trash2, BellRing,
} from "lucide-react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from "recharts";

/* ============================================================================
   DESIGN TOKENS
   Deep charcoal SOC-dashboard theme. Colors applied via inline style / plain
   CSS (not Tailwind arbitrary values) since only core utility classes compile.
============================================================================ */
const T = {
  void: "#0a0c10",
  base: "#0d1015",
  panel: "rgba(21,25,32,0.72)",
  panelSolid: "#12151b",
  border: "rgba(255,255,255,0.08)",
  borderBright: "rgba(255,255,255,0.16)",
  text: "#e7e9ee",
  textMuted: "#8b93a3",
  textFaint: "#5b6373",
  red: "#ff3b52",
  redDim: "#ff3b52",
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

const SEV = {
  safe: { label: "Safe", text: T.green, soft: T.greenSoft, glow: T.greenGlow, ring: "rgba(54,211,153,0.35)" },
  spam: { label: "Spam", text: T.amber, soft: T.amberSoft, glow: T.amberGlow, ring: "rgba(245,165,36,0.4)" },
  phishing: { label: "Phishing", text: T.red, soft: T.redSoft, glow: T.redGlow, ring: "rgba(255,59,82,0.55)" },
  malicious: { label: "Malicious", text: T.malicious, soft: "rgba(255,31,61,0.13)", glow: T.maliciousGlow, ring: "rgba(255,31,61,0.7)" },
};

const SEVERITY_WEIGHT = { low: 1, medium: 2, high: 3, critical: 4 };

/* ============================================================================
   GLOBAL STYLE — fonts, keyframes, small utility classes
============================================================================ */
function GlobalStyle() {
  return (
    <style>{`
      @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');
      .ss-root { font-family: 'Inter', ui-sans-serif, system-ui, sans-serif; background: ${T.base}; color: ${T.text}; }
      .ss-display { font-family: 'Space Grotesk', 'Inter', sans-serif; letter-spacing: -0.01em; }
      .ss-mono { font-family: 'JetBrains Mono', ui-monospace, monospace; }
      .ss-bg {
        background:
          radial-gradient(ellipse 900px 500px at 12% -10%, rgba(255,59,82,0.10), transparent 60%),
          radial-gradient(ellipse 700px 500px at 100% 0%, rgba(255,59,82,0.06), transparent 55%),
          linear-gradient(180deg, ${T.void} 0%, ${T.base} 100%);
        background-attachment: fixed;
      }
      .ss-grid {
        background-image: linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px);
        background-size: 42px 42px;
      }
      .ss-panel {
        background: ${T.panel};
        border: 1px solid ${T.border};
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
      }
      .ss-panel:hover { border-color: ${T.borderBright}; }
      .ss-scroll::-webkit-scrollbar { width: 8px; height: 8px; }
      .ss-scroll::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.12); border-radius: 8px; }
      .ss-scroll::-webkit-scrollbar-track { background: transparent; }
      @keyframes pulseGlow {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.55; }
      }
      .ss-pulse { animation: pulseGlow 2.2s ease-in-out infinite; }
      @keyframes scanSweep {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
      }
      .ss-sweep::after {
        content: '';
        position: absolute; inset: 0;
        background: linear-gradient(90deg, transparent, rgba(255,59,82,0.18), transparent);
        animation: scanSweep 1.6s linear infinite;
      }
      @keyframes fadeUp { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
      .ss-fade-up { animation: fadeUp 0.35s ease both; }
      @keyframes ringIn { from { stroke-dashoffset: 283; } }
      .ss-ring { animation: ringIn 1s cubic-bezier(.22,.9,.3,1) both; }
      .ss-focus:focus-visible { outline: 2px solid ${T.red}; outline-offset: 2px; border-radius: 8px; }
      a, button { -webkit-tap-highlight-color: transparent; }
      @media (prefers-reduced-motion: reduce) {
        .ss-pulse, .ss-sweep::after, .ss-fade-up, .ss-ring { animation: none !important; }
      }
    `}</style>
  );
}

/* ============================================================================
   MOCK DATA LAYER
   This mirrors the shape a real /api/scans response will use. Every screen
   (dashboard stats, charts, history, reports) derives from this ONE array so
   numbers never contradict each other across the app.
============================================================================ */
const INDICATOR_LIB = {
  suspiciousSender: { label: "Suspicious Sender", description: "The sender's domain does not match the organization it claims to represent." },
  urgentLanguage: { label: "Urgent Language", description: "The message uses pressure tactics and tight deadlines to provoke a hasty response." },
  suspiciousUrl: { label: "Suspicious URL", description: "The included link uses a domain designed to closely resemble a trusted service." },
  credentialRequest: { label: "Credential Request", description: "The message asks you to enter a password or other personal credentials." },
  spoofedDisplayName: { label: "Spoofed Display Name", description: "The sender's display name does not match their actual email address." },
  genericGreeting: { label: "Generic Greeting", description: "The message uses a generic greeting instead of your name, common in mass campaigns." },
  suspiciousAttachment: { label: "Suspicious Attachment", description: "The message includes an attachment type often used to deliver malware." },
  unsolicitedOffer: { label: "Unsolicited Offer", description: "The message offers a prize, refund, or deal that was never requested." },
  verifiedSender: { label: "Verified Sender", description: "The sender domain matches known, verified organizational records." },
  noSuspiciousLinks: { label: "No Suspicious Links", description: "No links in this message point to known malicious or deceptive domains." },
  consistentHistory: { label: "Consistent Sender History", description: "This sender matches the pattern of previous legitimate messages from this address." },
};

function daysAgo(n) {
  const d = new Date();
  d.setDate(d.getDate() - n);
  d.setHours(9 + (n % 6), (n * 7) % 60, 0, 0);
  return d.toISOString();
}

const RAW_SCANS = [
  {
    id: "scan-1001", date: daysAgo(0), source: "manual",
    sender: "security@paypa1-support.com", subject: "URGENT: Your account requires immediate verification",
    body: "Your account will be permanently suspended unless you verify your information immediately. Click the link below to confirm your identity.",
    url: "https://paypa1-support.example.com/verify",
    classification: "phishing", risk: 94, confidence: 97, severity: "high",
    indicators: [
      { id: "suspiciousSender", severity: "high" },
      { id: "urgentLanguage", severity: "high" },
      { id: "suspiciousUrl", severity: "critical" },
      { id: "credentialRequest", severity: "high" },
    ],
    explanation: "The message contains characteristics commonly associated with phishing attempts. The sender domain appears suspicious, the content creates urgency, and the included URL may imitate a legitimate service.",
    recommendedAction: "Do not click the link or provide credentials. Report this message and delete it.",
  },
  {
    id: "scan-1002", date: daysAgo(1), source: "gmail",
    sender: "billing@invoice-secure-payments.net", subject: "Invoice_2024_Overdue_Notice.exe attached",
    body: "Your account has an overdue balance. Open the attached invoice immediately to avoid service interruption and legal action.",
    url: "https://invoice-secure-payments.net/download",
    classification: "malicious", risk: 98, confidence: 99, severity: "critical",
    indicators: [
      { id: "suspiciousAttachment", severity: "critical" },
      { id: "spoofedDisplayName", severity: "high" },
      { id: "suspiciousUrl", severity: "critical" },
      { id: "urgentLanguage", severity: "medium" },
    ],
    explanation: "This message attempts to deliver an executable file disguised as an invoice. The sender identity is spoofed and the urgency framing is designed to bypass careful review before opening the attachment.",
    recommendedAction: "Do not open the attachment. Delete this message and report it to your IT or security team.",
  },
  {
    id: "scan-1003", date: daysAgo(1), source: "manual",
    sender: "deals@mega-savings-now.biz", subject: "You have WON a $500 gift card!!!",
    body: "Congratulations! You've been randomly selected to receive a $500 gift card. Claim your prize before it expires.",
    url: "https://mega-savings-now.biz/claim",
    classification: "spam", risk: 58, confidence: 88, severity: "medium",
    indicators: [
      { id: "unsolicitedOffer", severity: "medium" },
      { id: "genericGreeting", severity: "low" },
      { id: "spoofedDisplayName", severity: "low" },
    ],
    explanation: "This message matches common bulk-marketing and prize-scam patterns. It was not personally addressed and offers an unsolicited reward, typical of spam campaigns rather than a targeted attack.",
    recommendedAction: "No urgent action needed. Mark as spam and avoid clicking the claim link.",
  },
  {
    id: "scan-1004", date: daysAgo(2), source: "gmail",
    sender: "noreply@github.com", subject: "Your weekly digest is ready",
    body: "Here's a summary of activity across your repositories this week.",
    url: "",
    classification: "safe", risk: 3, confidence: 96, severity: "low",
    indicators: [
      { id: "verifiedSender", severity: "info" },
      { id: "noSuspiciousLinks", severity: "info" },
      { id: "consistentHistory", severity: "info" },
    ],
    explanation: "This message originates from a verified sender domain with a consistent history and contains no suspicious links, attachments, or urgency indicators.",
    recommendedAction: "No action needed. This message appears safe.",
  },
  {
    id: "scan-1005", date: daysAgo(3), source: "manual",
    sender: "hr@company-internal-portal.com", subject: "Update your payroll direct deposit details",
    body: "Our payroll system has been updated. Please confirm your direct deposit details within 24 hours to avoid a delay in payment.",
    url: "https://company-internal-portal.com/payroll-update",
    classification: "phishing", risk: 89, confidence: 93, severity: "high",
    indicators: [
      { id: "suspiciousSender", severity: "high" },
      { id: "urgentLanguage", severity: "medium" },
      { id: "credentialRequest", severity: "high" },
      { id: "suspiciousUrl", severity: "high" },
    ],
    explanation: "This message impersonates an internal HR request but originates from an external domain not associated with the organization, and asks for sensitive financial credentials under time pressure.",
    recommendedAction: "Do not enter any information. Verify the request directly with HR through a known internal channel.",
  },
  {
    id: "scan-1006", date: daysAgo(4), source: "gmail",
    sender: "notifications@slack.com", subject: "New message in #engineering",
    body: "You have unread messages in your workspace.",
    url: "",
    classification: "safe", risk: 2, confidence: 98, severity: "low",
    indicators: [{ id: "verifiedSender", severity: "info" }, { id: "consistentHistory", severity: "info" }],
    explanation: "Sent from a verified, previously trusted sender with no unusual content or links.",
    recommendedAction: "No action needed.",
  },
  {
    id: "scan-1007", date: daysAgo(5), source: "manual",
    sender: "support@apple-icloud-verify.com", subject: "Your Apple ID has been locked",
    body: "We detected unusual activity on your Apple ID. Your account has been locked for your protection. Verify your identity to restore access.",
    url: "https://apple-icloud-verify.com/restore",
    classification: "phishing", risk: 91, confidence: 95, severity: "high",
    indicators: [
      { id: "suspiciousSender", severity: "high" },
      { id: "urgentLanguage", severity: "high" },
      { id: "credentialRequest", severity: "high" },
      { id: "suspiciousUrl", severity: "critical" },
    ],
    explanation: "This message impersonates Apple support using a lookalike domain and pressures the recipient into entering account credentials on a page that does not belong to Apple.",
    recommendedAction: "Do not click the link or enter your Apple ID credentials. Verify account status directly at apple.com.",
  },
  {
    id: "scan-1008", date: daysAgo(6), source: "manual",
    sender: "newsletter@dailydeals-club.info", subject: "Flash Sale: 80% off everything today only",
    body: "Everything must go! Today only, get 80% off site-wide. Limited stock available.",
    url: "https://dailydeals-club.info",
    classification: "spam", risk: 45, confidence: 82, severity: "medium",
    indicators: [{ id: "unsolicitedOffer", severity: "medium" }, { id: "genericGreeting", severity: "low" }],
    explanation: "This message matches typical bulk promotional patterns with high-pressure discount framing and no personalization.",
    recommendedAction: "No urgent action needed. Unsubscribe or mark as spam if unwanted.",
  },
  {
    id: "scan-1009", date: daysAgo(7), source: "gmail",
    sender: "team@figma.com", subject: "Sarah commented on your design file",
    body: "Sarah left a comment on 'ScamShield Dashboard v2'.",
    url: "https://figma.com/file/abc123",
    classification: "safe", risk: 5, confidence: 97, severity: "low",
    indicators: [{ id: "verifiedSender", severity: "info" }, { id: "noSuspiciousLinks", severity: "info" }],
    explanation: "Sent from a verified collaboration platform domain with a link pointing to the platform's own verified URL structure.",
    recommendedAction: "No action needed.",
  },
  {
    id: "scan-1010", date: daysAgo(8), source: "manual",
    sender: "admin@wire-transfer-dept.co", subject: "RE: Wire transfer confirmation needed - URGENT",
    body: "Please confirm the attached wire transfer details before end of day to avoid processing delays.",
    url: "https://wire-transfer-dept.co/confirm",
    classification: "malicious", risk: 96, confidence: 98, severity: "critical",
    indicators: [
      { id: "suspiciousSender", severity: "high" },
      { id: "urgentLanguage", severity: "high" },
      { id: "suspiciousUrl", severity: "critical" },
      { id: "spoofedDisplayName", severity: "high" },
    ],
    explanation: "This message follows a business-email-compromise pattern, spoofing a finance-department identity and pressuring urgent action on a wire transfer through an unverified external link.",
    recommendedAction: "Do not act on this request. Verify directly with your finance team through a known phone line before any transfer.",
  },
  {
    id: "scan-1011", date: daysAgo(10), source: "manual",
    sender: "no-reply@dropbox.com", subject: "A file was shared with you",
    body: "A team member shared 'Q3_Report.pdf' with you.",
    url: "https://dropbox.com/s/abc123",
    classification: "safe", risk: 4, confidence: 95, severity: "low",
    indicators: [{ id: "verifiedSender", severity: "info" }, { id: "noSuspiciousLinks", severity: "info" }],
    explanation: "Verified sender domain and standard file-share link structure with no anomalies detected.",
    recommendedAction: "No action needed.",
  },
  {
    id: "scan-1012", date: daysAgo(12), source: "gmail",
    sender: "rewards@survey-cash-back.net", subject: "Complete this 2-minute survey and earn $50",
    body: "Share your feedback and receive a $50 reward instantly after completion.",
    url: "https://survey-cash-back.net/start",
    classification: "spam", risk: 52, confidence: 85, severity: "medium",
    indicators: [{ id: "unsolicitedOffer", severity: "medium" }, { id: "genericGreeting", severity: "low" }],
    explanation: "This message follows a common survey-reward spam pattern used to harvest personal information or drive ad traffic.",
    recommendedAction: "No urgent action needed. Avoid entering personal details and mark as spam.",
  },
  {
    id: "scan-1013", date: daysAgo(15), source: "manual",
    sender: "it-helpdesk@company-support-team.com", subject: "Mailbox storage full - action required",
    body: "Your mailbox has exceeded its storage limit. Click below to increase your quota before messages start bouncing.",
    url: "https://company-support-team.com/upgrade",
    classification: "phishing", risk: 87, confidence: 92, severity: "high",
    indicators: [
      { id: "suspiciousSender", severity: "high" },
      { id: "urgentLanguage", severity: "medium" },
      { id: "credentialRequest", severity: "high" },
      { id: "suspiciousUrl", severity: "high" },
    ],
    explanation: "This message impersonates an internal IT helpdesk from an external lookalike domain and leads to a credential-harvesting page disguised as a mailbox upgrade tool.",
    recommendedAction: "Do not click the link. Report to your real IT department and delete this message.",
  },
  {
    id: "scan-1014", date: daysAgo(18), source: "manual",
    sender: "calendar-notification@google.com", subject: "Reminder: Team sync in 15 minutes",
    body: "This is a reminder for your upcoming meeting 'Weekly Team Sync'.",
    url: "",
    classification: "safe", risk: 1, confidence: 99, severity: "low",
    indicators: [{ id: "verifiedSender", severity: "info" }, { id: "consistentHistory", severity: "info" }],
    explanation: "Automated calendar notification from a verified platform domain with no external links or requests.",
    recommendedAction: "No action needed.",
  },
  {
    id: "scan-1015", date: daysAgo(21), source: "gmail",
    sender: "prizes@lucky-draw-winners.com", subject: "FINAL NOTICE: Claim your lottery winnings",
    body: "This is your final notice. Failure to respond within 24 hours will forfeit your winnings of $1,000,000.",
    url: "https://lucky-draw-winners.com/claim-now",
    classification: "phishing", risk: 90, confidence: 94, severity: "high",
    indicators: [
      { id: "suspiciousSender", severity: "high" },
      { id: "urgentLanguage", severity: "high" },
      { id: "credentialRequest", severity: "medium" },
      { id: "suspiciousUrl", severity: "high" },
    ],
    explanation: "This message uses a high-value prize lure combined with an artificial deadline to pressure the recipient into submitting personal and financial details.",
    recommendedAction: "Do not respond or click any links. Delete and report this message.",
  },
  {
    id: "scan-1016", date: daysAgo(25), source: "manual",
    sender: "updates@linkedin.com", subject: "You have 3 new profile views",
    body: "See who's been viewing your profile this week.",
    url: "https://linkedin.com/notifications",
    classification: "safe", risk: 6, confidence: 94, severity: "low",
    indicators: [{ id: "verifiedSender", severity: "info" }, { id: "noSuspiciousLinks", severity: "info" }],
    explanation: "Standard platform notification from a verified sender with no anomalous indicators.",
    recommendedAction: "No action needed.",
  },
  {
    id: "scan-1017", date: daysAgo(28), source: "manual",
    sender: "promo@electronics-clearance-outlet.top", subject: "Warehouse clearance: laptops from $99",
    body: "Massive warehouse clearance event. Laptops, phones and more starting at unbelievable prices. While stocks last.",
    url: "https://electronics-clearance-outlet.top",
    classification: "spam", risk: 40, confidence: 80, severity: "medium",
    indicators: [{ id: "unsolicitedOffer", severity: "medium" }],
    explanation: "This message matches typical too-good-to-be-true promotional spam patterns from an unfamiliar retail domain.",
    recommendedAction: "No urgent action needed. Avoid purchasing and mark as spam.",
  },
];

function enrichScan(s) {
  const isPositive = s.classification === "safe";
  return {
    ...s,
    indicators: s.indicators.map((i) => ({
      ...i,
      label: INDICATOR_LIB[i.id]?.label ?? i.id,
      description: INDICATOR_LIB[i.id]?.description ?? "",
      positive: isPositive,
    })),
  };
}

const SCANS_SEED = RAW_SCANS.map(enrichScan).sort((a, b) => new Date(b.date) - new Date(a.date));

const GMAIL_INBOX = [
  { id: "gm-1", from: "security@paypa1-support.com", subject: "URGENT: Your account requires immediate verification", snippet: "Your account will be permanently suspended unless you verify...", receivedAt: daysAgo(0), analyzed: true, linkedScanId: "scan-1001" },
  { id: "gm-2", from: "no-reply@amazon.com", subject: "Your order has shipped", snippet: "Track your package — arriving tomorrow between 9am and 1pm.", receivedAt: daysAgo(0), analyzed: false },
  { id: "gm-3", from: "billing@invoice-secure-payments.net", subject: "Invoice_2024_Overdue_Notice.exe attached", snippet: "Your account has an overdue balance. Open the attached invoice...", receivedAt: daysAgo(1), analyzed: true, linkedScanId: "scan-1002" },
  { id: "gm-4", from: "team@notion.so", subject: "Weekly workspace summary", snippet: "Here's what changed in your workspace this week.", receivedAt: daysAgo(1), analyzed: false },
  { id: "gm-5", from: "support@apple-icloud-verify.com", subject: "Your Apple ID has been locked", snippet: "We detected unusual activity on your Apple ID...", receivedAt: daysAgo(2), analyzed: true, linkedScanId: "scan-1007" },
  { id: "gm-6", from: "prizes@lucky-draw-winners.com", subject: "FINAL NOTICE: Claim your lottery winnings", snippet: "This is your final notice. Failure to respond within 24 hours...", receivedAt: daysAgo(2), analyzed: false },
  { id: "gm-7", from: "calendar-notification@google.com", subject: "Reminder: 1:1 with manager in 30 minutes", snippet: "This is a reminder for your upcoming meeting.", receivedAt: daysAgo(3), analyzed: false },
  { id: "gm-8", from: "rewards@survey-cash-back.net", subject: "Complete this 2-minute survey and earn $50", snippet: "Share your feedback and receive a $50 reward instantly...", receivedAt: daysAgo(4), analyzed: false },
];

const ANALYSIS_STEPS = [
  "Extracting email content",
  "Analyzing sender reputation",
  "Checking embedded URLs",
  "Evaluating threat indicators",
  "Calculating risk score",
  "Generating result",
];

const FAQ_ITEMS = [
  { q: "What is phishing?", a: "Phishing is a deceptive attempt to trick you into revealing sensitive information, such as passwords or financial details, usually by impersonating a trusted organization." },
  { q: "What is spam?", a: "Spam is unsolicited bulk messaging, typically promotional. It's a nuisance but usually not designed to steal your information directly." },
  { q: "What is the difference between spam and phishing?", a: "Spam is unwanted but generally low-risk marketing content. Phishing is a targeted attempt to steal credentials or sensitive data by impersonating a trusted source." },
  { q: "What does the risk score mean?", a: "The risk score (0–100) reflects how dangerous a message is estimated to be based on combined threat indicators. A higher score means greater potential harm if you act on the message." },
  { q: "What does confidence mean?", a: "Confidence reflects how certain the detection engine is about its classification, based on how strongly the evidence matches known patterns. Risk and confidence are separate: a message can have high risk and high confidence, or high risk with only moderate confidence." },
  { q: "Can ScamShield guarantee that an email is safe?", a: "No automated system can guarantee complete safety. ScamShield highlights known threat patterns to help you make an informed decision, but always use your own judgment for sensitive actions." },
  { q: "Can ScamShield analyze Gmail messages?", a: "Yes, once connected. In this prototype, Gmail connection uses clearly labeled demo data — no real Google account is accessed." },
  { q: "How should I respond to a high-risk result?", a: "Avoid clicking links, downloading attachments, or entering credentials. Report the message and delete it. When in doubt, verify directly with the organization through a known, trusted channel." },
];

/* ============================================================================
   APP CONTEXT
============================================================================ */
const AppCtx = createContext(null);
const useApp = () => useContext(AppCtx);

/* ============================================================================
   SMALL SHARED PRIMITIVES
============================================================================ */
function Btn({ children, variant = "primary", size = "md", icon: Icon, className = "", ...props }) {
  const sizes = { sm: "text-xs px-3 py-1.5 gap-1.5", md: "text-sm px-4 py-2.5 gap-2", lg: "text-sm px-6 py-3.5 gap-2" };
  const base = "inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 ss-focus disabled:opacity-50 disabled:cursor-not-allowed";
  const style =
    variant === "primary"
      ? { background: T.red, color: "#fff", boxShadow: `0 0 0 1px rgba(255,59,82,0.4), 0 4px 20px -4px ${T.redGlow}` }
      : variant === "outline"
      ? { background: "transparent", color: T.text, border: `1px solid ${T.borderBright}` }
      : variant === "ghost"
      ? { background: "transparent", color: T.textMuted }
      : { background: T.panelSolid, color: T.text, border: `1px solid ${T.border}` };
  return (
    <button
      className={`${base} ${sizes[size]} ${className} hover:-translate-y-0.5`}
      style={style}
      onMouseEnter={(e) => { if (variant === "primary") e.currentTarget.style.boxShadow = `0 0 0 1px rgba(255,59,82,0.6), 0 6px 26px -2px ${T.redGlow}`; }}
      onMouseLeave={(e) => { if (variant === "primary") e.currentTarget.style.boxShadow = `0 0 0 1px rgba(255,59,82,0.4), 0 4px 20px -4px ${T.redGlow}`; }}
      {...props}
    >
      {Icon && <Icon size={16} strokeWidth={2} />}
      {children}
    </button>
  );
}

function ClassIcon({ classification, size = 16 }) {
  const map = { safe: ShieldCheck, spam: MailWarning, phishing: ShieldAlert, malicious: ShieldX };
  const Ic = map[classification] || Shield;
  return <Ic size={size} strokeWidth={2} color={SEV[classification]?.text} />;
}

function SeverityTag({ classification, size = "md" }) {
  const c = SEV[classification];
  const pad = size === "sm" ? "px-2 py-0.5 text-[11px]" : "px-2.5 py-1 text-xs";
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-semibold ${pad}`}
      style={{ background: c.soft, color: c.text, border: `1px solid ${c.ring}` }}
    >
      <ClassIcon classification={classification} size={size === "sm" ? 12 : 13} />
      {c.label.toUpperCase()}
    </span>
  );
}

function Panel({ children, className = "", glow, style = {}, ...props }) {
  return (
    <div
      className={`ss-panel rounded-2xl ${className}`}
      style={{ ...(glow ? { boxShadow: `0 0 0 1px ${glow}, 0 8px 32px -8px ${glow}` } : {}), ...style }}
      {...props}
    >
      {children}
    </div>
  );
}

function EmptyState({ icon: Icon = Inbox, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-16 px-6">
      <div className="rounded-2xl p-4 mb-4" style={{ background: T.panelSolid, border: `1px solid ${T.border}` }}>
        <Icon size={28} color={T.textFaint} />
      </div>
      <p className="ss-display font-semibold text-base mb-1" style={{ color: T.text }}>{title}</p>
      <p className="text-sm max-w-sm mb-5" style={{ color: T.textMuted }}>{description}</p>
      {action}
    </div>
  );
}

function Field({ label, children, hint, error }) {
  return (
    <label className="block">
      <span className="block text-xs font-medium mb-1.5" style={{ color: T.textMuted }}>{label}</span>
      {children}
      {hint && !error && <span className="block text-[11px] mt-1" style={{ color: T.textFaint }}>{hint}</span>}
      {error && <span className="block text-[11px] mt-1" style={{ color: T.red }}>{error}</span>}
    </label>
  );
}

const inputStyle = {
  background: "rgba(255,255,255,0.03)",
  border: `1px solid ${T.border}`,
  color: T.text,
};
function inputClass(extra = "") {
  return `w-full rounded-lg px-3.5 py-2.5 text-sm placeholder:text-[#5b6373] transition-colors duration-200 ss-focus ${extra}`;
}

/* ============================================================================
   RISK / CONFIDENCE METERS  — signature component
============================================================================ */
function RadialMeter({ value, label, color, glow, sub, size = 148 }) {
  const r = 52;
  const c = 2 * Math.PI * r;
  const offset = c - (value / 100) * c;
  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} viewBox="0 0 120 120" className="-rotate-90">
          <circle cx="60" cy="60" r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="9" />
          <circle
            cx="60" cy="60" r={r} fill="none" stroke={color} strokeWidth="9" strokeLinecap="round"
            strokeDasharray={c} strokeDashoffset={offset} className="ss-ring"
            style={{ filter: `drop-shadow(0 0 8px ${glow})`, transition: "stroke-dashoffset 1s cubic-bezier(.22,.9,.3,1)" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="ss-mono ss-display font-bold" style={{ fontSize: size / 4.6, color: T.text }}>{value}</span>
          <span className="text-[10px] tracking-wide" style={{ color: T.textFaint }}>/ 100</span>
        </div>
      </div>
      <p className="text-xs font-semibold mt-3 tracking-wide" style={{ color: T.textMuted }}>{label}</p>
      {sub && <p className="text-[11px] mt-0.5" style={{ color: T.textFaint }}>{sub}</p>}
    </div>
  );
}

/* ============================================================================
   SIDEBAR / HEADER / SHELL
============================================================================ */
function NavIcon({ id, label, icon: Icon, active, onClick, glow }) {
  return (
    <button
      onClick={onClick}
      className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ss-focus group"
      style={{
        color: active ? T.text : T.textMuted,
        background: active ? "rgba(255,59,82,0.08)" : "transparent",
        borderLeft: active ? `2px solid ${T.red}` : "2px solid transparent",
      }}
      onMouseEnter={(e) => { if (!active) e.currentTarget.style.background = "rgba(255,255,255,0.04)"; }}
      onMouseLeave={(e) => { if (!active) e.currentTarget.style.background = "transparent"; }}
    >
      <Icon size={18} strokeWidth={active ? 2.3 : 2} style={glow && active ? { filter: `drop-shadow(0 0 6px ${T.redGlow})`, color: T.red } : active ? { color: T.red } : {}} />
      <span>{label}</span>
    </button>
  );
}

function Sidebar({ mobileOpen, setMobileOpen }) {
  const { page, navigate, user, logout } = useApp();
  const items = [
    { id: "dashboard", label: "Home", icon: Home, glow: true },
    { id: "scanner", label: "Scanner", icon: Mail },
    { id: "history", label: "History", icon: HistoryIcon },
    { id: "about", label: "About", icon: Info },
    { id: "settings", label: "Settings", icon: SettingsIcon },
  ];
  const content = (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2.5 px-3 py-2 mb-6">
        <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: "rgba(255,59,82,0.12)", border: `1px solid ${T.redGlow}` }}>
          <Shield size={19} color={T.red} style={{ filter: `drop-shadow(0 0 5px ${T.redGlow})` }} />
        </div>
        <div>
          <p className="ss-display font-bold text-sm leading-none">ScamShield</p>
          <p className="text-[10px] tracking-widest" style={{ color: T.textFaint }}>AI SECURITY</p>
        </div>
      </div>
      <nav className="flex flex-col gap-1 flex-1">
        {items.map((it) => (
          <NavIcon key={it.id} {...it} active={page === it.id} onClick={() => { navigate(it.id); setMobileOpen(false); }} />
        ))}
      </nav>
      <div className="pt-4 mt-4" style={{ borderTop: `1px solid ${T.border}` }}>
        <div className="flex items-center gap-2.5 px-3 py-2 rounded-xl mb-1" style={{ background: "rgba(255,255,255,0.03)" }}>
          <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0" style={{ background: T.panelSolid, border: `1px solid ${T.border}` }}>
            <User size={14} color={T.textMuted} />
          </div>
          <div className="min-w-0">
            <p className="text-xs font-medium truncate" style={{ color: T.text }}>{user?.name || "Demo Account"}</p>
            <p className="text-[10px] truncate" style={{ color: T.textFaint }}>{user?.email || "demo@scamshield.ai"}</p>
          </div>
        </div>
        <button onClick={logout} className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-medium ss-focus" style={{ color: T.textMuted }}>
          <LogOut size={15} /> Log out
        </button>
      </div>
    </div>
  );
  return (
    <>
      <aside className="hidden lg:flex flex-col w-64 flex-shrink-0 p-4 h-screen sticky top-0" style={{ borderRight: `1px solid ${T.border}` }}>
        {content}
      </aside>
      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-black/60" onClick={() => setMobileOpen(false)} />
          <aside className="absolute left-0 top-0 h-full w-72 p-4 ss-bg ss-fade-up" style={{ borderRight: `1px solid ${T.border}` }}>
            <button onClick={() => setMobileOpen(false)} className="absolute top-4 right-4 p-1.5 rounded-lg ss-focus" style={{ color: T.textMuted }}>
              <X size={18} />
            </button>
            {content}
          </aside>
        </div>
      )}
    </>
  );
}

function Header({ title, subtitle, onMenuClick }) {
  const { user } = useApp();
  return (
    <header className="flex items-center justify-between gap-4 px-5 lg:px-8 py-5 sticky top-0 z-30" style={{ background: "rgba(13,16,21,0.85)", backdropFilter: "blur(10px)", borderBottom: `1px solid ${T.border}` }}>
      <div className="flex items-center gap-3 min-w-0">
        <button onClick={onMenuClick} className="lg:hidden p-2 rounded-lg ss-focus" style={{ color: T.textMuted, background: T.panelSolid, border: `1px solid ${T.border}` }}>
          <Menu size={18} />
        </button>
        <div className="min-w-0">
          <h1 className="ss-display font-bold text-lg lg:text-xl truncate" style={{ color: T.text }}>{title}</h1>
          {subtitle && <p className="text-xs mt-0.5 truncate" style={{ color: T.textMuted }}>{subtitle}</p>}
        </div>
      </div>
      <div className="flex items-center gap-3 flex-shrink-0">
        <button className="p-2 rounded-lg ss-focus relative" style={{ color: T.textMuted, background: T.panelSolid, border: `1px solid ${T.border}` }} aria-label="Notifications">
          <BellRing size={16} />
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full" style={{ background: T.red }} />
        </button>
        <div className="hidden sm:flex items-center gap-2 pl-3" style={{ borderLeft: `1px solid ${T.border}` }}>
          <div className="w-7 h-7 rounded-full flex items-center justify-center" style={{ background: T.panelSolid, border: `1px solid ${T.border}` }}>
            <User size={13} color={T.textMuted} />
          </div>
          <span className="text-xs font-medium" style={{ color: T.text }}>{user?.name || "Demo Account"}</span>
        </div>
      </div>
    </header>
  );
}

function AppShell({ title, subtitle, children }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  return (
    <div className="flex min-h-screen ss-bg ss-grid">
      <Sidebar mobileOpen={mobileOpen} setMobileOpen={setMobileOpen} />
      <div className="flex-1 min-w-0">
        <Header title={title} subtitle={subtitle} onMenuClick={() => setMobileOpen(true)} />
        <main className="px-5 lg:px-8 py-6 lg:py-8 max-w-[1400px]">{children}</main>
      </div>
    </div>
  );
}

/* ============================================================================
   PUBLIC NAV (landing / about / faq when logged out)
============================================================================ */
function PublicHeader() {
  const { navigate } = useApp();
  const [open, setOpen] = useState(false);
  const links = [
    { id: "about", label: "About" },
    { id: "faq", label: "FAQ" },
  ];
  return (
    <header className="sticky top-0 z-40 px-5 lg:px-10 py-4" style={{ background: "rgba(13,16,21,0.85)", backdropFilter: "blur(10px)", borderBottom: `1px solid ${T.border}` }}>
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        <button onClick={() => navigate("landing")} className="flex items-center gap-2.5 ss-focus rounded-lg">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: "rgba(255,59,82,0.12)", border: `1px solid ${T.redGlow}` }}>
            <Shield size={16} color={T.red} style={{ filter: `drop-shadow(0 0 5px ${T.redGlow})` }} />
          </div>
          <span className="ss-display font-bold text-sm">ScamShield AI</span>
        </button>
        <nav className="hidden md:flex items-center gap-7">
          {links.map((l) => (
            <button key={l.id} onClick={() => navigate(l.id)} className="text-sm font-medium ss-focus rounded" style={{ color: T.textMuted }}>{l.label}</button>
          ))}
        </nav>
        <div className="hidden md:flex items-center gap-3">
          <Btn variant="ghost" size="sm" onClick={() => navigate("login")}>Log in</Btn>
          <Btn size="sm" onClick={() => navigate("register")}>Get started</Btn>
        </div>
        <button className="md:hidden p-2 rounded-lg ss-focus" style={{ color: T.textMuted }} onClick={() => setOpen((o) => !o)}>
          {open ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>
      {open && (
        <div className="md:hidden mt-4 flex flex-col gap-3 pb-2">
          {links.map((l) => <button key={l.id} onClick={() => { navigate(l.id); setOpen(false); }} className="text-sm font-medium text-left" style={{ color: T.textMuted }}>{l.label}</button>)}
          <Btn variant="outline" onClick={() => navigate("login")}>Log in</Btn>
          <Btn onClick={() => navigate("register")}>Get started</Btn>
        </div>
      )}
    </header>
  );
}

function PublicFooter() {
  const { navigate } = useApp();
  return (
    <footer className="px-5 lg:px-10 py-10 mt-10" style={{ borderTop: `1px solid ${T.border}` }}>
      <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-xs" style={{ color: T.textFaint }}>
        <p>© 2026 ScamShield AI — a Software Engineering demonstration project.</p>
        <div className="flex gap-5">
          <button onClick={() => navigate("about")} className="hover:underline">About</button>
          <button onClick={() => navigate("faq")} className="hover:underline">FAQ</button>
          <button onClick={() => navigate("login")} className="hover:underline">Log in</button>
        </div>
      </div>
    </footer>
  );
}

/* ============================================================================
   LANDING PAGE
============================================================================ */
function LandingPage() {
  const { navigate } = useApp();
  const features = [
    { icon: Gauge, title: "Risk scoring", desc: "Every message gets a 0–100 risk score so severity is instantly clear, never a bare label." },
    { icon: Fingerprint, title: "Threat indicators", desc: "See exactly which signals were detected — suspicious domains, urgency, credential requests, and more." },
    { icon: BadgeCheck, title: "Plain-language explanations", desc: "Every result includes a short, jargon-free explanation of why it was flagged." },
    { icon: Inbox, title: "Gmail-ready", desc: "Built to connect directly to your inbox for continuous protection, not just one-off checks." },
  ];
  const steps = [
    { n: "01", title: "Submit a message", desc: "Paste an email manually, or connect Gmail to scan messages directly from your inbox." },
    { n: "02", title: "AI analysis runs", desc: "The detection engine checks sender reputation, links, language patterns, and known threat signatures." },
    { n: "03", title: "Understand the result", desc: "Get a classification, risk score, confidence, and a clear explanation — plus what to do next." },
  ];
  return (
    <div className="ss-root ss-bg ss-grid min-h-screen">
      <PublicHeader />
      {/* HERO */}
      <section className="px-5 lg:px-10 pt-16 lg:pt-24 pb-16 relative overflow-hidden">
        <div className="max-w-6xl mx-auto grid lg:grid-cols-2 gap-14 items-center">
          <div className="ss-fade-up">
            <span className="inline-flex items-center gap-2 text-xs font-semibold px-3 py-1.5 rounded-full mb-6" style={{ background: T.redSoft, color: T.red, border: `1px solid ${T.redGlow}` }}>
              <Sparkles size={12} /> AI-powered threat detection
            </span>
            <h1 className="ss-display font-bold text-4xl lg:text-5xl leading-[1.08] mb-5" style={{ color: T.text }}>
              Know if an email is <span style={{ color: T.red, textShadow: `0 0 30px ${T.redGlow}` }}>dangerous</span> before you click.
            </h1>
            <p className="text-base leading-relaxed mb-8 max-w-lg" style={{ color: T.textMuted }}>
              ScamShield AI analyzes suspicious emails and explains, in plain language, whether they're safe, spam, phishing, or malicious — with a risk score, confidence level, and clear next steps.
            </p>
            <div className="flex flex-wrap gap-3">
              <Btn size="lg" icon={ScanLine} onClick={() => navigate("register")}>Analyze an email</Btn>
              <Btn size="lg" variant="outline" onClick={() => navigate("about")}>How it works</Btn>
            </div>
          </div>
          <div className="ss-fade-up" style={{ animationDelay: "0.1s" }}>
            <Panel className="p-5 relative" glow={T.redGlow}>
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-semibold" style={{ color: T.textMuted }}>LIVE ANALYSIS PREVIEW</span>
                <SeverityTag classification="phishing" size="sm" />
              </div>
              <div className="rounded-xl p-4 mb-4 ss-mono text-xs leading-relaxed" style={{ background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}`, color: T.textMuted }}>
                <p><span style={{ color: T.textFaint }}>From:</span> security@paypa1-support.com</p>
                <p><span style={{ color: T.textFaint }}>Subject:</span> URGENT: Your account requires immediate verification</p>
              </div>
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="rounded-xl p-3.5" style={{ background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}` }}>
                  <p className="text-[10px] mb-1" style={{ color: T.textFaint }}>RISK SCORE</p>
                  <p className="ss-mono font-bold text-2xl" style={{ color: T.red }}>94<span className="text-xs" style={{ color: T.textFaint }}>/100</span></p>
                </div>
                <div className="rounded-xl p-3.5" style={{ background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}` }}>
                  <p className="text-[10px] mb-1" style={{ color: T.textFaint }}>CONFIDENCE</p>
                  <p className="ss-mono font-bold text-2xl" style={{ color: T.text }}>97<span className="text-xs" style={{ color: T.textFaint }}>%</span></p>
                </div>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {["Suspicious Sender", "Urgent Language", "Suspicious URL", "Credential Request"].map((t) => (
                  <span key={t} className="text-[10px] px-2 py-1 rounded-md" style={{ background: T.redSoft, color: T.red, border: `1px solid ${T.redGlow}` }}>{t}</span>
                ))}
              </div>
            </Panel>
          </div>
        </div>
      </section>
      {/* FEATURES */}
      <section className="px-5 lg:px-10 py-16">
        <div className="max-w-6xl mx-auto">
          <h2 className="ss-display font-bold text-2xl lg:text-3xl mb-2 text-center" style={{ color: T.text }}>Detection that explains itself</h2>
          <p className="text-sm text-center mb-12 max-w-xl mx-auto" style={{ color: T.textMuted }}>Every result goes beyond a label — so you understand the threat, not just its name.</p>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {features.map((f) => (
              <Panel key={f.title} className="p-5">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-4" style={{ background: T.redSoft, border: `1px solid ${T.redGlow}` }}>
                  <f.icon size={18} color={T.red} />
                </div>
                <h3 className="font-semibold text-sm mb-1.5" style={{ color: T.text }}>{f.title}</h3>
                <p className="text-xs leading-relaxed" style={{ color: T.textMuted }}>{f.desc}</p>
              </Panel>
            ))}
          </div>
        </div>
      </section>
      {/* HOW IT WORKS */}
      <section id="how-it-works" className="px-5 lg:px-10 py-16" style={{ borderTop: `1px solid ${T.border}` }}>
        <div className="max-w-5xl mx-auto">
          <h2 className="ss-display font-bold text-2xl lg:text-3xl mb-12 text-center" style={{ color: T.text }}>How it works</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {steps.map((s, i) => (
              <div key={s.n} className="relative">
                <span className="ss-display ss-mono font-bold text-4xl block mb-3" style={{ color: "rgba(255,59,82,0.25)" }}>{s.n}</span>
                <h3 className="font-semibold text-sm mb-2" style={{ color: T.text }}>{s.title}</h3>
                <p className="text-xs leading-relaxed" style={{ color: T.textMuted }}>{s.desc}</p>
                {i < steps.length - 1 && <ArrowRight className="hidden md:block absolute top-2 -right-9" size={16} color={T.textFaint} />}
              </div>
            ))}
          </div>
        </div>
      </section>
      {/* CTA */}
      <section className="px-5 lg:px-10 py-16">
        <Panel className="max-w-4xl mx-auto p-10 text-center" glow={T.redGlow}>
          <h2 className="ss-display font-bold text-2xl mb-3" style={{ color: T.text }}>Ready to check a suspicious email?</h2>
          <p className="text-sm mb-7" style={{ color: T.textMuted }}>Create a free demo account and run your first analysis in under a minute.</p>
          <Btn size="lg" icon={ScanLine} onClick={() => navigate("register")}>Analyze an email</Btn>
        </Panel>
      </section>
      <PublicFooter />
    </div>
  );
}

/* ============================================================================
   AUTH PAGES
============================================================================ */
function AuthShell({ title, subtitle, children, footer }) {
  const { navigate } = useApp();
  return (
    <div className="ss-root ss-bg ss-grid min-h-screen flex flex-col">
      <div className="px-5 py-5">
        <button onClick={() => navigate("landing")} className="flex items-center gap-2.5 ss-focus rounded-lg w-fit">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: "rgba(255,59,82,0.12)", border: `1px solid ${T.redGlow}` }}>
            <Shield size={16} color={T.red} />
          </div>
          <span className="ss-display font-bold text-sm">ScamShield AI</span>
        </button>
      </div>
      <div className="flex-1 flex items-center justify-center px-5 py-10">
        <Panel className="w-full max-w-md p-7 lg:p-8 ss-fade-up">
          <h1 className="ss-display font-bold text-xl mb-1.5" style={{ color: T.text }}>{title}</h1>
          <p className="text-sm mb-7" style={{ color: T.textMuted }}>{subtitle}</p>
          {children}
          {footer}
        </Panel>
      </div>
    </div>
  );
}

function LoginPage() {
  const { navigate, login } = useApp();
  const [form, setForm] = useState({ email: "demo@scamshield.ai", password: "" });
  const [showPw, setShowPw] = useState(false);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  function submit(e) {
    e.preventDefault();
    const errs = {};
    if (!form.email) errs.email = "Email is required.";
    if (!form.password) errs.password = "Password is required.";
    setErrors(errs);
    if (Object.keys(errs).length) return;
    setLoading(true);
    setTimeout(() => { login({ name: "Demo Account", email: form.email }); setLoading(false); navigate("dashboard"); }, 700);
  }

  return (
    <AuthShell
      title="Welcome back"
      subtitle="Log in to your ScamShield AI dashboard."
      footer={<p className="text-xs text-center mt-6" style={{ color: T.textMuted }}>Don't have an account?{" "}<button onClick={() => navigate("register")} className="font-semibold ss-focus rounded" style={{ color: T.red }}>Create one</button></p>}
    >
      <div className="mb-5 flex items-start gap-2 rounded-lg px-3 py-2.5 text-[11px]" style={{ background: T.amberSoft, border: `1px solid ${T.amberGlow}`, color: T.amber }}>
        <Info size={13} className="mt-0.5 flex-shrink-0" />
        <span>This is simulated authentication for demonstration purposes — no real account is created. Any password will work.</span>
      </div>
      <form onSubmit={submit} className="flex flex-col gap-4" noValidate>
        <Field label="Email" error={errors.email}>
          <input type="email" className={inputClass()} style={inputStyle} placeholder="you@example.com" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        </Field>
        <Field label="Password" error={errors.password}>
          <div className="relative">
            <input type={showPw ? "text" : "password"} className={inputClass("pr-10")} style={inputStyle} placeholder="••••••••" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
            <button type="button" onClick={() => setShowPw((s) => !s)} className="absolute right-3 top-1/2 -translate-y-1/2 ss-focus rounded" style={{ color: T.textFaint }} aria-label={showPw ? "Hide password" : "Show password"}>
              {showPw ? <EyeOff size={15} /> : <Eye size={15} />}
            </button>
          </div>
        </Field>
        <Btn type="submit" size="md" className="w-full mt-1" disabled={loading}>
          {loading ? <Loader2 size={16} className="animate-spin" /> : <Lock size={15} />} {loading ? "Logging in..." : "Log in"}
        </Btn>
      </form>
    </AuthShell>
  );
}

function RegisterPage() {
  const { navigate, login } = useApp();
  const [form, setForm] = useState({ name: "", email: "", password: "", confirm: "" });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  function submit(e) {
    e.preventDefault();
    const errs = {};
    if (!form.name) errs.name = "Name is required.";
    if (!form.email) errs.email = "Email is required.";
    if (!form.password) errs.password = "Password is required.";
    else if (form.password.length < 6) errs.password = "Use at least 6 characters.";
    if (form.confirm !== form.password) errs.confirm = "Passwords do not match.";
    setErrors(errs);
    if (Object.keys(errs).length) return;
    setLoading(true);
    setTimeout(() => { login({ name: form.name, email: form.email }); setLoading(false); navigate("dashboard"); }, 700);
  }

  return (
    <AuthShell
      title="Create your account"
      subtitle="Start analyzing suspicious emails in minutes."
      footer={<p className="text-xs text-center mt-6" style={{ color: T.textMuted }}>Already have an account?{" "}<button onClick={() => navigate("login")} className="font-semibold ss-focus rounded" style={{ color: T.red }}>Log in</button></p>}
    >
      <div className="mb-5 flex items-start gap-2 rounded-lg px-3 py-2.5 text-[11px]" style={{ background: T.amberSoft, border: `1px solid ${T.amberGlow}`, color: T.amber }}>
        <Info size={13} className="mt-0.5 flex-shrink-0" />
        <span>Simulated registration for demonstration purposes — no data leaves your browser session.</span>
      </div>
      <form onSubmit={submit} className="flex flex-col gap-4" noValidate>
        <Field label="Name" error={errors.name}>
          <input className={inputClass()} style={inputStyle} placeholder="Jane Doe" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        </Field>
        <Field label="Email" error={errors.email}>
          <input type="email" className={inputClass()} style={inputStyle} placeholder="you@example.com" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        </Field>
        <Field label="Password" error={errors.password} hint="At least 6 characters.">
          <input type="password" className={inputClass()} style={inputStyle} placeholder="••••••••" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        </Field>
        <Field label="Confirm password" error={errors.confirm}>
          <input type="password" className={inputClass()} style={inputStyle} placeholder="••••••••" value={form.confirm} onChange={(e) => setForm({ ...form, confirm: e.target.value })} />
        </Field>
        <Btn type="submit" size="md" className="w-full mt-1" disabled={loading}>
          {loading ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={15} />} {loading ? "Creating account..." : "Create account"}
        </Btn>
      </form>
    </AuthShell>
  );
}

/* ============================================================================
   DASHBOARD
============================================================================ */
function computeStats(scans) {
  const totalScans = scans.length;
  const threatsDetected = scans.filter((s) => s.classification !== "safe").length;
  const safeMessages = scans.filter((s) => s.classification === "safe").length;
  const highRisk = scans.filter((s) => s.severity === "high" || s.severity === "critical").length;

  const days = [...Array(14)].map((_, i) => 13 - i).map((n) => {
    const d = new Date(); d.setDate(d.getDate() - n); d.setHours(0, 0, 0, 0);
    return d;
  });
  const activity = days.map((d) => {
    const key = d.toDateString();
    const dayScans = scans.filter((s) => new Date(s.date).toDateString() === key);
    return {
      date: d.toLocaleDateString("en-US", { month: "short", day: "numeric" }),
      scans: dayScans.length,
      threats: dayScans.filter((s) => s.classification !== "safe").length,
    };
  });

  const distribution = ["safe", "spam", "phishing", "malicious"].map((c) => ({
    name: SEV[c].label, key: c, value: scans.filter((s) => s.classification === c).length, color: SEV[c].text,
  }));

  return { totalScans, threatsDetected, safeMessages, highRisk, activity, distribution };
}

function StatCard({ icon: Icon, label, value, tint }) {
  return (
    <Panel className="p-5">
      <div className="flex items-center justify-between mb-3">
        <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ background: tint.soft, border: `1px solid ${tint.ring}` }}>
          <Icon size={16} color={tint.text} />
        </div>
      </div>
      <p className="ss-mono ss-display font-bold text-2xl lg:text-3xl" style={{ color: T.text }}>{value}</p>
      <p className="text-xs mt-1" style={{ color: T.textMuted }}>{label}</p>
    </Panel>
  );
}

function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="ss-panel rounded-lg px-3 py-2 text-xs" style={{ background: "rgba(18,21,27,0.95)" }}>
      <p className="font-semibold mb-1" style={{ color: T.text }}>{label}</p>
      {payload.map((p) => (
        <p key={p.dataKey} style={{ color: p.color }}>{p.name}: <span className="ss-mono">{p.value}</span></p>
      ))}
    </div>
  );
}

function DashboardPage() {
  const { scans, navigate } = useApp();
  const stats = useMemo(() => computeStats(scans), [scans]);
  const recent = scans.slice(0, 6);

  return (
    <AppShell title="Dashboard" subtitle="Your security overview at a glance">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <p className="text-sm max-w-md" style={{ color: T.textMuted }}>Track scan activity, threat trends, and recent detections across your account.</p>
        <Btn icon={ScanLine} onClick={() => navigate("scanner")} className="flex-shrink-0">Analyze an email</Btn>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard icon={ScanLine} label="Total Scans" value={stats.totalScans} tint={{ text: T.text, soft: "rgba(255,255,255,0.06)", ring: T.border }} />
        <StatCard icon={ShieldAlert} label="Threats Detected" value={stats.threatsDetected} tint={{ text: T.red, soft: T.redSoft, ring: T.redGlow }} />
        <StatCard icon={ShieldCheck} label="Safe Messages" value={stats.safeMessages} tint={{ text: T.green, soft: T.greenSoft, ring: T.greenGlow }} />
        <StatCard icon={TriangleAlert} label="High Risk" value={stats.highRisk} tint={{ text: T.amber, soft: T.amberSoft, ring: T.amberGlow }} />
      </div>

      <div className="grid lg:grid-cols-3 gap-4 mb-6">
        <Panel className="lg:col-span-2 p-5">
          <h3 className="font-semibold text-sm mb-4" style={{ color: T.text }}>Threat activity over time</h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={stats.activity} margin={{ left: -20, right: 8, top: 5 }}>
                <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
                <XAxis dataKey="date" tick={{ fill: T.textFaint, fontSize: 10 }} axisLine={{ stroke: T.border }} tickLine={false} interval={2} />
                <YAxis tick={{ fill: T.textFaint, fontSize: 10 }} axisLine={false} tickLine={false} allowDecimals={false} />
                <Tooltip content={<ChartTooltip />} />
                <Line type="monotone" dataKey="scans" name="Scans" stroke="#8b93a3" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="threats" name="Threats" stroke={T.red} strokeWidth={2.5} dot={false} style={{ filter: `drop-shadow(0 0 4px ${T.redGlow})` }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel className="p-5">
          <h3 className="font-semibold text-sm mb-4" style={{ color: T.text }}>Threat distribution</h3>
          <div className="h-40">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={stats.distribution} dataKey="value" nameKey="name" innerRadius={44} outerRadius={64} paddingAngle={3} stroke="none">
                  {stats.distribution.map((d) => <Cell key={d.key} fill={d.color} />)}
                </Pie>
                <Tooltip content={<ChartTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-2 mt-2">
            {stats.distribution.map((d) => (
              <div key={d.key} className="flex items-center gap-1.5 text-[11px]">
                <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: d.color }} />
                <span style={{ color: T.textMuted }}>{d.name}</span>
                <span className="ss-mono ml-auto" style={{ color: T.text }}>{d.value}</span>
              </div>
            ))}
          </div>
        </Panel>
      </div>

      <Panel className="p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-sm" style={{ color: T.text }}>Recent threat activity</h3>
          <button onClick={() => navigate("history")} className="text-xs font-semibold ss-focus rounded flex items-center gap-1" style={{ color: T.red }}>
            View all <ChevronRight size={13} />
          </button>
        </div>
        <ScanTable scans={recent} compact />
      </Panel>
    </AppShell>
  );
}

/* ============================================================================
   SCAN TABLE (shared: dashboard + history)
============================================================================ */
function ScanTable({ scans, compact = false }) {
  const { navigate, setActiveScanId } = useApp();
  if (!scans.length) {
    return <EmptyState icon={Search} title="No scans found" description="Try adjusting your filters, or run a new analysis to see results here." />;
  }
  function openReport(id) {
    setActiveScanId(id);
    navigate("report");
  }
  return (
    <>
      {/* Desktop table */}
      <div className="hidden md:block overflow-x-auto ss-scroll -mx-1">
        <table className="w-full text-sm min-w-[720px]">
          <thead>
            <tr className="text-left" style={{ color: T.textFaint }}>
              <th className="font-medium text-xs pb-3 px-1">Date</th>
              <th className="font-medium text-xs pb-3 px-1">Sender</th>
              <th className="font-medium text-xs pb-3 px-1">Subject</th>
              <th className="font-medium text-xs pb-3 px-1">Classification</th>
              <th className="font-medium text-xs pb-3 px-1">Risk</th>
              <th className="font-medium text-xs pb-3 px-1"></th>
            </tr>
          </thead>
          <tbody>
            {scans.map((s) => (
              <tr key={s.id} onClick={() => openReport(s.id)} className="cursor-pointer transition-colors duration-150 group" style={{ borderTop: `1px solid ${T.border}` }}
                onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(255,255,255,0.02)")}
                onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}>
                <td className="py-3 px-1 text-xs whitespace-nowrap" style={{ color: T.textMuted }}>{new Date(s.date).toLocaleDateString("en-US", { month: "short", day: "numeric" })}</td>
                <td className="py-3 px-1 text-xs max-w-[180px] truncate" style={{ color: T.text }}>{s.sender}</td>
                <td className="py-3 px-1 text-xs max-w-[240px] truncate" style={{ color: T.textMuted }}>{s.subject}</td>
                <td className="py-3 px-1"><SeverityTag classification={s.classification} size="sm" /></td>
                <td className="py-3 px-1"><span className="ss-mono text-xs font-semibold" style={{ color: SEV[s.classification].text }}>{s.risk}</span></td>
                <td className="py-3 px-1 text-right">
                  <span className="text-xs font-medium inline-flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity" style={{ color: T.red }}>
                    View <ChevronRight size={12} />
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {/* Mobile cards */}
      <div className="md:hidden flex flex-col gap-2.5">
        {scans.map((s) => (
          <button key={s.id} onClick={() => openReport(s.id)} className="text-left rounded-xl p-3.5 ss-focus" style={{ background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}` }}>
            <div className="flex items-center justify-between mb-2">
              <SeverityTag classification={s.classification} size="sm" />
              <span className="ss-mono text-xs font-semibold" style={{ color: SEV[s.classification].text }}>{s.risk}/100</span>
            </div>
            <p className="text-sm font-medium truncate mb-0.5" style={{ color: T.text }}>{s.subject}</p>
            <div className="flex items-center justify-between">
              <p className="text-xs truncate" style={{ color: T.textMuted }}>{s.sender}</p>
              <p className="text-[11px] flex-shrink-0 ml-2" style={{ color: T.textFaint }}>{new Date(s.date).toLocaleDateString("en-US", { month: "short", day: "numeric" })}</p>
            </div>
          </button>
        ))}
      </div>
    </>
  );
}

/* ============================================================================
   SCANNER PAGE
============================================================================ */
function ScannerPage() {
  const { navigate, addScan } = useApp();
  const [tab, setTab] = useState("manual");
  const [form, setForm] = useState({ sender: "", subject: "", body: "", url: "" });
  const [errors, setErrors] = useState({});

  const DEMO = {
    sender: "security@paypa1-support.com",
    subject: "URGENT: Your account requires immediate verification",
    body: "Your account will be permanently suspended unless you verify your information immediately. Click the link below to confirm your identity.",
    url: "https://paypa1-support.example.com/verify",
  };

  function runAnalysis(e) {
    e?.preventDefault?.();
    const errs = {};
    if (!form.sender) errs.sender = "Sender email is required.";
    if (!form.subject) errs.subject = "Subject is required.";
    if (!form.body) errs.body = "Email body is required.";
    setErrors(errs);
    if (Object.keys(errs).length) return;
    const scanId = addScan({ ...form, source: "manual" });
    navigate("analysis", { scanId });
  }

  return (
    <AppShell title="Email Scanner" subtitle="Analyze a suspicious email manually or from Gmail">
      <div className="flex gap-2 mb-6 p-1 rounded-xl w-fit" style={{ background: T.panelSolid, border: `1px solid ${T.border}` }}>
        {[{ id: "manual", label: "Manual Analysis", icon: FileText }, { id: "gmail", label: "Gmail Integration", icon: Inbox }].map((t) => (
          <button key={t.id} onClick={() => setTab(t.id)} className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ss-focus"
            style={tab === t.id ? { background: T.red, color: "#fff", boxShadow: `0 2px 14px -2px ${T.redGlow}` } : { color: T.textMuted }}>
            <t.icon size={15} /> {t.label}
          </button>
        ))}
      </div>

      {tab === "manual" ? (
        <div className="grid lg:grid-cols-3 gap-5">
          <Panel className="lg:col-span-2 p-6">
            <div className="flex items-center justify-between mb-5">
              <h3 className="font-semibold text-sm" style={{ color: T.text }}>Email details</h3>
              <button onClick={() => setForm(DEMO)} className="text-xs font-semibold flex items-center gap-1.5 ss-focus rounded" style={{ color: T.red }}>
                <Sparkles size={13} /> Try a sample phishing email
              </button>
            </div>
            <form onSubmit={runAnalysis} className="flex flex-col gap-4" noValidate>
              <Field label="Sender email" error={errors.sender}>
                <input className={inputClass()} style={inputStyle} placeholder="sender@example.com" value={form.sender} onChange={(e) => setForm({ ...form, sender: e.target.value })} />
              </Field>
              <Field label="Subject" error={errors.subject}>
                <input className={inputClass()} style={inputStyle} placeholder="Email subject line" value={form.subject} onChange={(e) => setForm({ ...form, subject: e.target.value })} />
              </Field>
              <Field label="Email body" error={errors.body}>
                <textarea rows={6} className={inputClass()} style={inputStyle} placeholder="Paste the full email content here..." value={form.body} onChange={(e) => setForm({ ...form, body: e.target.value })} />
              </Field>
              <Field label="URL (optional)" hint="Include any link found in the email, if present.">
                <input className={inputClass()} style={inputStyle} placeholder="https://..." value={form.url} onChange={(e) => setForm({ ...form, url: e.target.value })} />
              </Field>
              <Btn type="submit" size="lg" icon={ScanLine} className="mt-2 w-full sm:w-fit">Analyze email</Btn>
            </form>
          </Panel>
          <Panel className="p-6 h-fit">
            <h3 className="font-semibold text-sm mb-3 flex items-center gap-2" style={{ color: T.text }}><Info size={15} color={T.textMuted} /> What we check</h3>
            <ul className="flex flex-col gap-3 text-xs" style={{ color: T.textMuted }}>
              {["Sender domain reputation", "Embedded URL destinations", "Urgency & pressure language", "Credential or payment requests", "Known scam patterns"].map((it) => (
                <li key={it} className="flex items-start gap-2"><CircleCheck size={14} className="mt-0.5 flex-shrink-0" color={T.green} />{it}</li>
              ))}
            </ul>
            <div className="mt-5 pt-4 text-[11px] leading-relaxed" style={{ borderTop: `1px solid ${T.border}`, color: T.textFaint }}>
              This runs against demonstration data for this prototype. No content is sent to a real detection backend yet.
            </div>
          </Panel>
        </div>
      ) : (
        <GmailPanel />
      )}
    </AppShell>
  );
}

function GmailPanel() {
  const { gmailConnected, setGmailConnected, navigate, addScan, inbox, setInbox } = useApp();
  const [connecting, setConnecting] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [analyzingId, setAnalyzingId] = useState(null);

  function connect() {
    setShowModal(false);
    setConnecting(true);
    setTimeout(() => { setConnecting(false); setGmailConnected(true); }, 1100);
  }

  function analyze(msg) {
    setAnalyzingId(msg.id);
    setTimeout(() => {
      const scanData = SCANS_SEED.find((s) => s.id === msg.linkedScanId) || {
        sender: msg.from, subject: msg.subject, body: msg.snippet, url: "",
      };
      const scanId = addScan({ ...scanData, source: "gmail" });
      setInbox((prev) => prev.map((m) => (m.id === msg.id ? { ...m, analyzed: true, linkedScanId: scanId } : m)));
      setAnalyzingId(null);
      navigate("analysis", { scanId });
    }, 900);
  }

  if (!gmailConnected) {
    return (
      <Panel className="p-8 lg:p-12 max-w-xl">
        <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-5" style={{ background: T.redSoft, border: `1px solid ${T.redGlow}` }}>
          <Inbox size={22} color={T.red} />
        </div>
        <h3 className="ss-display font-bold text-lg mb-2" style={{ color: T.text }}>Connect Gmail</h3>
        <p className="text-sm leading-relaxed mb-5" style={{ color: T.textMuted }}>
          Connect your Gmail account to scan messages directly from your inbox, without copying and pasting each one manually.
        </p>
        <div className="rounded-xl p-4 mb-6 text-xs leading-relaxed flex gap-2.5" style={{ background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}`, color: T.textMuted }}>
          <Lock size={14} className="flex-shrink-0 mt-0.5" color={T.textFaint} />
          <span>ScamShield requests <strong style={{ color: T.text }}>read-only</strong> access to scan message content. Nothing is ever sent, deleted, or modified. You can disconnect at any time from Settings.</span>
        </div>
        <Btn icon={connecting ? Loader2 : Inbox} onClick={() => setShowModal(true)} disabled={connecting}>
          {connecting ? "Connecting..." : "Connect Gmail"}
        </Btn>
      </Panel>
    );
  }

  return (
    <div>
      <Panel className="p-4 mb-5 flex items-center gap-3" style={{ background: T.greenSoft }}>
        <CircleCheck size={18} color={T.green} />
        <div className="flex-1">
          <p className="text-sm font-medium" style={{ color: T.text }}>Gmail connected (demo mode)</p>
          <p className="text-xs" style={{ color: T.textMuted }}>Showing sample inbox data — no real Google account is accessed.</p>
        </div>
        <button onClick={() => setGmailConnected(false)} className="text-xs font-semibold ss-focus rounded" style={{ color: T.textMuted }}>Disconnect</button>
      </Panel>
      <Panel className="p-0 overflow-hidden">
        <div className="px-5 py-4 flex items-center justify-between" style={{ borderBottom: `1px solid ${T.border}` }}>
          <h3 className="font-semibold text-sm" style={{ color: T.text }}>Inbox</h3>
          <RefreshCw size={14} color={T.textFaint} />
        </div>
        <div className="divide-y" style={{ borderColor: T.border }}>
          {inbox.map((m) => (
            <div key={m.id} className="px-5 py-4 flex items-center gap-4" style={{ borderTop: `1px solid ${T.border}` }}>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2 mb-0.5">
                  <p className="text-sm font-medium truncate" style={{ color: T.text }}>{m.from}</p>
                  {m.analyzed && <span className="text-[10px] px-1.5 py-0.5 rounded flex-shrink-0" style={{ background: T.panelSolid, color: T.textFaint, border: `1px solid ${T.border}` }}>Analyzed</span>}
                </div>
                <p className="text-sm truncate" style={{ color: T.textMuted }}>{m.subject}</p>
                <p className="text-xs truncate mt-0.5" style={{ color: T.textFaint }}>{m.snippet}</p>
              </div>
              <Btn size="sm" variant={m.analyzed ? "outline" : "primary"} onClick={() => analyze(m)} disabled={analyzingId === m.id}>
                {analyzingId === m.id ? <Loader2 size={13} className="animate-spin" /> : <ScanLine size={13} />}
                {analyzingId === m.id ? "Analyzing" : m.analyzed ? "Re-analyze" : "Analyze"}
              </Btn>
            </div>
          ))}
        </div>
      </Panel>

      {showModal && <GmailConsentModal onConfirm={connect} onCancel={() => setShowModal(false)} />}
    </div>
  );
}

function GmailConsentModal({ onConfirm, onCancel }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-5" style={{ background: "rgba(0,0,0,0.7)" }} onClick={onCancel}>
      <div className="w-full max-w-sm rounded-2xl p-6 ss-fade-up" style={{ background: "#1a1d24", border: `1px solid ${T.borderBright}` }} onClick={(e) => e.stopPropagation()}>
        <span className="text-[10px] font-bold tracking-widest px-2 py-1 rounded" style={{ background: T.amberSoft, color: T.amber }}>DEMO MODE</span>
        <p className="text-sm mt-3 mb-1" style={{ color: T.textMuted }}>ScamShield AI wants to access your Google Account</p>
        <p className="ss-display font-bold text-lg mb-4" style={{ color: T.text }}>demo.user@gmail.com</p>
        <div className="rounded-xl p-3.5 mb-5 text-xs leading-relaxed" style={{ background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}`, color: T.textMuted }}>
          This will allow ScamShield AI to: <strong style={{ color: T.text }}>view your email messages (read-only)</strong>. This is a simulated consent screen — no real Google authentication occurs.
        </div>
        <div className="flex gap-3">
          <Btn variant="outline" className="flex-1" onClick={onCancel}>Cancel</Btn>
          <Btn className="flex-1" onClick={onConfirm}>Allow</Btn>
        </div>
      </div>
    </div>
  );
}

/* ============================================================================
   ANALYSIS + RESULT
============================================================================ */
function AnalysisPage() {
  const { scans, activeScanIdForAnalysis } = useApp();
  const [stepIndex, setStepIndex] = useState(0);
  const [done, setDone] = useState(false);
  const scan = scans.find((s) => s.id === activeScanIdForAnalysis);

  useEffect(() => {
    setStepIndex(0);
    setDone(false);
    const interval = setInterval(() => {
      setStepIndex((i) => {
        if (i >= ANALYSIS_STEPS.length - 1) { clearInterval(interval); setTimeout(() => setDone(true), 500); return i; }
        return i + 1;
      });
    }, 480);
    return () => clearInterval(interval);
  }, [activeScanIdForAnalysis]);

  if (!scan) {
    return <AppShell title="Analysis"><EmptyState icon={AlertTriangle} title="No scan selected" description="Start a new analysis from the Scanner page." /></AppShell>;
  }

  return (
    <AppShell title="Analyzing message" subtitle={scan.subject}>
      {!done ? (
        <Panel className="max-w-2xl mx-auto p-8 lg:p-10 text-center relative overflow-hidden">
          <div className="relative w-20 h-20 mx-auto mb-6 rounded-2xl flex items-center justify-center overflow-hidden" style={{ background: T.redSoft, border: `1px solid ${T.redGlow}` }}>
            <div className="absolute inset-0 ss-sweep" />
            <ScanLine size={30} color={T.red} className="ss-pulse" />
          </div>
          <h2 className="ss-display font-bold text-lg mb-1" style={{ color: T.text }}>Running threat analysis</h2>
          <p className="text-xs mb-8" style={{ color: T.textFaint }}>This will only take a moment</p>
          <div className="flex flex-col gap-3 text-left max-w-sm mx-auto">
            {ANALYSIS_STEPS.map((s, i) => (
              <div key={s} className="flex items-center gap-3 text-sm">
                {i < stepIndex ? <CheckCircle2 size={17} color={T.green} className="flex-shrink-0" />
                  : i === stepIndex ? <Loader2 size={17} color={T.red} className="animate-spin flex-shrink-0" />
                  : <Circle size={17} color={T.textFaint} className="flex-shrink-0" />}
                <span style={{ color: i <= stepIndex ? T.text : T.textFaint }}>{s}</span>
              </div>
            ))}
          </div>
        </Panel>
      ) : (
        <ResultView scan={scan} />
      )}
    </AppShell>
  );
}

function ResultView({ scan, isReport = false }) {
  const { navigate } = useApp();
  const c = SEV[scan.classification];
  const positive = scan.classification === "safe";
  return (
    <div className="max-w-3xl mx-auto ss-fade-up">
      <Panel className="p-6 lg:p-8 mb-5" glow={c.glow}>
        <div className="flex flex-wrap items-start justify-between gap-4 mb-6">
          <div>
            <p className="text-xs mb-2" style={{ color: T.textFaint }}>CLASSIFICATION</p>
            <SeverityTag classification={scan.classification} />
          </div>
          {!isReport && (
            <Btn variant="outline" size="sm" icon={FileText} onClick={() => navigate("report", { scanId: scan.id })}>View full report</Btn>
          )}
        </div>

        <div className="grid sm:grid-cols-2 gap-6 mb-7 py-6" style={{ borderTop: `1px solid ${T.border}`, borderBottom: `1px solid ${T.border}` }}>
          <RadialMeter value={scan.risk} label="RISK SCORE" sub={scan.severity.toUpperCase() + " SEVERITY"} color={c.text} glow={c.glow} />
          <RadialMeter value={scan.confidence} label="DETECTION CONFIDENCE" sub="Model certainty" color={T.text} glow="rgba(255,255,255,0.15)" />
        </div>
        <div className="flex items-start gap-2 text-[11px] leading-relaxed mb-7 rounded-lg px-3.5 py-3" style={{ background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}`, color: T.textMuted }}>
          <HelpCircle size={14} className="flex-shrink-0 mt-0.5" color={T.textFaint} />
          <span><strong style={{ color: T.text }}>Risk</strong> measures how dangerous this message is if acted on. <strong style={{ color: T.text }}>Confidence</strong> measures how certain the detection engine is about this classification. They're independent — read both.</span>
        </div>

        <h3 className="font-semibold text-sm mb-3" style={{ color: T.text }}>{positive ? "What we checked" : "Threat indicators"}</h3>
        <div className="flex flex-col gap-2.5 mb-7">
          {scan.indicators.map((ind) => (
            <div key={ind.id} className="flex items-start gap-3 rounded-xl p-3.5" style={{ background: positive ? T.greenSoft : "rgba(255,255,255,0.03)", border: `1px solid ${positive ? T.greenGlow : T.border}` }}>
              {positive ? <CircleCheck size={16} color={T.green} className="mt-0.5 flex-shrink-0" /> : <TriangleAlert size={16} color={SEV[scan.classification].text} className="mt-0.5 flex-shrink-0" />}
              <div className="min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <p className="text-sm font-medium" style={{ color: T.text }}>{ind.label}</p>
                  {!positive && <span className="text-[10px] px-1.5 py-0.5 rounded font-semibold uppercase" style={{ color: SEV[scan.classification].text, background: SEV[scan.classification].soft }}>{ind.severity}</span>}
                </div>
                <p className="text-xs mt-0.5" style={{ color: T.textMuted }}>{ind.description}</p>
              </div>
            </div>
          ))}
        </div>

        <h3 className="font-semibold text-sm mb-2" style={{ color: T.text }}>Why was this flagged?</h3>
        <p className="text-sm leading-relaxed mb-7" style={{ color: T.textMuted }}>{scan.explanation}</p>

        <div className="rounded-xl p-4 flex items-start gap-3" style={{ background: c.soft, border: `1px solid ${c.ring}` }}>
          {positive ? <ShieldCheck size={20} color={c.text} className="flex-shrink-0" /> : <ShieldAlert size={20} color={c.text} className="flex-shrink-0" />}
          <div>
            <p className="text-xs font-semibold mb-0.5" style={{ color: c.text }}>RECOMMENDED ACTION</p>
            <p className="text-sm" style={{ color: T.text }}>{scan.recommendedAction}</p>
          </div>
        </div>
      </Panel>

      <details className="mb-5">
        <summary className="cursor-pointer text-xs font-semibold ss-focus rounded flex items-center gap-1.5 w-fit" style={{ color: T.textMuted }}>
          <ChevronDown size={13} /> View original message content
        </summary>
        <Panel className="p-4 mt-2 ss-mono text-xs leading-relaxed" style={{ color: T.textMuted }}>
          <p className="mb-1"><span style={{ color: T.textFaint }}>From:</span> {scan.sender}</p>
          <p className="mb-1"><span style={{ color: T.textFaint }}>Subject:</span> {scan.subject}</p>
          {scan.url && <p className="mb-2"><span style={{ color: T.textFaint }}>Link:</span> {scan.url}</p>}
          <p style={{ borderTop: `1px solid ${T.border}`, paddingTop: "8px", marginTop: "8px" }}>{scan.body}</p>
        </Panel>
      </details>

      {!isReport && (
        <div className="flex flex-wrap gap-3">
          <Btn icon={ScanLine} onClick={() => navigate("scanner")}>Analyze another email</Btn>
          <Btn variant="outline" icon={HistoryIcon} onClick={() => navigate("history")}>Go to scan history</Btn>
        </div>
      )}
    </div>
  );
}

/* ============================================================================
   HISTORY PAGE
============================================================================ */
function HistoryPage() {
  const { scans } = useApp();
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");
  const [sort, setSort] = useState("newest");

  const filtered = useMemo(() => {
    let r = [...scans];
    if (filter !== "all") r = r.filter((s) => s.classification === filter);
    if (search) {
      const q = search.toLowerCase();
      r = r.filter((s) => s.sender.toLowerCase().includes(q) || s.subject.toLowerCase().includes(q));
    }
    if (sort === "newest") r.sort((a, b) => new Date(b.date) - new Date(a.date));
    if (sort === "oldest") r.sort((a, b) => new Date(a.date) - new Date(b.date));
    if (sort === "risk") r.sort((a, b) => b.risk - a.risk);
    return r;
  }, [scans, search, filter, sort]);

  const filters = [
    { id: "all", label: "All" }, { id: "safe", label: "Safe" }, { id: "spam", label: "Spam" },
    { id: "phishing", label: "Phishing" }, { id: "malicious", label: "Malicious" },
  ];

  return (
    <AppShell title="Scan History" subtitle={`${scans.length} messages analyzed`}>
      <Panel className="p-4 mb-5">
        <div className="flex flex-col lg:flex-row gap-3 lg:items-center">
          <div className="relative flex-1">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2" color={T.textFaint} />
            <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search by sender or subject..." className={inputClass("pl-9")} style={inputStyle} />
          </div>
          <div className="flex items-center gap-2">
            <ArrowUpDown size={14} color={T.textFaint} />
            <select value={sort} onChange={(e) => setSort(e.target.value)} className="text-xs rounded-lg px-3 py-2.5 ss-focus" style={{ ...inputStyle, colorScheme: "dark" }}>
              <option value="newest">Newest first</option>
              <option value="oldest">Oldest first</option>
              <option value="risk">Highest risk</option>
            </select>
          </div>
        </div>
        <div className="flex flex-wrap gap-2 mt-3.5">
          {filters.map((f) => (
            <button key={f.id} onClick={() => setFilter(f.id)} className="text-xs font-medium px-3 py-1.5 rounded-full transition-all ss-focus"
              style={filter === f.id ? { background: f.id === "all" ? T.panelSolid : SEV[f.id]?.soft, color: f.id === "all" ? T.text : SEV[f.id]?.text, border: `1px solid ${f.id === "all" ? T.borderBright : SEV[f.id]?.ring}` } : { color: T.textMuted, border: `1px solid ${T.border}` }}>
              {f.label}
            </button>
          ))}
        </div>
      </Panel>
      <Panel className="p-5">
        <ScanTable scans={filtered} />
      </Panel>
    </AppShell>
  );
}

/* ============================================================================
   REPORT PAGE
============================================================================ */
function ReportPage() {
  const { scans, activeScanId, navigate } = useApp();
  const scan = scans.find((s) => s.id === activeScanId);

  if (!scan) {
    return <AppShell title="Security Report"><EmptyState icon={FileText} title="No report selected" description="Choose a scan from your history to view its full report." action={<Btn onClick={() => navigate("history")}>Go to history</Btn>} /></AppShell>;
  }

  return (
    <AppShell title="Security Report" subtitle={`Scan ID: ${scan.id}`}>
      <button onClick={() => navigate("history")} className="flex items-center gap-1.5 text-xs font-medium mb-5 ss-focus rounded" style={{ color: T.textMuted }}>
        <ArrowLeft size={14} /> Back to history
      </button>
      <Panel className="p-5 mb-5">
        <div className="grid sm:grid-cols-4 gap-4 text-xs">
          <div><p style={{ color: T.textFaint }}>SCAN ID</p><p className="ss-mono font-medium mt-0.5" style={{ color: T.text }}>{scan.id}</p></div>
          <div><p style={{ color: T.textFaint }}>DATE</p><p className="font-medium mt-0.5" style={{ color: T.text }}>{new Date(scan.date).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}</p></div>
          <div><p style={{ color: T.textFaint }}>TIME</p><p className="font-medium mt-0.5" style={{ color: T.text }}>{new Date(scan.date).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" })}</p></div>
          <div><p style={{ color: T.textFaint }}>SOURCE</p><p className="font-medium mt-0.5 capitalize" style={{ color: T.text }}>{scan.source}</p></div>
        </div>
      </Panel>
      <ResultView scan={scan} isReport />
      <div className="flex gap-3 mt-5 max-w-3xl mx-auto">
        <Btn variant="outline" icon={Download} disabled className="opacity-60 cursor-not-allowed" title="Available once backend export is implemented">
          Download report (coming soon)
        </Btn>
      </div>
    </AppShell>
  );
}

/* ============================================================================
   SETTINGS PAGE
============================================================================ */
function SettingsPage() {
  const { user, gmailConnected, setGmailConnected } = useApp();
  const [tab, setTab] = useState("account");
  const [prefs, setPrefs] = useState({ autoScan: true, strictMode: false, notifyHighRisk: true, notifyWeekly: false });
  const [showClearModal, setShowClearModal] = useState(false);
  const [toast, setToast] = useState("");

  useEffect(() => { if (toast) { const t = setTimeout(() => setToast(""), 2400); return () => clearTimeout(t); } }, [toast]);

  const tabs = [
    { id: "account", label: "Account", icon: User },
    { id: "detection", label: "Detection", icon: Shield },
    { id: "notifications", label: "Notifications", icon: BellRing },
    { id: "gmail", label: "Gmail Connection", icon: Inbox },
    { id: "privacy", label: "Privacy & Data", icon: Lock },
  ];

  function Toggle({ checked, onChange, label, desc }) {
    return (
      <div className="flex items-center justify-between gap-4 py-3.5" style={{ borderBottom: `1px solid ${T.border}` }}>
        <div>
          <p className="text-sm font-medium" style={{ color: T.text }}>{label}</p>
          {desc && <p className="text-xs mt-0.5" style={{ color: T.textMuted }}>{desc}</p>}
        </div>
        <button onClick={onChange} role="switch" aria-checked={checked} aria-label={label} className="ss-focus rounded-full flex-shrink-0" style={{ width: 40, height: 22, background: checked ? T.red : "rgba(255,255,255,0.12)", padding: 2, transition: "background 0.2s" }}>
          <span style={{ display: "block", width: 18, height: 18, borderRadius: "50%", background: "#fff", transform: checked ? "translateX(18px)" : "translateX(0)", transition: "transform 0.2s" }} />
        </button>
      </div>
    );
  }

  return (
    <AppShell title="Settings" subtitle="Manage your account, detection, and privacy preferences">
      <div className="grid lg:grid-cols-[200px_1fr] gap-6">
        <div className="flex lg:flex-col gap-1 overflow-x-auto ss-scroll pb-2 lg:pb-0">
          {tabs.map((t) => (
            <button key={t.id} onClick={() => setTab(t.id)} className="flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-sm font-medium whitespace-nowrap ss-focus flex-shrink-0"
              style={tab === t.id ? { background: T.redSoft, color: T.red, border: `1px solid ${T.redGlow}` } : { color: T.textMuted, border: `1px solid transparent` }}>
              <t.icon size={15} /> {t.label}
            </button>
          ))}
        </div>

        <Panel className="p-6">
          {tab === "account" && (
            <div className="max-w-md flex flex-col gap-4">
              <h3 className="font-semibold text-sm mb-1" style={{ color: T.text }}>Account details</h3>
              <Field label="Name"><input className={inputClass()} style={inputStyle} defaultValue={user?.name || "Demo Account"} /></Field>
              <Field label="Email"><input className={inputClass()} style={inputStyle} defaultValue={user?.email || "demo@scamshield.ai"} /></Field>
              <Btn className="w-fit" onClick={() => setToast("Account details saved.")}>Save changes</Btn>
            </div>
          )}
          {tab === "detection" && (
            <div>
              <h3 className="font-semibold text-sm mb-1" style={{ color: T.text }}>Detection preferences</h3>
              <p className="text-xs mb-2" style={{ color: T.textMuted }}>Tune how ScamShield evaluates incoming messages.</p>
              <Toggle checked={prefs.autoScan} onChange={() => setPrefs((p) => ({ ...p, autoScan: !p.autoScan }))} label="Auto-scan connected Gmail" desc="Automatically analyze new messages as they arrive." />
              <Toggle checked={prefs.strictMode} onChange={() => setPrefs((p) => ({ ...p, strictMode: !p.strictMode }))} label="Strict detection mode" desc="Flag borderline messages more aggressively. May increase false positives." />
            </div>
          )}
          {tab === "notifications" && (
            <div>
              <h3 className="font-semibold text-sm mb-1" style={{ color: T.text }}>Notifications</h3>
              <p className="text-xs mb-2" style={{ color: T.textMuted }}>Choose when ScamShield should alert you.</p>
              <Toggle checked={prefs.notifyHighRisk} onChange={() => setPrefs((p) => ({ ...p, notifyHighRisk: !p.notifyHighRisk }))} label="High-risk alerts" desc="Get notified immediately when a phishing or malicious message is detected." />
              <Toggle checked={prefs.notifyWeekly} onChange={() => setPrefs((p) => ({ ...p, notifyWeekly: !p.notifyWeekly }))} label="Weekly summary" desc="Receive a weekly digest of scan activity." />
            </div>
          )}
          {tab === "gmail" && (
            <div>
              <h3 className="font-semibold text-sm mb-3" style={{ color: T.text }}>Gmail connection</h3>
              {gmailConnected ? (
                <div className="flex items-center justify-between rounded-xl p-4" style={{ background: T.greenSoft, border: `1px solid ${T.greenGlow}` }}>
                  <div className="flex items-center gap-3">
                    <CircleCheck size={18} color={T.green} />
                    <div><p className="text-sm font-medium" style={{ color: T.text }}>Connected (demo mode)</p><p className="text-xs" style={{ color: T.textMuted }}>demo.user@gmail.com</p></div>
                  </div>
                  <Btn size="sm" variant="outline" onClick={() => setGmailConnected(false)}>Disconnect</Btn>
                </div>
              ) : (
                <div className="flex items-center justify-between rounded-xl p-4" style={{ background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}` }}>
                  <p className="text-sm" style={{ color: T.textMuted }}>Not connected</p>
                  <Btn size="sm" onClick={() => setGmailConnected(true)}>Connect Gmail</Btn>
                </div>
              )}
            </div>
          )}
          {tab === "privacy" && (
            <div>
              <h3 className="font-semibold text-sm mb-1" style={{ color: T.text }}>Privacy & data</h3>
              <p className="text-xs mb-4" style={{ color: T.textMuted }}>Scan history is stored for your account only, and never shared with third parties.</p>
              <div className="rounded-xl p-4 flex items-center justify-between" style={{ background: T.redSoft, border: `1px solid ${T.redGlow}` }}>
                <div>
                  <p className="text-sm font-medium" style={{ color: T.text }}>Clear scan history</p>
                  <p className="text-xs mt-0.5" style={{ color: T.textMuted }}>Permanently delete all stored scan records for this demo session.</p>
                </div>
                <Btn size="sm" variant="outline" icon={Trash2} onClick={() => setShowClearModal(true)}>Clear</Btn>
              </div>
            </div>
          )}
        </Panel>
      </div>

      {showClearModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-5" style={{ background: "rgba(0,0,0,0.7)" }} onClick={() => setShowClearModal(false)}>
          <div className="w-full max-w-sm rounded-2xl p-6 ss-fade-up" style={{ background: "#1a1d24", border: `1px solid ${T.borderBright}` }} onClick={(e) => e.stopPropagation()}>
            <TriangleAlert size={22} color={T.red} className="mb-3" />
            <h3 className="ss-display font-bold text-base mb-1.5" style={{ color: T.text }}>Clear all scan history?</h3>
            <p className="text-xs mb-5" style={{ color: T.textMuted }}>This cannot be undone. All scan records for this demo session will be permanently removed.</p>
            <div className="flex gap-3">
              <Btn variant="outline" className="flex-1" onClick={() => setShowClearModal(false)}>Cancel</Btn>
              <Btn className="flex-1" onClick={() => { setShowClearModal(false); setToast("Scan history cleared."); }}>Clear history</Btn>
            </div>
          </div>
        </div>
      )}

      {toast && (
        <div className="fixed bottom-6 right-6 z-50 rounded-xl px-4 py-3 flex items-center gap-2.5 ss-fade-up" style={{ background: "#1a1d24", border: `1px solid ${T.greenGlow}` }}>
          <CircleCheck size={16} color={T.green} />
          <span className="text-sm" style={{ color: T.text }}>{toast}</span>
        </div>
      )}
    </AppShell>
  );
}

/* ============================================================================
   ABOUT PAGE
============================================================================ */
function AboutPage() {
  const { user } = useApp();
  const Shell = user ? AppShell : PublicPageShell;
  const pipeline = [
    { label: "User Input", desc: "Email content submitted manually or via Gmail." },
    { label: "Preprocessing", desc: "Content is cleaned and normalized for analysis." },
    { label: "Feature Extraction", desc: "Sender, links, language, and structure are analyzed." },
    { label: "Threat Detection", desc: "Detection engine compares features to known threat patterns." },
    { label: "Risk Assessment", desc: "A risk score and confidence level are calculated." },
    { label: "Classification", desc: "The message is labeled safe, spam, phishing, or malicious." },
    { label: "Explanation", desc: "Plain-language reasoning is generated for the result." },
    { label: "Recommendation", desc: "A clear, actionable next step is provided." },
  ];
  return (
    <Shell title="About ScamShield AI" subtitle="Understanding how detection works">
      <div className="max-w-3xl flex flex-col gap-8">
        <Panel className="p-6">
          <h2 className="ss-display font-bold text-lg mb-2" style={{ color: T.text }}>What is ScamShield?</h2>
          <p className="text-sm leading-relaxed" style={{ color: T.textMuted }}>ScamShield AI is a security platform that analyzes suspicious emails and classifies them as safe, spam, phishing, or malicious — while explaining, in plain language, exactly why. Instead of a single label, you get a risk score, a confidence level, the specific indicators found, and a recommended next step.</p>
        </Panel>
        <Panel className="p-6">
          <h2 className="ss-display font-bold text-lg mb-4" style={{ color: T.text }}>How does it work?</h2>
          <div className="flex flex-col gap-0">
            {pipeline.map((p, i) => (
              <div key={p.label} className="flex gap-4">
                <div className="flex flex-col items-center flex-shrink-0">
                  <div className="w-7 h-7 rounded-full flex items-center justify-center text-[11px] font-bold ss-mono" style={{ background: T.redSoft, color: T.red, border: `1px solid ${T.redGlow}` }}>{i + 1}</div>
                  {i < pipeline.length - 1 && <div className="w-px flex-1 my-1" style={{ background: T.border, minHeight: 24 }} />}
                </div>
                <div className="pb-6">
                  <p className="text-sm font-semibold" style={{ color: T.text }}>{p.label}</p>
                  <p className="text-xs mt-0.5" style={{ color: T.textMuted }}>{p.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </Panel>
        <Panel className="p-6">
          <h2 className="ss-display font-bold text-lg mb-2" style={{ color: T.text }}>What threats can it detect?</h2>
          <p className="text-sm leading-relaxed" style={{ color: T.textMuted }}>ScamShield is designed to identify spam campaigns, phishing attempts that impersonate trusted organizations, and malicious messages carrying dangerous links or attachments — while distinguishing them from genuinely safe correspondence.</p>
        </Panel>
        <Panel className="p-6">
          <h2 className="ss-display font-bold text-lg mb-2" style={{ color: T.text }}>Why explainability matters</h2>
          <p className="text-sm leading-relaxed" style={{ color: T.textMuted }}>A label alone doesn't help you make a good decision. ScamShield always shows the specific evidence behind a result, so you can understand the threat — not just trust a black box.</p>
        </Panel>
        <Panel className="p-6">
          <h2 className="ss-display font-bold text-lg mb-2" style={{ color: T.text }}>How should I use the platform?</h2>
          <p className="text-sm leading-relaxed" style={{ color: T.textMuted }}>Use ScamShield as a second opinion before clicking links, downloading attachments, or entering credentials from an unfamiliar message. It's a decision aid, not a replacement for caution.</p>
        </Panel>
      </div>
    </Shell>
  );
}

/* ============================================================================
   FAQ PAGE
============================================================================ */
function FaqPage() {
  const { user } = useApp();
  const Shell = user ? AppShell : PublicPageShell;
  const [openIdx, setOpenIdx] = useState(0);
  return (
    <Shell title="Frequently asked questions" subtitle="Common questions about ScamShield AI">
      <div className="max-w-2xl flex flex-col gap-2.5">
        {FAQ_ITEMS.map((item, i) => (
          <Panel key={item.q} className="p-0 overflow-hidden">
            <button onClick={() => setOpenIdx(openIdx === i ? -1 : i)} className="w-full flex items-center justify-between gap-4 px-5 py-4 text-left ss-focus">
              <span className="text-sm font-medium" style={{ color: T.text }}>{item.q}</span>
              {openIdx === i ? <ChevronUp size={16} color={T.textMuted} className="flex-shrink-0" /> : <ChevronDown size={16} color={T.textMuted} className="flex-shrink-0" />}
            </button>
            {openIdx === i && <p className="px-5 pb-4 text-sm leading-relaxed" style={{ color: T.textMuted }}>{item.a}</p>}
          </Panel>
        ))}
      </div>
    </Shell>
  );
}

function PublicPageShell({ title, subtitle, children }) {
  return (
    <div className="ss-root ss-bg ss-grid min-h-screen">
      <PublicHeader />
      <div className="px-5 lg:px-10 py-12 lg:py-16">
        <div className="max-w-5xl mx-auto">
          <h1 className="ss-display font-bold text-2xl lg:text-3xl mb-2" style={{ color: T.text }}>{title}</h1>
          {subtitle && <p className="text-sm mb-10" style={{ color: T.textMuted }}>{subtitle}</p>}
          {children}
        </div>
      </div>
      <PublicFooter />
    </div>
  );
}

/* ============================================================================
   ROOT APP
============================================================================ */
export default function ScamShieldApp() {
  const [page, setPage] = useState("landing");
  const [user, setUser] = useState(null);
  const [scans, setScans] = useState(SCANS_SEED);
  const [inbox, setInbox] = useState(GMAIL_INBOX);
  const [gmailConnected, setGmailConnected] = useState(false);
  const [activeScanId, setActiveScanId] = useState(null);
  const [activeScanIdForAnalysis, setActiveScanIdForAnalysis] = useState(null);
  const scrollRef = useRef(null);

  function navigate(target, params = {}) {
    if (params.scanId) {
      if (target === "analysis") setActiveScanIdForAnalysis(params.scanId);
      setActiveScanId(params.scanId);
    }
    setPage(target);
    window?.scrollTo?.({ top: 0, behavior: "instant" });
  }

  function login(u) { setUser(u); }
  function logout() { setUser(null); setPage("landing"); }

  function addScan(data) {
    const id = `scan-${1100 + scans.length + Math.floor(Math.random() * 900)}`;
    const guess = guessClassification(data);
    const newScan = enrichScan({ id, date: new Date().toISOString(), source: data.source, ...data, ...guess });
    setScans((prev) => [newScan, ...prev]);
    return id;
  }

  const ctx = { page, navigate, user, login, logout, scans, addScan, gmailConnected, setGmailConnected, inbox, setInbox, activeScanId, setActiveScanId, activeScanIdForAnalysis };

  const protectedPages = ["dashboard", "scanner", "analysis", "history", "report", "settings"];
  useEffect(() => {
    if (!user && protectedPages.includes(page)) setPage("login");
  }, [user, page]);

  let content;
  switch (page) {
    case "landing": content = <LandingPage />; break;
    case "login": content = <LoginPage />; break;
    case "register": content = <RegisterPage />; break;
    case "about": content = <AboutPage />; break;
    case "faq": content = <FaqPage />; break;
    case "dashboard": content = <DashboardPage />; break;
    case "scanner": content = <ScannerPage />; break;
    case "analysis": content = <AnalysisPage />; break;
    case "history": content = <HistoryPage />; break;
    case "report": content = <ReportPage />; break;
    case "settings": content = <SettingsPage />; break;
    default: content = <LandingPage />;
  }

  return (
    <AppCtx.Provider value={ctx}>
      <GlobalStyle />
      <div className="ss-root">{content}</div>
    </AppCtx.Provider>
  );
}

/* Very small mock "classifier" so manually typed emails still produce a
   plausible result — this is presentational only and mimics detection engine
   output shape; NOT real threat intelligence. */
function guessClassification(data) {
  const text = `${data.sender} ${data.subject} ${data.body} ${data.url || ""}`.toLowerCase();
  const urgentWords = ["urgent", "immediately", "suspend", "verify", "expire", "final notice"];
  const credWords = ["password", "credential", "confirm your identity", "log in", "login", "ssn"];
  const spamWords = ["won", "prize", "free", "discount", "% off", "gift card", "survey"];
  const hasUrgent = urgentWords.some((w) => text.includes(w));
  const hasCred = credWords.some((w) => text.includes(w));
  const hasSpam = spamWords.some((w) => text.includes(w));
  const suspiciousDomain = /paypa1|secur[e3]-|verify-|-support\.|\.top|\.biz|\.info|1cloud|icloud-verify/.test(text);

  const indicators = [];
  if (suspiciousDomain) indicators.push({ id: "suspiciousSender", severity: "high" });
  if (hasUrgent) indicators.push({ id: "urgentLanguage", severity: "medium" });
  if (data.url && (suspiciousDomain || hasCred)) indicators.push({ id: "suspiciousUrl", severity: "high" });
  if (hasCred) indicators.push({ id: "credentialRequest", severity: "high" });
  if (hasSpam && !hasCred) indicators.push({ id: "unsolicitedOffer", severity: "medium" });

  let classification = "safe", risk = 6, confidence = 92, severity = "low";
  if (indicators.length >= 3) { classification = "phishing"; risk = 88 + Math.floor(Math.random() * 10); confidence = 92 + Math.floor(Math.random() * 7); severity = "high"; }
  else if (hasCred && suspiciousDomain) { classification = "phishing"; risk = 85; confidence = 90; severity = "high"; }
  else if (hasSpam && indicators.length <= 2) { classification = "spam"; risk = 40 + Math.floor(Math.random() * 20); confidence = 80 + Math.floor(Math.random() * 10); severity = "medium"; }
  else if (indicators.length === 0) { classification = "safe"; risk = 2 + Math.floor(Math.random() * 8); confidence = 93 + Math.floor(Math.random() * 6); severity = "low"; indicators.push({ id: "verifiedSender", severity: "info" }, { id: "noSuspiciousLinks", severity: "info" }); }
  else { classification = "spam"; risk = 35 + Math.floor(Math.random() * 15); confidence = 78; severity = "medium"; }

  const explanations = {
    safe: "This message shows no indicators commonly associated with spam, phishing, or malicious content based on sender reputation, link safety, and language patterns.",
    spam: "This message matches common bulk-marketing or unsolicited-offer patterns. It appears low-risk but unwanted rather than a targeted attack.",
    phishing: "This message contains characteristics commonly associated with phishing attempts, including sender anomalies, urgency, and requests that pressure quick action.",
    malicious: "This message shows strong indicators of malicious intent, including deceptive links or attachments designed to compromise your device or accounts.",
  };
  const actions = {
    safe: "No action needed. This message appears safe.",
    spam: "No urgent action needed. Mark as spam and avoid clicking any links.",
    phishing: "Do not click any links or provide credentials. Report this message and delete it.",
    malicious: "Do not open attachments or click links. Delete this message and report it to your IT or security team.",
  };

  return { classification, risk, confidence, severity, indicators, explanation: explanations[classification], recommendedAction: actions[classification] };
}