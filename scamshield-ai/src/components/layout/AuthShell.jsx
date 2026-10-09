import { Link } from "react-router-dom";
import { T } from "../../constants/theme";
import Logo from "../common/Logo";
import Panel from "../common/Panel";

export default function AuthShell({ title, subtitle, children, footer }) {
  return (
    <div className="ss-bg ss-grid min-h-screen flex flex-col">
      <div className="px-5 py-5">
        <Link to="/" className="ss-focus rounded-lg inline-block" aria-label="ScamShield AI home"><Logo size={32} /></Link>
      </div>
      <main className="flex-1 flex items-center justify-center px-5 py-10">
        <Panel className="w-full max-w-md p-7 lg:p-8 ss-fade-up">
          <h1 className="ss-display font-bold text-xl mb-1.5" style={{ color: T.text }}>{title}</h1>
          <p className="text-sm mb-6" style={{ color: T.textMuted }}>{subtitle}</p>
          {children}
          {footer}
        </Panel>
      </main>
    </div>
  );
}