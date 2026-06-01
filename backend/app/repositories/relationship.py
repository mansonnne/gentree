from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Relationship
from app.models.enums import RelationshipType
from app.repositories.base import SQLAlchemyRepository


class RelationshipRepository(SQLAlchemyRepository[Relationship]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Relationship)

    async def get_by_id(self, relationship_id: UUID) -> Relationship | None:
        result = await self.session.execute(
            select(Relationship).where(Relationship.id == relationship_id)
        )
        return result.scalar_one_or_none()

    async def get_by_profile(self, profile_id: UUID) -> list[Relationship]:
        result = await self.session.execute(
            select(Relationship)
            .where(Relationship.profile_id == profile_id)
            .order_by(Relationship.created_at)
        )
        return list(result.scalars().all())

    async def exists(
        self,
        profile_id: UUID,
        source_person_id: UUID,
        target_person_id: UUID,
        relationship_type: RelationshipType,
    ) -> bool:
        result = await self.session.execute(
            select(Relationship.id).where(
                Relationship.profile_id == profile_id,
                Relationship.source_person_id == source_person_id,
                Relationship.target_person_id == target_person_id,
                Relationship.relationship_type == relationship_type,
            )
        )
        return result.scalar_one_or_none() is not None

    async def create(self, **kwargs: object) -> Relationship:
        rel = Relationship(**kwargs)
        self.session.add(rel)
        await self.session.commit()
        await self.session.refresh(rel)
        return rel

    async def update(self, rel: Relationship, **kwargs: object) -> Relationship:
        for key, value in kwargs.items():
            setattr(rel, key, value)
        await self.session.commit()
        await self.session.refresh(rel)
        return rel

    async def delete(self, rel: Relationship) -> None:
        await self.session.delete(rel)
        await self.session.commit()
