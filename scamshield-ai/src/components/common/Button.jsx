import { Loader2 } from "lucide-react";

const SIZES = {
  sm: "text-xs px-3 py-1.5 gap-1.5",
  md: "text-sm px-4 py-2.5 gap-2",
  lg: "text-sm px-6 py-3.5 gap-2",
};

export default function Button({
  children, variant = "primary", size = "md", icon: Icon, loading = false,
  className = "", disabled, type = "button", ...props
}) {
  return (
    <button
      type={type}
      className={`ss-btn ss-btn-${variant} ${SIZES[size]} ${className}`}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      {...props}
    >
      {loading ? <Loader2 size={16} className="animate-spin" aria-hidden="true" /> : Icon ? <Icon size={16} strokeWidth={2} aria-hidden="true" /> : null}
      {children}
    </button>
  );
}