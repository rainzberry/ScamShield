import { useEffect, useRef, useState } from "react";
import { ScanLine, Upload, X } from "lucide-react";
import { T } from "../../constants/theme";
import Button from "../common/Button";
import { InlineAlert } from "../common/StateViews";

const ACCEPTED = ["image/png", "image/jpeg", "image/webp"];
const MAX_MB = 5;

export default function QrForm({ onSubmit, disabled }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [error, setError] = useState("");
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef(null);

  useEffect(() => {
    if (!file) { setPreview(null); return undefined; }
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  function choose(f) {
    setError("");
    if (!f) return;
    if (!ACCEPTED.includes(f.type)) { setFile(null); return setError("Unsupported format. Upload a PNG, JPG or WebP image."); }
    if (f.size === 0) { setFile(null); return setError("The selected file is empty."); }
    if (f.size > MAX_MB * 1024 * 1024) { setFile(null); return setError(`File is too large. Maximum size is ${MAX_MB} MB.`); }
    setFile(f);
  }

  function submit(e) {
    e.preventDefault();
    if (!file) return setError("Select a QR code image first.");
    onSubmit("qr", { file });
  }

  return (
    <form onSubmit={submit} className="flex flex-col gap-4">
      <div
        role="button" tabIndex={0}
        aria-label="Choose a QR code image to upload"
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); inputRef.current?.click(); } }}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => { e.preventDefault(); setDragging(false); choose(e.dataTransfer.files?.[0]); }}
        className="rounded-xl p-8 text-center cursor-pointer ss-focus transition-colors"
        style={{ border: `2px dashed ${dragging ? T.red : T.borderBright}`, background: dragging ? T.redSoft : "rgba(255,255,255,0.02)" }}
      >
        <Upload size={26} color={T.textMuted} className="mx-auto mb-3" aria-hidden="true" />
        <p className="text-sm font-medium" style={{ color: T.text }}>Drop a QR code image here, or click to browse</p>
        <p className="text-xs mt-1" style={{ color: T.textFaint }}>PNG, JPG or WebP, up to {MAX_MB} MB</p>
        <input ref={inputRef} type="file" accept={ACCEPTED.join(",")} className="hidden" aria-label="QR code image file" onChange={(e) => { choose(e.target.files?.[0]); e.target.value = ""; }} />
      </div>

      {error && <InlineAlert tone="error">{error}</InlineAlert>}

      {file && preview && (
        <div className="flex items-center gap-4 rounded-xl p-3" style={{ background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}` }}>
          <img src={preview} alt="Selected QR code preview" className="w-20 h-20 object-contain rounded-lg bg-white p-1" />
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium truncate" style={{ color: T.text }}>{file.name}</p>
            <p className="text-xs" style={{ color: T.textMuted }}>{(file.size / 1024).toFixed(1)} KB</p>
          </div>
          <button type="button" onClick={() => setFile(null)} className="p-2 rounded-lg ss-focus" style={{ color: T.textMuted }} aria-label="Remove selected image"><X size={16} /></button>
        </div>
      )}

      <InlineAlert tone="info">The image is decoded on the server. The decoded content is analysed but never opened or executed.</InlineAlert>
      <Button type="submit" size="lg" icon={ScanLine} disabled={disabled || !file} className="w-full sm:w-fit">Analyze QR code</Button>
    </form>
  );
}