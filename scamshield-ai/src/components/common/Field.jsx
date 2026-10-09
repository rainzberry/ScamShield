import { T } from "../../constants/theme";

/* Wraps one input with a visible label, optional hint and an accessible error message.
   Put aria-invalid on the input yourself: aria-invalid={Boolean(error)} */
export default function Field({ label, hint, error, children }) {
  return (
    <label className="block">
      <span className="block text-xs font-medium mb-1.5" style={{ color: T.textMuted }}>{label}</span>
      {children}
      {hint && !error && <span className="block text-[11px] mt-1" style={{ color: T.textFaint }}>{hint}</span>}
      {error && <span role="alert" className="block text-[11px] mt-1" style={{ color: T.red }}>{error}</span>}
    </label>
  );
}