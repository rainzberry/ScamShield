import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { CLASSIFICATIONS, getClassStyle, T } from "../../constants/theme";
import ChartTooltip from "./ChartTooltip";

export default function DistributionChart({ counts }) {
  const data = CLASSIFICATIONS.map((k) => ({
    key: k, name: getClassStyle(k).label, value: counts[k] || 0, color: getClassStyle(k).text,
  }));
  const visible = data.filter((d) => d.value > 0);
  return (
    <div>
      <div className="h-44" role="img" aria-label="Classification distribution chart">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={visible} dataKey="value" nameKey="name" innerRadius={46} outerRadius={68} paddingAngle={3} stroke="none">
              {visible.map((d) => <Cell key={d.key} fill={d.color} />)}
            </Pie>
            <Tooltip content={<ChartTooltip />} />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <ul className="grid grid-cols-2 gap-2 mt-2">
        {data.map((d) => (
          <li key={d.key} className="flex items-center gap-1.5 text-[11px]">
            <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: d.color }} aria-hidden="true" />
            <span style={{ color: T.textMuted }}>{d.name}</span>
            <span className="ss-mono ml-auto" style={{ color: T.text }}>{d.value}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}