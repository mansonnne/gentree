from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import UserRole, UserStatus


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    role: UserRole
    status: UserStatus
    first_name: str | None
    last_name: str | None
    middle_name: str | None
    created_at: datetime
    updated_at: datetime
