import { ChevronLeft, ChevronRight } from "lucide-react";
import { T } from "../../constants/theme";
import Button from "../common/Button";

export default function Pagination({ page, pages, total, onChange }) {
  if (pages <= 1) {
    return <p className="text-xs mt-4" style={{ color: T.textFaint }}>{total} {total === 1 ? "result" : "results"}</p>;
  }
  return (
    <nav className="flex items-center justify-between gap-3 mt-5" aria-label="Pagination">
      <p className="text-xs" style={{ color: T.textFaint }}>{total} results</p>
      <div className="flex items-center gap-3">
        <Button variant="outline" size="sm" icon={ChevronLeft} disabled={page <= 1} onClick={() => onChange(page - 1)} aria-label="Previous page">Prev</Button>
        <span className="text-xs ss-mono" style={{ color: T.textMuted }} aria-live="polite">Page {page} of {pages}</span>
        <Button variant="outline" size="sm" disabled={page >= pages} onClick={() => onChange(page + 1)} aria-label="Next page">
          Next <ChevronRight size={14} aria-hidden="true" />
        </Button>
      </div>
    </nav>
  );
}