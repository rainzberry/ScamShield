import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { severityColor, T } from "../../constants/theme";
import { titleCase } from "../../utils/format";
import ChartTooltip from "./ChartTooltip";

export default function SeverityChart({ data }) {
  const rows = data.map((d) => ({ name: titleCase(d.key), value: d.value, color: severityColor(d.key) }));
  return (
    <div className="h-56" role="img" aria-label="Severity distribution bar chart">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={rows} margin={{ left: -20, right: 8, top: 5 }}>
          <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
          <XAxis dataKey="name" tick={{ fill: T.textFaint, fontSize: 11 }} axisLine={{ stroke: T.border }} tickLine={false} />
          <YAxis tick={{ fill: T.textFaint, fontSize: 10 }} axisLine={false} tickLine={false} allowDecimals={false} />
          <Tooltip content={<ChartTooltip />} cursor={{ fill: "rgba(255,255,255,0.04)" }} />
          <Bar dataKey="value" name="Scans" radius={[6, 6, 0, 0]}>
            {rows.map((r) => <Cell key={r.name} fill={r.color} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}