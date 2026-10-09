import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { Eye, EyeOff, Lock } from "lucide-react";
import { T } from "../constants/theme";
import { useAuth } from "../context/AuthContext";
import Button from "../components/common/Button";
import Field from "../components/common/Field";
import { InlineAlert } from "../components/common/StateViews";
import AuthShell from "../components/layout/AuthShell";

export default function Login() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ email: "", password: "" });
  const [showPw, setShowPw] = useState(false);
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState("");
  const [loading, setLoading] = useState(false);

  if (isAuthenticated) return <Navigate to="/dashboard" replace />;

  async function submit(e) {
    e.preventDefault();
    const errs = {};
    if (!form.email.trim()) errs.email = "Email is required.";
    if (!form.password) errs.password = "Password is required.";
    setErrors(errs);
    setApiError("");
    if (Object.keys(errs).length) return;
    setLoading(true);
    try {
      await login(form.email.trim(), form.password);
      navigate(location.state?.from || "/dashboard", { replace: true });
    } catch (err) {
      setApiError(err.userMessage || "Login failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthShell
      title="Welcome back"
      subtitle="Log in to your ScamShield AI account."
      footer={<p className="text-xs text-center mt-6" style={{ color: T.textMuted }}>Don't have an account? <Link to="/register" className="font-semibold ss-focus rounded" style={{ color: T.red }}>Create one</Link></p>}
    >
      {location.state?.expired && <InlineAlert tone="warning" className="mb-4">Session expired. Please log in again.</InlineAlert>}
      {apiError && <InlineAlert tone="error" className="mb-4">{apiError}</InlineAlert>}
      <form onSubmit={submit} className="flex flex-col gap-4" noValidate>
        <Field label="Email" error={errors.email}>
          <input type="email" autoComplete="email" className="ss-input" placeholder="you@example.com" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} aria-invalid={Boolean(errors.email)} />
        </Field>
        <Field label="Password" error={errors.password}>
          <div className="relative">
            <input type={showPw ? "text" : "password"} autoComplete="current-password" className="ss-input pr-10" placeholder="Your password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} aria-invalid={Boolean(errors.password)} />
            <button type="button" onClick={() => setShowPw((s) => !s)} className="absolute right-3 top-1/2 -translate-y-1/2 ss-focus rounded" style={{ color: T.textFaint }} aria-label={showPw ? "Hide password" : "Show password"}>
              {showPw ? <EyeOff size={15} /> : <Eye size={15} />}
            </button>
          </div>
        </Field>
        <Button type="submit" className="w-full mt-1" icon={Lock} loading={loading}>{loading ? "Logging in..." : "Log in"}</Button>
      </form>
    </AuthShell>
  );
}