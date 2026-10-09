import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { Sparkles } from "lucide-react";
import { T } from "../constants/theme";
import { useAuth } from "../context/AuthContext";
import Button from "../components/common/Button";
import Field from "../components/common/Field";
import { InlineAlert } from "../components/common/StateViews";
import AuthShell from "../components/layout/AuthShell";

export default function Register() {
  const { register, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "", confirm: "" });
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState("");
  const [loading, setLoading] = useState(false);

  if (isAuthenticated) return <Navigate to="/dashboard" replace />;
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    const errs = {};
    if (!form.name.trim()) errs.name = "Name is required.";
    if (!form.email.trim()) errs.email = "Email is required.";
    else if (!/^\S+@\S+\.\S+$/.test(form.email.trim())) errs.email = "Enter a valid email address.";
    if (!form.password) errs.password = "Password is required.";
    else if (form.password.length < 8) errs.password = "Use at least 8 characters.";
    if (form.confirm !== form.password) errs.confirm = "Passwords do not match.";
    setErrors(errs);
    setApiError("");
    if (Object.keys(errs).length) return;
    setLoading(true);
    try {
      await register({ name: form.name.trim(), email: form.email.trim(), password: form.password });
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setApiError(err.userMessage || "Registration failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthShell
      title="Create your account"
      subtitle="Start analysing suspicious content in minutes."
      footer={<p className="text-xs text-center mt-6" style={{ color: T.textMuted }}>Already have an account? <Link to="/login" className="font-semibold ss-focus rounded" style={{ color: T.red }}>Log in</Link></p>}
    >
      {apiError && <InlineAlert tone="error" className="mb-4">{apiError}</InlineAlert>}
      <form onSubmit={submit} className="flex flex-col gap-4" noValidate>
        <Field label="Name" error={errors.name}>
          <input autoComplete="name" className="ss-input" placeholder="Jane Doe" value={form.name} onChange={set("name")} aria-invalid={Boolean(errors.name)} />
        </Field>
        <Field label="Email" error={errors.email}>
          <input type="email" autoComplete="email" className="ss-input" placeholder="you@example.com" value={form.email} onChange={set("email")} aria-invalid={Boolean(errors.email)} />
        </Field>
        <Field label="Password" hint="At least 8 characters." error={errors.password}>
          <input type="password" autoComplete="new-password" className="ss-input" value={form.password} onChange={set("password")} aria-invalid={Boolean(errors.password)} />
        </Field>
        <Field label="Confirm password" error={errors.confirm}>
          <input type="password" autoComplete="new-password" className="ss-input" value={form.confirm} onChange={set("confirm")} aria-invalid={Boolean(errors.confirm)} />
        </Field>
        <Button type="submit" className="w-full mt-1" icon={Sparkles} loading={loading}>{loading ? "Creating account..." : "Create account"}</Button>
      </form>
    </AuthShell>
  );
}