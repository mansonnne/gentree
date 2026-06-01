from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Profile
from app.repositories.base import SQLAlchemyRepository


class ProfileRepository(SQLAlchemyRepository[Profile]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Profile)

    async def get_by_id(self, profile_id: UUID) -> Profile | None:
        result = await self.session.execute(
            select(Profile).where(Profile.id == profile_id)
        )
        return result.scalar_one_or_none()

    async def get_by_owner(self, owner_user_id: UUID) -> list[Profile]:
        result = await self.session.execute(
            select(Profile)
            .where(Profile.owner_user_id == owner_user_id)
            .order_by(Profile.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, owner_user_id: UUID, **kwargs: object) -> Profile:
        profile = Profile(owner_user_id=owner_user_id, **kwargs)
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def update(self, profile: Profile, **kwargs: object) -> Profile:
        for key, value in kwargs.items():
            setattr(profile, key, value)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile
