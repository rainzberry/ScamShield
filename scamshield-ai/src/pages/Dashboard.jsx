import { Link, useNavigate } from "react-router-dom";
import { Gauge, ScanLine, ShieldAlert, ShieldCheck, ShieldX, MailWarning, ChevronRight } from "lucide-react";
import { getDashboardStats } from "../api/dashboardApi";
import { getClassStyle, T } from "../constants/theme";
import useFetch from "../hooks/useFetch";
import ActivityChart from "../components/charts/ActivityChart";
import DistributionChart from "../components/charts/DistributionChart";
import SeverityChart from "../components/charts/SeverityChart";
import Button from "../components/common/Button";
import PageHeader from "../components/common/PageHeader";
import Panel from "../components/common/Panel";
import { EmptyState, ErrorState, LoadingState } from "../components/common/StateViews";
import ScanTable from "../components/history/ScanTable";

function StatCard({ icon: Icon, label, value, color, soft, ring }) {
  return (
    <Panel className="p-5">
      <div className="w-9 h-9 rounded-lg flex items-center justify-center mb-3" style={{ background: soft, border: `1px solid ${ring}` }}>
        <Icon size={16} color={color} aria-hidden="true" />
      </div>
      <p className="ss-mono ss-display font-bold text-2xl lg:text-3xl" style={{ color: T.text }}>{value}</p>
      <p className="text-xs mt-1" style={{ color: T.textMuted }}>{label}</p>
    </Panel>
  );
}

export default function Dashboard() {
  const navigate = useNavigate();
  const { data: stats, loading, error, reload } = useFetch(getDashboardStats, []);

  const action = <Button icon={ScanLine} onClick={() => navigate("/scanner")}>New scan</Button>;

  if (loading) return <><PageHeader title="Dashboard" subtitle="Your security overview" /><LoadingState label="Loading dashboard..." /></>;
  if (error) return <><PageHeader title="Dashboard" subtitle="Your security overview" /><ErrorState title="Could not load dashboard" message={error} onRetry={reload} /></>;

  if (stats.total === 0) {
    return (
      <>
        <PageHeader title="Dashboard" subtitle="Your security overview" actions={action} />
        <Panel>
          <EmptyState icon={ScanLine} title="No scans yet" description="Run your first analysis and your statistics, charts and recent activity will appear here." action={action} />
        </Panel>
      </>
    );
  }

  const c = stats.counts;
  const cards = [
    { icon: ScanLine, label: "Total scans", value: stats.total, color: T.text, soft: "rgba(255,255,255,0.06)", ring: T.border },
    { icon: ShieldCheck, label: "Safe", value: c.safe, ...pick("safe") },
    { icon: MailWarning, label: "Spam", value: c.spam, ...pick("spam") },
    { icon: ShieldAlert, label: "Phishing", value: c.phishing, ...pick("phishing") },
    { icon: ShieldX, label: "Malicious", value: c.malicious, ...pick("malicious") },
    { icon: Gauge, label: "Average risk", value: stats.averageRisk === null ? "—" : `${Math.round(stats.averageRisk)}/100`, color: T.amber, soft: T.amberSoft, ring: T.amberGlow },
  ];

  return (
    <>
      <PageHeader title="Dashboard" subtitle="Real statistics from your stored scans" actions={action} />

      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-6">
        {cards.map((card) => <StatCard key={card.label} {...card} />)}
      </div>

      <div className="grid lg:grid-cols-3 gap-4 mb-6">
        <Panel className="lg:col-span-2 p-5">
          <h2 className="font-semibold text-sm mb-4" style={{ color: T.text }}>{stats.activity.length ? "Scan activity over time" : "Severity distribution"}</h2>
          {stats.activity.length
            ? <ActivityChart data={stats.activity} />
            : stats.severity.length
              ? <SeverityChart data={stats.severity} />
              : <p className="text-sm py-10 text-center" style={{ color: T.textMuted }}>The backend did not provide activity or severity data.</p>}
        </Panel>
        <Panel className="p-5">
          <h2 className="font-semibold text-sm mb-4" style={{ color: T.text }}>Classification distribution</h2>
          <DistributionChart counts={c} />
        </Panel>
      </div>

      {stats.activity.length > 0 && stats.severity.length > 0 && (
        <Panel className="p-5 mb-6">
          <h2 className="font-semibold text-sm mb-4" style={{ color: T.text }}>Severity distribution</h2>
          <SeverityChart data={stats.severity} />
        </Panel>
      )}

      <Panel className="p-5">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-sm" style={{ color: T.text }}>Recent scans</h2>
          <Link to="/history" className="text-xs font-semibold ss-focus rounded flex items-center gap-1" style={{ color: T.red }}>View all <ChevronRight size={13} aria-hidden="true" /></Link>
        </div>
        <ScanTable scans={stats.recent} emptyTitle="No recent scans" emptyDescription="The backend did not return recent scans." />
      </Panel>
    </>
  );

  function pick(key) {
    const s = getClassStyle(key);
    return { color: s.text, soft: s.soft, ring: s.ring };
  }
}