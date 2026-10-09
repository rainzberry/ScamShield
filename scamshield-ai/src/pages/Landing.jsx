import { useNavigate } from "react-router-dom";
import { ArrowRight, BadgeCheck, Fingerprint, Gauge, Inbox, QrCode, ScanLine, Sparkles } from "lucide-react";
import { T } from "../constants/theme";
import Button from "../components/common/Button";
import ClassBadge from "../components/common/ClassBadge";
import Panel from "../components/common/Panel";

const FEATURES = [
  { icon: Gauge, title: "Risk scoring", desc: "Every scan gets a 0-100 risk score and a confidence value, never a bare label." },
  { icon: Fingerprint, title: "Threat indicators", desc: "See which signals were detected: suspicious domains, urgency, credential requests and more." },
  { icon: BadgeCheck, title: "Explainable results", desc: "Each result shows the model and rule evidence behind the decision." },
  { icon: QrCode, title: "QR and URL analysis", desc: "Upload a QR image or paste a link. The content is analysed, never opened." },
];

const STEPS = [
  { n: "01", title: "Submit content", desc: "Scan an email, URL, text message or QR code image." },
  { n: "02", title: "Backend analysis", desc: "The Flask API passes your content to the detection engine and stores the scan." },
  { n: "03", title: "Understand the result", desc: "Get the classification, risk, confidence, evidence and recommended action." },
];

export default function Landing() {
  const navigate = useNavigate();
  return (
    <>
      <section className="px-5 lg:px-10 pt-16 lg:pt-24 pb-16">
        <div className="max-w-6xl mx-auto grid lg:grid-cols-2 gap-14 items-center">
          <div className="ss-fade-up">
            <span className="inline-flex items-center gap-2 text-xs font-semibold px-3 py-1.5 rounded-full mb-6" style={{ background: T.redSoft, color: T.red, border: `1px solid ${T.redGlow}` }}>
              <Sparkles size={12} aria-hidden="true" /> Explainable machine-learning detection
            </span>
            <h1 className="ss-display font-bold text-4xl lg:text-5xl leading-[1.08] mb-5" style={{ color: T.text }}>
              Know if a message is <span style={{ color: T.red, textShadow: `0 0 30px ${T.redGlow}` }}>dangerous</span> before you act on it.
            </h1>
            <p className="text-base leading-relaxed mb-8 max-w-lg" style={{ color: T.textMuted }}>
              ScamShield AI analyses emails, links, text and QR codes for phishing, spam, scams and malicious content, and explains every decision with evidence.
            </p>
            <div className="flex flex-wrap gap-3">
              <Button size="lg" icon={ScanLine} onClick={() => navigate("/register")}>Start scanning</Button>
              <Button size="lg" variant="outline" onClick={() => navigate("/about")}>How it works</Button>
            </div>
          </div>

          <div className="ss-fade-up">
            <Panel className="p-5" glow={T.redGlow}>
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-semibold" style={{ color: T.textMuted }}>ILLUSTRATIVE EXAMPLE</span>
                <ClassBadge classification="phishing" size="sm" />
              </div>
              <div className="rounded-xl p-4 mb-4 ss-mono text-xs leading-relaxed break-words" style={{ background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}`, color: T.textMuted }}>
                <p><span style={{ color: T.textFaint }}>From:</span> security@paypa1-support.example</p>
                <p><span style={{ color: T.textFaint }}>Subject:</span> URGENT: Verify your account</p>
              </div>
              <div className="flex flex-wrap gap-1.5 mb-4">
                {["Suspicious sender", "Urgent language", "Suspicious URL", "Credential request"].map((t) => (
                  <span key={t} className="text-[10px] px-2 py-1 rounded-md" style={{ background: T.redSoft, color: T.red, border: `1px solid ${T.redGlow}` }}>{t}</span>
                ))}
              </div>
              <p className="text-[11px]" style={{ color: T.textFaint }}>Static illustration of the kind of evidence shown. This is not a live scan. Real results come from the detection backend after you submit content.</p>
            </Panel>
          </div>
        </div>
      </section>

      <section className="px-5 lg:px-10 py-16">
        <div className="max-w-6xl mx-auto">
          <h2 className="ss-display font-bold text-2xl lg:text-3xl mb-2 text-center" style={{ color: T.text }}>Detection that explains itself</h2>
          <p className="text-sm text-center mb-12 max-w-xl mx-auto" style={{ color: T.textMuted }}>Every result goes beyond a label so you understand the threat, not just its name.</p>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {FEATURES.map((f) => (
              <Panel key={f.title} className="p-5">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-4" style={{ background: T.redSoft, border: `1px solid ${T.redGlow}` }}>
                  <f.icon size={18} color={T.red} aria-hidden="true" />
                </div>
                <h3 className="font-semibold text-sm mb-1.5" style={{ color: T.text }}>{f.title}</h3>
                <p className="text-xs leading-relaxed" style={{ color: T.textMuted }}>{f.desc}</p>
              </Panel>
            ))}
          </div>
        </div>
      </section>

      <section className="px-5 lg:px-10 py-16" style={{ borderTop: `1px solid ${T.border}` }}>
        <div className="max-w-5xl mx-auto">
          <h2 className="ss-display font-bold text-2xl lg:text-3xl mb-12 text-center" style={{ color: T.text }}>How it works</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {STEPS.map((s, i) => (
              <div key={s.n} className="relative">
                <span className="ss-display ss-mono font-bold text-4xl block mb-3" style={{ color: "rgba(255,59,82,0.25)" }}>{s.n}</span>
                <h3 className="font-semibold text-sm mb-2" style={{ color: T.text }}>{s.title}</h3>
                <p className="text-xs leading-relaxed" style={{ color: T.textMuted }}>{s.desc}</p>
                {i < STEPS.length - 1 && <ArrowRight className="hidden md:block absolute top-2 -right-9" size={16} color={T.textFaint} aria-hidden="true" />}
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="px-5 lg:px-10 py-16">
        <Panel className="max-w-4xl mx-auto p-10 text-center" glow={T.redGlow}>
          <Inbox size={22} color={T.red} className="mx-auto mb-3" aria-hidden="true" />
          <h2 className="ss-display font-bold text-2xl mb-3" style={{ color: T.text }}>Ready to check something suspicious?</h2>
          <p className="text-sm mb-7" style={{ color: T.textMuted }}>Create an account and run your first analysis in under a minute.</p>
          <Button size="lg" icon={ScanLine} onClick={() => navigate("/register")}>Create account</Button>
        </Panel>
      </section>
    </>
  );
}