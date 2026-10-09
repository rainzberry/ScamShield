from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class SettingsUpdateSchema(BaseModel):
    display_name: Optional[str] = Field(default=None, max_length=80)
    theme: Optional[Literal["light", "dark", "system"]] = None
    email_notifications: Optional[bool] = None
