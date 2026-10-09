from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

from ..utils.urls import normalize_url


class AttachmentMeta(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content_type: Optional[str] = Field(default=None, max_length=127)
    size: Optional[int] = Field(default=None, ge=0, le=10**10)


class EmailAnalyzeSchema(BaseModel):
    sender: str = Field(default="", max_length=320)
    subject: str = Field(default="", max_length=998)
    body: str = Field(min_length=1, max_length=100_000)
    url: Optional[str] = Field(default=None, max_length=2048)
    attachments: List[AttachmentMeta] = Field(default_factory=list, max_length=20)
    source: Literal["manual", "gmail_demo"] = "manual"

    @field_validator("sender", "subject", mode="before")
    @classmethod
    def _strip(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("body")
    @classmethod
    def _body_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Body must not be blank.")
        return value

    @field_validator("url", mode="before")
    @classmethod
    def _url_ok(cls, value):
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        if not isinstance(value, str):
            raise ValueError("URL must be a string.")
        return normalize_url(value)


class TextAnalyzeSchema(BaseModel):
    text: str = Field(min_length=1, max_length=50_000)

    @field_validator("text")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Text must not be blank.")
        return value


class UrlAnalyzeSchema(BaseModel):
    url: str = Field(min_length=1, max_length=2048)

    @field_validator("url")
    @classmethod
    def _valid(cls, value: str) -> str:
        return normalize_url(value)
