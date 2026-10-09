from __future__ import annotations

import re
import unicodedata
from html.parser import HTMLParser
from typing import List, Tuple

from ..configs.settings import MAX_TEXT_CHARS

_ZW = re.compile(r"[\u200b-\u200f\u202a-\u202e\u2060\ufeff]")
_URL_RE = re.compile(r"(?i)\b(?:https?://|ftp://|www\.)[^\s<>\"'`]+")
_EMAIL_RE = re.compile(r"(?i)\b[\w.+\-]+@[\w\-]+(?:\.[\w\-]+)+\b")
_HTML_HINT = re.compile(r"(?i)<\s*(?:html|body|div|p|a|table|br|span|img|head|style|font)\b")
_TRAIL = ".,;:!?)]}>'\""


class _Extractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: List[str] = []
        self.hrefs: List[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
        elif tag == "a":
            for k, v in attrs:
                if k == "href" and v:
                    self.hrefs.append(v)
        elif tag in ("br", "p", "div", "tr", "li"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


def looks_like_html(text: str) -> bool:
    return bool(_HTML_HINT.search(text[:20000]))


def html_to_text(text: str) -> Tuple[str, List[str]]:
    try:
        p = _Extractor()
        p.feed(text)
        p.close()
        return "".join(p.parts), p.hrefs
    except Exception:
        return re.sub(r"<[^>]+>", " ", text), []


def extract_urls(text: str, max_urls: int = 20) -> List[str]:
    if not isinstance(text, str) or not text:
        return []
    hrefs: List[str] = []
    if looks_like_html(text):
        hrefs = html_to_text(text[:200000])[1]
    cands = hrefs + _URL_RE.findall(text[:200000])
    seen, out = set(), []
    for c in cands:
        c = c.strip().rstrip(_TRAIL)
        if c.lower().startswith(("http://", "https://", "ftp://", "www.")) and c not in seen:
            seen.add(c)
            out.append(c)
        if len(out) >= max_urls:
            break
    return out


def compose_email_text(subject: str, body: str) -> str:
    return f"{subject or ''}\n\n{body or ''}"


def clean_text(text, max_chars: int = MAX_TEXT_CHARS) -> str:
    """Shared by training and inference. URLs/emails become tokens; HTML is stripped."""
    if not isinstance(text, str):
        return ""
    t = unicodedata.normalize("NFKC", text[: max_chars * 3])
    t = _ZW.sub("", t)
    if looks_like_html(t):
        t = html_to_text(t)[0]
    t = _URL_RE.sub(" urltoken ", t)
    t = _EMAIL_RE.sub(" emailtoken ", t)
    t = re.sub(r"\s+", " ", t.lower()).strip()
    return t[:max_chars]