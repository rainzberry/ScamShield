import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { T } from "../../constants/theme";
import ChartTooltip from "./ChartTooltip";

export default function ActivityChart({ data }) {
  return (
    <div className="h-56" role="img" aria-label="Scan activity over time line chart">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ left: -20, right: 8, top: 5 }}>
          <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
          <XAxis dataKey="date" tick={{ fill: T.textFaint, fontSize: 10 }} axisLine={{ stroke: T.border }} tickLine={false} />
          <YAxis tick={{ fill: T.textFaint, fontSize: 10 }} axisLine={false} tickLine={false} allowDecimals={false} />
          <Tooltip content={<ChartTooltip />} />
          <Legend wrapperStyle={{ fontSize: 11, color: T.textMuted }} />
          <Line type="monotone" dataKey="scans" name="Scans" stroke="#8b93a3" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="threats" name="Threats" stroke={T.red} strokeWidth={2.5} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}