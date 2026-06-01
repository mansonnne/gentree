from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import NotificationType


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    notification_type: NotificationType
    title: str
    body: str
    related_archive_request_id: UUID | None
    read_at: datetime | None
    created_at: datetime


class UnreadCountRead(BaseModel):
    count: int
