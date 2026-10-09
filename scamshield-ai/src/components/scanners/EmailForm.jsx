import { useState } from "react";
import { ScanLine, Sparkles } from "lucide-react";
import { T } from "../../constants/theme";
import { isValidUrl } from "../../utils/validators";
import Button from "../common/Button";
import Field from "../common/Field";

const EMPTY = { sender: "", subject: "", body: "", url: "" };
// A sample INPUT only. The result still comes from the backend.
const SAMPLE = {
  sender: "security@paypa1-support.example",
  subject: "URGENT: Your account requires immediate verification",
  body: "Your account will be suspended unless you verify your information immediately. Click the link below to confirm your identity.",
  url: "https://paypa1-support.example/verify",
};

export default function EmailForm({ onSubmit, disabled }) {
  const [form, setForm] = useState(EMPTY);
  const [errors, setErrors] = useState({});
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  function submit(e) {
    e.preventDefault();
    const errs = {};
    if (!form.sender.trim()) errs.sender = "Sender is required.";
    if (!form.subject.trim()) errs.subject = "Subject is required.";
    if (!form.body.trim()) errs.body = "Email body is required.";
    if (form.url.trim() && !isValidUrl(form.url.trim())) errs.url = "Enter a full URL starting with http:// or https://";
    setErrors(errs);
    if (Object.keys(errs).length) return;
    const payload = { sender: form.sender.trim(), subject: form.subject.trim(), body: form.body.trim() };
    if (form.url.trim()) payload.url = form.url.trim();
    onSubmit("email", payload);
  }

  return (
    <form onSubmit={submit} className="flex flex-col gap-4" noValidate>
      <div className="flex justify-end">
        <button type="button" onClick={() => setForm(SAMPLE)} className="text-xs font-semibold flex items-center gap-1.5 ss-focus rounded" style={{ color: T.red }}>
          <Sparkles size={13} aria-hidden="true" /> Fill with sample input
        </button>
      </div>
      <Field label="Sender" error={errors.sender}>
        <input className="ss-input" placeholder="sender@example.com" value={form.sender} onChange={set("sender")} aria-invalid={Boolean(errors.sender)} />
      </Field>
      <Field label="Subject" error={errors.subject}>
        <input className="ss-input" placeholder="Email subject line" value={form.subject} onChange={set("subject")} aria-invalid={Boolean(errors.subject)} />
      </Field>
      <Field label="Body" error={errors.body}>
        <textarea rows={6} className="ss-input" placeholder="Paste the email content here..." value={form.body} onChange={set("body")} aria-invalid={Boolean(errors.body)} />
      </Field>
      <Field label="URL (optional)" hint="Any link from the email. It is analysed, never opened." error={errors.url}>
        <input className="ss-input" placeholder="https://..." value={form.url} onChange={set("url")} aria-invalid={Boolean(errors.url)} />
      </Field>
      <Button type="submit" size="lg" icon={ScanLine} disabled={disabled} className="w-full sm:w-fit">Analyze email</Button>
    </form>
  );
}