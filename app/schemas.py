from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Literal

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

ApplicationStatus = Literal["saved", "applied", "interview", "offer", "rejected"]


class ApplicationCreate(BaseModel):
    company: str = Field(min_length=1, max_length=120)
    position: str = Field(min_length=1, max_length=120)
    url: str | None = Field(default=None, max_length=500)
    status: ApplicationStatus = "saved"
    notes: str | None = None


class ApplicationUpdate(BaseModel):
    company: str | None = Field(default=None, min_length=1, max_length=120)
    position: str | None = Field(default=None, min_length=1, max_length=120)
    url: str | None = Field(default=None, max_length=500)
    status: ApplicationStatus | None = None
    notes: str | None = None


class ApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company: str
    position: str
    url: str | None
    status: ApplicationStatus
    notes: str | None
    created_at: datetime