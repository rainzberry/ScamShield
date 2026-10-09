export default function Panel({ children, className = "", glow, style = {}, ...props }) {
  return (
    <div
      className={`ss-panel rounded-2xl ${className}`}
      style={{ ...(glow ? { boxShadow: `0 0 0 1px ${glow}, 0 8px 32px -8px ${glow}` } : {}), ...style }}
      {...props}
    >
      {children}
    </div>
  );
}