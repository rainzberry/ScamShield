from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class ScanListQuery(BaseModel):
    page: int = Field(default=1, ge=1, le=100_000)
    per_page: int = Field(default=20, ge=1, le=100)
    classification: Optional[Literal["safe", "spam", "phishing", "malicious"]] = None
    scan_type: Optional[Literal["email", "text", "url", "qr"]] = None
    sort: Literal["created_at", "risk_score"] = "created_at"
    order: Literal["asc", "desc"] = "desc"
    q: Optional[str] = Field(default=None, max_length=100)

    @field_validator("classification", "scan_type", mode="before")
    @classmethod
    def _all_means_none(cls, value):
        return None if isinstance(value, str) and value.lower() in ("all", "") else value


class ReportQuery(BaseModel):
    format: Literal["json", "pdf"] = "json"
