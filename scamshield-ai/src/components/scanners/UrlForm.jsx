import { useState } from "react";
import { ScanLine } from "lucide-react";
import { isValidUrl } from "../../utils/validators";
import Button from "../common/Button";
import Field from "../common/Field";

export default function UrlForm({ onSubmit, disabled }) {
  const [url, setUrl] = useState("");
  const [error, setError] = useState("");

  function submit(e) {
    e.preventDefault();
    const value = url.trim();
    if (!value) return setError("URL is required.");
    if (!isValidUrl(value)) return setError("Enter a full URL starting with http:// or https://");
    setError("");
    onSubmit("url", { url: value });
  }

  return (
    <form onSubmit={submit} className="flex flex-col gap-4" noValidate>
      <Field label="URL to analyze" hint="The URL is sent to the backend for analysis. ScamShield never opens it." error={error}>
        <input className="ss-input" placeholder="https://example.com/login" value={url} onChange={(e) => setUrl(e.target.value)} aria-invalid={Boolean(error)} />
      </Field>
      <Button type="submit" size="lg" icon={ScanLine} disabled={disabled} className="w-full sm:w-fit">Analyze URL</Button>
    </form>
  );
}