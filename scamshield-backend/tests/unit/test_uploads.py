"""Upload validation unit tests (no Flask app needed)."""
import io

import pytest
from werkzeug.datastructures import FileStorage

from app.errors.exceptions import FileTooLargeError, UnsupportedMediaError, ValidationAppError
from app.security.uploads import validate_image_upload
from tests.helpers import blank_png

KW = dict(max_bytes=100_000, allowed_extensions=(".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"),
          allowed_mime_types=("image/png", "image/jpeg", "image/webp", "image/bmp", "image/gif"),
          max_pixels=1_000_000)


def _f(data, name="a.png", mime="image/png"):
    return FileStorage(stream=io.BytesIO(data), filename=name, content_type=mime)


def test_valid_png_accepted():
    img = validate_image_upload(_f(blank_png()), **KW)
    assert img.image_format == "PNG" and img.width == img.height == 200


def test_rejections():
    cases = [
        (None, ValidationAppError), (_f(b"x", name=""), ValidationAppError),
        (_f(blank_png(), name="a.exe"), UnsupportedMediaError),
        (_f(blank_png(), mime="text/html"), UnsupportedMediaError),
        (_f(b"0" * 100_001), FileTooLargeError),
        (_f(b""), ValidationAppError), (_f(b"not an image"), ValidationAppError),
        (_f(blank_png(2000)), ValidationAppError),            # 4M pixels > max_pixels
    ]
    for storage, exc in cases:
        with pytest.raises(exc):
            validate_image_upload(storage, **KW)


def test_filename_is_sanitised():
    img = validate_image_upload(_f(blank_png(), name="../../etc/passwd.png"), **KW)
    assert "/" not in img.safe_filename and ".." not in img.safe_filename
