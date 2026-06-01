from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.archive_request import ArchiveRequest, ArchiveRequestStatusHistory
from app.models.enums import ArchiveRequestStatus
from app.repositories.base import SQLAlchemyRepository


class ArchiveRequestRepository(SQLAlchemyRepository[ArchiveRequest]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ArchiveRequest)

    async def get_by_id(self, request_id: UUID) -> ArchiveRequest | None:
        result = await self.session.execute(
            select(ArchiveRequest).where(ArchiveRequest.id == request_id)
        )
        return result.scalar_one_or_none()

    async def get_by_profile(self, profile_id: UUID) -> list[ArchiveRequest]:
        result = await self.session.execute(
            select(ArchiveRequest)
            .where(ArchiveRequest.profile_id == profile_id)
            .order_by(ArchiveRequest.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_user(self, user_id: UUID) -> list[ArchiveRequest]:
        result = await self.session.execute(
            select(ArchiveRequest)
            .where(ArchiveRequest.created_by_user_id == user_id)
            .order_by(ArchiveRequest.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, **kwargs: object) -> ArchiveRequest:
        req = ArchiveRequest(**kwargs)
        self.session.add(req)
        await self.session.flush()
        await self._record_status_history(req.id, None, req.current_status, None, None)
        await self.session.commit()
        await self.session.refresh(req)
        return req

    async def change_status(
        self,
        req: ArchiveRequest,
        new_status: ArchiveRequestStatus,
        changed_by_user_id: UUID,
        comment: str | None = None,
    ) -> ArchiveRequest:
        old_status = req.current_status
        req.current_status = new_status
        await self.session.flush()
        await self._record_status_history(req.id, old_status, new_status, changed_by_user_id, comment)
        await self.session.commit()
        await self.session.refresh(req)
        return req

    async def update(self, req: ArchiveRequest, **kwargs: object) -> ArchiveRequest:
        for key, value in kwargs.items():
            setattr(req, key, value)
        await self.session.commit()
        await self.session.refresh(req)
        return req

    async def get_status_history(self, request_id: UUID) -> list[ArchiveRequestStatusHistory]:
        result = await self.session.execute(
            select(ArchiveRequestStatusHistory)
            .where(ArchiveRequestStatusHistory.archive_request_id == request_id)
            .order_by(ArchiveRequestStatusHistory.created_at)
        )
        return list(result.scalars().all())

    async def _record_status_history(
        self,
        request_id: UUID,
        from_status: ArchiveRequestStatus | None,
        to_status: ArchiveRequestStatus,
        changed_by_user_id: UUID | None,
        comment: str | None,
    ) -> None:
        entry = ArchiveRequestStatusHistory(
            archive_request_id=request_id,
            from_status=from_status,
            to_status=to_status,
            changed_by_user_id=changed_by_user_id,
            comment=comment,
        )
        self.session.add(entry)
