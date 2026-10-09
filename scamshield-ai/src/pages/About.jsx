import { ABOUT_TOPICS, PIPELINE } from "../constants/content";
import { T } from "../constants/theme";
import PageHeader from "../components/common/PageHeader";
import Panel from "../components/common/Panel";

export default function About() {
  return (
    <div className="max-w-3xl">
      <PageHeader title="About ScamShield AI" subtitle="Understanding how detection and explanations work" />

      <Panel className="p-6 mb-5">
        <h2 className="ss-display font-bold text-lg mb-4" style={{ color: T.text }}>How a scan flows through the system</h2>
        <ol>
          {PIPELINE.map((p, i) => (
            <li key={p.label} className="flex gap-4">
              <div className="flex flex-col items-center flex-shrink-0">
                <div className="w-7 h-7 rounded-full flex items-center justify-center text-[11px] font-bold ss-mono" style={{ background: T.redSoft, color: T.red, border: `1px solid ${T.redGlow}` }}>{i + 1}</div>
                {i < PIPELINE.length - 1 && <div className="w-px flex-1 my-1" style={{ background: T.border, minHeight: 24 }} />}
              </div>
              <div className="pb-5">
                <p className="text-sm font-semibold" style={{ color: T.text }}>{p.label}</p>
                <p className="text-xs mt-0.5" style={{ color: T.textMuted }}>{p.desc}</p>
              </div>
            </li>
          ))}
        </ol>
      </Panel>

      <div className="flex flex-col gap-5">
        {ABOUT_TOPICS.map((t) => (
          <Panel key={t.title} className="p-6">
            <h2 className="ss-display font-bold text-base mb-2" style={{ color: T.text }}>{t.title}</h2>
            <p className="text-sm leading-relaxed" style={{ color: T.textMuted }}>{t.body}</p>
          </Panel>
        ))}
      </div>
    </div>
  );
}