from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from ..security.passwords import password_problems


class RegisterSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: Optional[str] = Field(default=None, max_length=80)

    @field_validator("password")
    @classmethod
    def _strong_enough(cls, value: str) -> str:
        problems = password_problems(value)
        if problems:
            raise ValueError("Password must have " + ", ".join(problems) + ".")
        return value

    @field_validator("display_name", mode="before")
    @classmethod
    def _strip_name(cls, value):
        return value.strip() or None if isinstance(value, str) else value


class LoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)
