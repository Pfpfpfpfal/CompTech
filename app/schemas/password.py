from typing import Any
import uuid

from pydantic import BaseModel, Field, HttpUrl

from app.utils import generator


class Password(BaseModel):
    password_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    url: HttpUrl
    login: str | None = None
    password: str
    additional_data: Any | None = None
    otp_key: str | None = None

    @property
    def otp(self) -> str | None:
        if not self.otp_key:
            return None
        return generator.otp(self.otp_key)


class PasswordUpdate(Password):
    password_id: uuid.UUID | None = Field(default=None, exclude=True)
    name: str | None = None
    url: HttpUrl | None = None
    login: str | None = None
    password: str | None = None


class PasswordList(BaseModel):
    passwords: list[Password] = Field(default_factory=list)
