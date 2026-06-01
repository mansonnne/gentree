from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fact import Fact
from app.repositories.base import SQLAlchemyRepository


class FactRepository(SQLAlchemyRepository[Fact]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Fact)

    async def get_by_id(self, fact_id: UUID) -> Fact | None:
        result = await self.session.execute(select(Fact).where(Fact.id == fact_id))
        return result.scalar_one_or_none()

    async def get_by_person(self, person_id: UUID) -> list[Fact]:
        result = await self.session.execute(
            select(Fact)
            .where(Fact.person_id == person_id)
            .order_by(Fact.fact_date.nulls_last(), Fact.created_at)
        )
        return list(result.scalars().all())

    async def create(self, **kwargs: object) -> Fact:
        fact = Fact(**kwargs)
        self.session.add(fact)
        await self.session.commit()
        await self.session.refresh(fact)
        return fact

    async def update(self, fact: Fact, **kwargs: object) -> Fact:
        for key, value in kwargs.items():
            setattr(fact, key, value)
        await self.session.commit()
        await self.session.refresh(fact)
        return fact

    async def delete(self, fact: Fact) -> None:
        await self.session.delete(fact)
        await self.session.commit()
