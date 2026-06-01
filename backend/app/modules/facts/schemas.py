from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import FactConfidence, FactType


class FactCreate(BaseModel):
    fact_type: FactType
    fact_date: date | None = None
    place: str | None = None
    value_text: str | None = None
    notes: str | None = None
    confidence: FactConfidence = FactConfidence.UNVERIFIED


class FactUpdate(BaseModel):
    fact_date: date | None = None
    place: str | None = None
    value_text: str | None = None
    notes: str | None = None
    confidence: FactConfidence | None = None


class FactRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    person_id: UUID
    fact_type: FactType
    fact_date: date | None
    place: str | None
    value_text: str | None
    notes: str | None
    confidence: FactConfidence
    verified_by_user_id: UUID | None
    verified_at: datetime | None
    created_at: datetime
    updated_at: datetime
