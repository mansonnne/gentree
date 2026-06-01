from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.archive_request import ArchiveRequest
from app.models.enums import ArchiveRequestStatus, NotificationType, UserRole
from app.models.user import User
from app.modules.archive_requests.schemas import (
    ArchiveRequestCreate,
    ArchiveRequestUpdate,
    StatusChangeRequest,
)
from app.repositories.archive_request import ArchiveRequestRepository
from app.repositories.profile import ProfileRepository

# allowed status transitions
_TRANSITIONS: dict[ArchiveRequestStatus, set[ArchiveRequestStatus]] = {
    ArchiveRequestStatus.DRAFT: {ArchiveRequestStatus.PREPARED, ArchiveRequestStatus.CANCELLED},
    ArchiveRequestStatus.PREPARED: {ArchiveRequestStatus.SENT, ArchiveRequestStatus.CANCELLED},
    ArchiveRequestStatus.SENT: {ArchiveRequestStatus.IN_PROGRESS, ArchiveRequestStatus.CANCELLED},
    ArchiveRequestStatus.IN_PROGRESS: {
        ArchiveRequestStatus.RESPONSE_RECEIVED,
        ArchiveRequestStatus.CANCELLED,
    },
    ArchiveRequestStatus.RESPONSE_RECEIVED: {ArchiveRequestStatus.COMPLETED},
    ArchiveRequestStatus.COMPLETED: set(),
    ArchiveRequestStatus.CANCELLED: set(),
}


class ArchiveRequestService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = ArchiveRequestRepository(db)
        self.profile_repo = ProfileRepository(db)
        self.db = db

    async def _get_profile_owner(self, profile_id: UUID) -> UUID:
        profile = await self.profile_repo.get_by_id(profile_id)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
        return profile.owner_user_id

    async def _get_request_with_access(
        self, request_id: UUID, user: User
    ) -> ArchiveRequest:
        req = await self.repo.get_by_id(request_id)
        if not req:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Archive request not found"
            )
        if user.role == UserRole.ADMIN:
            return req
        if user.role == UserRole.GENEALOGIST:
            if req.assigned_genealogist_user_id != user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
            return req
        if req.created_by_user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return req

    async def create(
        self, profile_id: UUID, data: ArchiveRequestCreate, user: User
    ) -> ArchiveRequest:
        owner_id = await self._get_profile_owner(profile_id)
        if user.role == UserRole.USER and owner_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return await self.repo.create(
            profile_id=profile_id,
            created_by_user_id=user.id,
            current_status=ArchiveRequestStatus.DRAFT,
            **data.model_dump(),
        )

    async def get_by_id(self, request_id: UUID, user: User) -> ArchiveRequest:
        return await self._get_request_with_access(request_id, user)

    async def list_by_profile(self, profile_id: UUID, user: User) -> list[ArchiveRequest]:
        await self._get_profile_owner(profile_id)  # check profile exists
        if user.role == UserRole.ADMIN:
            return await self.repo.get_by_profile(profile_id)
        return [
            r for r in await self.repo.get_by_profile(profile_id)
            if r.created_by_user_id == user.id
            or r.assigned_genealogist_user_id == user.id
        ]

    async def update(
        self, request_id: UUID, data: ArchiveRequestUpdate, user: User
    ) -> ArchiveRequest:
        req = await self._get_request_with_access(request_id, user)
        updates = data.model_dump(exclude_none=True)
        if not updates:
            return req
        return await self.repo.update(req, **updates)

    async def change_status(
        self, request_id: UUID, body: StatusChangeRequest, user: User
    ) -> tuple[ArchiveRequest, bool]:
        """Returns (updated_request, notify_owner)."""
        req = await self._get_request_with_access(request_id, user)
        allowed = _TRANSITIONS.get(req.current_status, set())
        if body.new_status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Cannot transition from {req.current_status} to {body.new_status}",
            )
        updated = await self.repo.change_status(
            req, body.new_status, user.id, body.comment
        )
        notify_owner = user.id != req.created_by_user_id
        return updated, notify_owner

    async def assign(self, request_id: UUID, genealogist_id: UUID, user: User) -> ArchiveRequest:
        if user.role not in (UserRole.ADMIN,):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
        req = await self.repo.get_by_id(request_id)
        if not req:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Archive request not found"
            )
        return await self.repo.update(req, assigned_genealogist_user_id=genealogist_id)

    async def get_history(self, request_id: UUID, user: User):
        await self._get_request_with_access(request_id, user)
        return await self.repo.get_status_history(request_id)
