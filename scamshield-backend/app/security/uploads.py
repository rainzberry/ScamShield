"""Safe image-upload validation.

Uploads are validated and processed ENTIRELY IN MEMORY - nothing is written to disk,
so there is no temp file to clean up and no path to traverse. The client-supplied
filename is reduced with secure_filename() and kept only as display metadata.
"""
from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import PurePosixPath

from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename

from ..errors.exceptions import FileTooLargeError, UnsupportedMediaError, ValidationAppError

ALLOWED_FORMATS = {"PNG", "JPEG", "WEBP", "BMP", "GIF"}


@dataclass(frozen=True)
class ValidatedImage:
    data: bytes
    image_format: str
    width: int
    height: int
    safe_filename: str


def validate_image_upload(file_storage, *, max_bytes: int, allowed_extensions,
                          allowed_mime_types, max_pixels: int) -> ValidatedImage:
    if file_storage is None or not getattr(file_storage, "filename", ""):
        raise ValidationAppError(
            "No image uploaded. Send multipart/form-data with an image in the 'file' field.")

    safe_name = secure_filename(file_storage.filename) or "upload"
    extension = PurePosixPath(safe_name).suffix.lower()
    if extension not in allowed_extensions:
        raise UnsupportedMediaError(
            f"Unsupported file extension. Allowed: {', '.join(allowed_extensions)}.")

    mime = (file_storage.mimetype or "").lower()
    if mime not in allowed_mime_types:
        raise UnsupportedMediaError(
            f"Unsupported content type. Allowed: {', '.join(allowed_mime_types)}.")

    data = file_storage.stream.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise FileTooLargeError(
            f"Image exceeds the maximum upload size of {max_bytes // 1024} KB.")
    if not data:
        raise ValidationAppError("The uploaded file is empty.")

    Image.MAX_IMAGE_PIXELS = max_pixels  # Pillow decompression-bomb guard
    try:
        with Image.open(io.BytesIO(data)) as img:
            image_format = img.format
            width, height = img.size
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError,
            Image.DecompressionBombError):
        raise ValidationAppError(
            "The file is not a valid image.", code="INVALID_IMAGE") from None

    if image_format not in ALLOWED_FORMATS:
        raise UnsupportedMediaError("Unsupported image format.")
    if width * height > max_pixels:
        raise ValidationAppError("Image dimensions are too large.", code="IMAGE_TOO_LARGE")

    return ValidatedImage(data=data, image_format=image_format, width=width,
                          height=height, safe_filename=safe_name)
