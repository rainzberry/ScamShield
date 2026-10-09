import { useState } from "react";
import { ScanLine } from "lucide-react";
import { T } from "../../constants/theme";
import Button from "../common/Button";
import Field from "../common/Field";

const MAX = 10000;

export default function TextForm({ onSubmit, disabled }) {
  const [content, setContent] = useState("");
  const [error, setError] = useState("");

  function submit(e) {
    e.preventDefault();
    const value = content.trim();
    if (!value) return setError("Enter the text you want to analyze.");
    if (value.length < 10) return setError("Text is too short to analyze. Enter at least 10 characters.");
    if (value.length > MAX) return setError(`Text is too long. Maximum is ${MAX} characters.`);
    setError("");
    onSubmit("text", { content: value });
  }

  return (
    <form onSubmit={submit} className="flex flex-col gap-4" noValidate>
      <Field label="Message or text content" error={error}>
        <textarea rows={8} className="ss-input" placeholder="Paste an SMS, chat message or any suspicious text..." value={content} onChange={(e) => setContent(e.target.value)} aria-invalid={Boolean(error)} />
      </Field>
      <p className="text-[11px] text-right ss-mono" style={{ color: content.length > MAX ? T.red : T.textFaint }}>{content.length} / {MAX}</p>
      <Button type="submit" size="lg" icon={ScanLine} disabled={disabled} className="w-full sm:w-fit">Analyze text</Button>
    </form>
  );
}