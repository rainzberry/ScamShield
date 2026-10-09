import { Shield } from "lucide-react";
import { T } from "../../constants/theme";

export default function Logo({ size = 36, showTagline = false }) {
  return (
    <span className="inline-flex items-center gap-2.5">
      <span
        className="rounded-xl flex items-center justify-center"
        style={{ width: size, height: size, background: "rgba(255,59,82,0.12)", border: `1px solid ${T.redGlow}` }}
      >
        <Shield size={size * 0.52} color={T.red} style={{ filter: `drop-shadow(0 0 5px ${T.redGlow})` }} aria-hidden="true" />
      </span>
      <span className="text-left">
        <span className="ss-display font-bold text-sm leading-none block" style={{ color: T.text }}>ScamShield AI</span>
        {showTagline && <span className="text-[10px] tracking-widest block mt-0.5" style={{ color: T.textFaint }}>AI SECURITY</span>}
      </span>
    </span>
  );
}