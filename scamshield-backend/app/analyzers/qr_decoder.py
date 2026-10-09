"""Local QR decoding with OpenCV's QRCodeDetector. No network access, no side effects."""
from __future__ import annotations

import io
from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image

from ..errors.exceptions import QRDecodeError, ValidationAppError

MAX_PAYLOAD_CHARS = 4096
_MAX_SIDE = 1600


@dataclass(frozen=True)
class QRDecodeResult:
    payload: str
    codes_found: int
    truncated: bool


def _load_bgr(data: bytes) -> np.ndarray:
    try:
        with Image.open(io.BytesIO(data)) as img:
            rgba = img.convert("RGBA")
            background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
            background.alpha_composite(rgba)
            rgb = np.asarray(background.convert("RGB"))
    except Exception:
        raise ValidationAppError("The file is not a valid image.", code="INVALID_IMAGE") from None
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    height, width = bgr.shape[:2]
    longest = max(height, width)
    if longest > _MAX_SIDE:
        scale = _MAX_SIDE / longest
        bgr = cv2.resize(bgr, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_AREA)
    return bgr


def _variants(bgr: np.ndarray):
    yield bgr
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    yield gray
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    yield otsu
    yield cv2.bitwise_not(gray)
    if max(gray.shape[:2]) < 500:
        yield cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)


def _detect(image: np.ndarray) -> list[str]:
    detector = cv2.QRCodeDetector()
    try:
        ok, decoded, _points, _ = detector.detectAndDecodeMulti(image)
        if ok:
            texts = [t for t in decoded if t]
            if texts:
                return texts
    except (cv2.error, AttributeError, ValueError):
        pass
    try:
        text, _points, _ = detector.detectAndDecode(image)
        if text:
            return [text]
    except cv2.error:
        pass
    return []


def decode_qr_image(data: bytes) -> QRDecodeResult:
    bgr = _load_bgr(data)
    for variant in _variants(bgr):
        texts = _detect(variant)
        if texts:
            payload = texts[0].replace("\x00", "")
            truncated = len(payload) > MAX_PAYLOAD_CHARS
            return QRDecodeResult(payload[:MAX_PAYLOAD_CHARS], len(texts), truncated)
    raise QRDecodeError()
