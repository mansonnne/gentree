from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.enums import ProfileStatus


class ProfileCreate(BaseModel):
    title: str
    description: str | None = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()


class ProfileUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: ProfileStatus | None = None


class ProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_user_id: UUID
    title: str
    description: str | None
    status: ProfileStatus
    started_at: date | None
    completed_at: date | None
    created_at: datetime
    updated_at: datetime
