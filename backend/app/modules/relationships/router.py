from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.modules.auth.dependencies import get_current_user
from app.modules.relationships.schemas import (
    RelationshipCreate,
    RelationshipRead,
    RelationshipUpdate,
    TreeResponse,
)
from app.modules.relationships.service import RelationshipService

router = APIRouter(tags=["relationships"])


@router.post(
    "/profiles/{profile_id}/relationships",
    response_model=RelationshipRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_relationship(
    profile_id: UUID,
    data: RelationshipCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> RelationshipRead:
    rel = await RelationshipService(db).create(profile_id, data, current_user)
    return RelationshipRead.model_validate(rel)


@router.get("/profiles/{profile_id}/relationships", response_model=list[RelationshipRead])
async def list_relationships(
    profile_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> list[RelationshipRead]:
    rels = await RelationshipService(db).list_by_profile(profile_id, current_user)
    return [RelationshipRead.model_validate(r) for r in rels]


@router.get("/profiles/{profile_id}/tree", response_model=TreeResponse)
async def get_tree(
    profile_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> TreeResponse:
    return await RelationshipService(db).get_tree(profile_id, current_user)


@router.patch("/relationships/{relationship_id}", response_model=RelationshipRead)
async def update_relationship(
    relationship_id: UUID,
    data: RelationshipUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> RelationshipRead:
    rel = await RelationshipService(db).update(relationship_id, data, current_user)
    return RelationshipRead.model_validate(rel)


@router.delete("/relationships/{relationship_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_relationship(
    relationship_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> None:
    await RelationshipService(db).delete(relationship_id, current_user)
