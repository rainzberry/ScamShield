import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import { FAQ_ITEMS } from "../constants/content";
import { T } from "../constants/theme";
import PageHeader from "../components/common/PageHeader";
import Panel from "../components/common/Panel";

export default function FAQ() {
  const [openIdx, setOpenIdx] = useState(0);
  return (
    <div className="max-w-2xl">
      <PageHeader title="Frequently asked questions" subtitle="Common questions about ScamShield AI" />
      <div className="flex flex-col gap-2.5">
        {FAQ_ITEMS.map((item, i) => {
          const open = openIdx === i;
          return (
            <Panel key={item.q} className="overflow-hidden">
              <h2>
                <button onClick={() => setOpenIdx(open ? -1 : i)} aria-expanded={open} aria-controls={`faq-${i}`}
                  className="w-full flex items-center justify-between gap-4 px-5 py-4 text-left ss-focus">
                  <span className="text-sm font-medium" style={{ color: T.text }}>{item.q}</span>
                  {open ? <ChevronUp size={16} color={T.textMuted} aria-hidden="true" /> : <ChevronDown size={16} color={T.textMuted} aria-hidden="true" />}
                </button>
              </h2>
              {open && <p id={`faq-${i}`} className="px-5 pb-4 text-sm leading-relaxed" style={{ color: T.textMuted }}>{item.a}</p>}
            </Panel>
          );
        })}
      </div>
    </div>
  );
}