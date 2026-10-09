import { T } from "../../constants/theme";

export default function PageHeader({ title, subtitle, actions }) {
  return (
    <div className="flex flex-wrap items-start justify-between gap-4 mb-6">
      <div className="min-w-0">
        <h1 className="ss-display font-bold text-xl lg:text-2xl" style={{ color: T.text }}>{title}</h1>
        {subtitle && <p className="text-sm mt-1" style={{ color: T.textMuted }}>{subtitle}</p>}
      </div>
      {actions && <div className="flex flex-wrap gap-2 no-print">{actions}</div>}
    </div>
  );
}