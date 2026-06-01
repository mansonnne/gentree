from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import UserRole
from app.models.profile import Person
from app.models.user import User
from app.modules.persons.schemas import PersonCreate, PersonUpdate
from app.repositories.person import PersonRepository
from app.repositories.profile import ProfileRepository


class PersonService:
    def __init__(self, db: AsyncSession) -> None:
        self.person_repo = PersonRepository(db)
        self.profile_repo = ProfileRepository(db)

    async def _assert_profile_access(self, profile_id: UUID, user: User) -> None:
        profile = await self.profile_repo.get_by_id(profile_id)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
        if user.role != UserRole.ADMIN and profile.owner_user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    async def _get_person_with_access(self, person_id: UUID, user: User) -> Person:
        person = await self.person_repo.get_by_id(person_id)
        if not person:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")
        await self._assert_profile_access(person.profile_id, user)
        return person

    async def create(self, profile_id: UUID, data: PersonCreate, user: User) -> Person:
        await self._assert_profile_access(profile_id, user)
        primary_name = data.primary_name.model_dump()
        person_data = data.model_dump(exclude={"primary_name"})
        return await self.person_repo.create(
            profile_id=profile_id,
            primary_name=primary_name,
            **person_data,
        )

    async def list_by_profile(self, profile_id: UUID, user: User) -> list[Person]:
        await self._assert_profile_access(profile_id, user)
        return await self.person_repo.get_by_profile(profile_id)

    async def get_by_id(self, person_id: UUID, user: User) -> Person:
        return await self._get_person_with_access(person_id, user)

    async def update(self, person_id: UUID, data: PersonUpdate, user: User) -> Person:
        person = await self._get_person_with_access(person_id, user)
        updates = data.model_dump(exclude_none=True)
        if not updates:
            return person
        return await self.person_repo.update(person, **updates)

    async def delete(self, person_id: UUID, user: User) -> None:
        person = await self._get_person_with_access(person_id, user)
        await self.person_repo.delete(person)
