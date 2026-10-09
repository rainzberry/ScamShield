"""Pure helpers (no Flask) shared by unit and API tests."""
from __future__ import annotations

import io


def make_qr_png(text: str, scale: int = 8, border: int = 4) -> bytes:
    """Render `text` as a QR PNG using the `qrcode` package, else OpenCV's encoder."""
    try:
        import qrcode

        qr = qrcode.QRCode(border=border, box_size=scale)
        qr.add_data(text)
        qr.make(fit=True)
        buf = io.BytesIO()
        qr.make_image(fill_color="black", back_color="white").convert("RGB").save(buf, format="PNG")
        return buf.getvalue()
    except ImportError:
        pass
    import cv2
    import numpy as np

    if not hasattr(cv2, "QRCodeEncoder"):
        import pytest
        pytest.skip("Install dev requirements (qrcode) to generate QR test images.")
    matrix = cv2.QRCodeEncoder.create().encode(text)
    matrix = np.pad(matrix, border, constant_values=255)
    matrix = cv2.resize(matrix, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
    ok, encoded = cv2.imencode(".png", matrix)
    return encoded.tobytes()


def blank_png(size: int = 200) -> bytes:
    from PIL import Image

    buf = io.BytesIO()
    Image.new("RGB", (size, size), "white").save(buf, format="PNG")
    return buf.getvalue()
