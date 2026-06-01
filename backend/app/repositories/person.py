from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.profile import Person, PersonName
from app.repositories.base import SQLAlchemyRepository


class PersonRepository(SQLAlchemyRepository[Person]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Person)

    async def get_by_id(self, person_id: UUID) -> Person | None:
        result = await self.session.execute(
            select(Person)
            .options(selectinload(Person.names))
            .where(Person.id == person_id)
        )
        return result.scalar_one_or_none()

    async def get_by_profile(self, profile_id: UUID) -> list[Person]:
        result = await self.session.execute(
            select(Person)
            .options(selectinload(Person.names))
            .where(Person.profile_id == profile_id)
            .order_by(Person.created_at)
        )
        return list(result.scalars().all())

    async def create(self, profile_id: UUID, primary_name: dict, **kwargs: object) -> Person:
        person = Person(profile_id=profile_id, **kwargs)
        self.session.add(person)
        await self.session.flush()  # get person.id before adding name

        name = PersonName(
            person_id=person.id,
            name_type="PRIMARY",
            is_primary=True,
            **primary_name,
        )
        self.session.add(name)
        await self.session.commit()
        await self.session.refresh(person)

        result = await self.session.execute(
            select(Person).options(selectinload(Person.names)).where(Person.id == person.id)
        )
        return result.scalar_one()

    async def update(self, person: Person, **kwargs: object) -> Person:
        for key, value in kwargs.items():
            setattr(person, key, value)
        await self.session.commit()

        result = await self.session.execute(
            select(Person).options(selectinload(Person.names)).where(Person.id == person.id)
        )
        return result.scalar_one()

    async def delete(self, person: Person) -> None:
        await self.session.delete(person)
        await self.session.commit()
