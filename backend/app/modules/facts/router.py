from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.modules.auth.dependencies import get_current_user
from app.modules.facts.schemas import FactCreate, FactRead, FactUpdate
from app.modules.facts.service import FactService

router = APIRouter(tags=["facts"])


@router.post(
    "/persons/{person_id}/facts",
    response_model=FactRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_fact(
    person_id: UUID,
    data: FactCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> FactRead:
    fact = await FactService(db).create(person_id, data, current_user)
    return FactRead.model_validate(fact)


@router.get("/persons/{person_id}/facts", response_model=list[FactRead])
async def list_facts(
    person_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> list[FactRead]:
    facts = await FactService(db).list_by_person(person_id, current_user)
    return [FactRead.model_validate(f) for f in facts]


@router.patch("/facts/{fact_id}", response_model=FactRead)
async def update_fact(
    fact_id: UUID,
    data: FactUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> FactRead:
    fact = await FactService(db).update(fact_id, data, current_user)
    return FactRead.model_validate(fact)


@router.delete("/facts/{fact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fact(
    fact_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> None:
    await FactService(db).delete(fact_id, current_user)
