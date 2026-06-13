from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Person, ProfilePerson
from app.repositories.base import SQLAlchemyRepository


class PersonRepository(SQLAlchemyRepository[Person]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Person)

    async def get_by_id(self, person_id: UUID) -> Person | None:
        result = await self.session.execute(
            select(Person).where(Person.id == person_id)
        )
        return result.scalar_one_or_none()

    async def get_by_profile(self, profile_id: UUID) -> list[Person]:
        result = await self.session.execute(
            select(Person)
            .join(ProfilePerson, ProfilePerson.person_id == Person.id)
            .where(ProfilePerson.profile_id == profile_id)
            .order_by(Person.created_at)
        )
        return list(result.scalars().all())

    async def is_in_profile(self, person_id: UUID, profile_id: UUID) -> bool:
        result = await self.session.execute(
            select(ProfilePerson).where(
                ProfilePerson.person_id == person_id,
                ProfilePerson.profile_id == profile_id,
            )
        )
        return result.scalar_one_or_none() is not None

    async def create(self, profile_id: UUID, **kwargs: object) -> Person:
        person = Person(**kwargs)
        self.session.add(person)
        await self.session.flush()

        link = ProfilePerson(profile_id=profile_id, person_id=person.id)
        self.session.add(link)
        await self.session.commit()
        await self.session.refresh(person)
        return person

    async def update(self, person: Person, **kwargs: object) -> Person:
        for key, value in kwargs.items():
            setattr(person, key, value)
        await self.session.commit()
        await self.session.refresh(person)
        return person

    async def delete(self, person: Person) -> None:
        await self.session.delete(person)
        await self.session.commit()
